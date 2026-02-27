from __future__ import annotations

import logging
from datetime import datetime

from src.config.timezone import now_utc, to_us, utc_and_us_iso
from src.execution.risk import RateLimiter
from src.execution.submitter import maybe_submit
from src.forecasting.baselines import baseline_forecast
from src.forecasting.ensemble import combine
from src.forecasting.features import extract_features
from src.forecasting.stats.binary_models import forecast_binary
from src.forecasting.stats.date_models import forecast_date
from src.forecasting.stats.multiclass_models import dirichlet_update
from src.forecasting.stats.numeric_models import forecast_numeric
from src.llm.openrouter_client import OpenRouterClient
from src.llm.roles import run_roles
from src.metaculus.client import MetaculusClient
from src.metaculus.selection import select_questions
from src.metaculus.state import StateStore
from src.metaculus.windows import is_question_open_now, is_tournament_open_now
from src.research.exa_client import ExaClient
from src.research.retrieval import retrieve_evidence
from src.storage.csv_logger import append_forecast_row, append_run_row
from src.storage.jsonl_logger import append_forecast_record
from src.storage.report import write_summary

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _stats_forecast(question: dict, features: dict) -> dict:
    qtype = question.get("type", "binary")
    if qtype == "binary":
        return forecast_binary(features)
    if qtype in {"multiple_choice", "distribution"}:
        return dirichlet_update(len(question.get("options", [])))
    if qtype == "numeric":
        return forecast_numeric()
    if qtype == "date":
        dateq = forecast_date()
        return {"p10": 0.2, "p50": 0.5, "p90": 0.8, "date_quantiles": dateq}
    return {"probability": 0.5}


def _reasoning(question: dict, evidence) -> str:
    refs = [f"[{item.idx}] {item.title} ({item.url})" for item in evidence.items[:3]]
    citation_ids = " ".join(f"[{item.idx}]" for item in evidence.items[:3]) or "[1]"
    return (
        f"Forecast for '{question.get('title')}' is based on recent evidence {citation_ids}. "
        "Key drivers were extracted from external sources with uncertainty retained.\n\n"
        "Sources:\n" + "\n".join(refs)
    )


def run_once(settings) -> int:
    ok, errors = settings.preflight()
    if not ok:
        logger.error("Preflight failed: %s", "; ".join(errors))
        return 1

    now = now_utc()
    now_us = to_us(now)
    utc_iso, us_iso = utc_and_us_iso(now)
    logger.info("Run start UTC=%s US=%s", utc_iso, us_iso)

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    state_store = StateStore(settings.data_dir / "state.json")
    state = state_store.load()

    meta_client = MetaculusClient(settings)
    exa_client = ExaClient(settings)
    llm_client = OpenRouterClient(settings)

    tournament = meta_client.tournament_meta()
    tournament_open, tournament_status = is_tournament_open_now(tournament, now_us)

    questions = meta_client.questions()
    chosen = select_questions(questions, now=now, limit=settings.max_questions)

    limiter = RateLimiter(settings.max_questions)
    records: list[dict] = []

    for question in chosen:
        q_open, q_status = is_question_open_now(question, now_us)
        can_submit = tournament_open and q_open and limiter.allow()

        evidence = retrieve_evidence(question, exa_client)
        llm_outputs = run_roles(question, evidence, llm_client)
        baseline = baseline_forecast(question)
        features = extract_features(question, evidence)
        stats = _stats_forecast(question, features)
        llm_forecast = llm_outputs.get("forecaster", {})
        final_forecast = combine(
            question,
            baseline,
            stats,
            llm_forecast,
            min_prob=settings.min_prob,
            max_prob=settings.max_prob,
        )
        reasoning = _reasoning(question, evidence)

        submission = maybe_submit(
            meta_client,
            settings,
            state,
            question,
            final_forecast,
            reasoning,
            can_submit=can_submit,
        )
        if not can_submit and submission["status"] == "SKIPPED_NOT_OPEN":
            logger.info("market closed/not open question_id=%s status=%s", question["id"], q_status)

        record = {
            "run_time_utc": utc_iso,
            "run_time_us": us_iso,
            "question_id": question.get("id"),
            "question_title": question.get("title"),
            "question_type": question.get("type", "binary"),
            "open_status": q_status,
            "tournament_status": tournament_status,
            "baseline": baseline,
            "stats": stats,
            "llm": llm_forecast,
            "final_forecast": final_forecast,
            "reasoning": reasoning,
            "submission": submission,
            "evidence": [item.__dict__ for item in evidence.items],
        }
        records.append(record)
        append_forecast_row(settings.data_dir / "forecasts.csv", record)
        append_forecast_record(settings.data_dir / "forecasts.jsonl", record)

    state_store.save(state)

    append_run_row(
        settings.data_dir / "runs.csv",
        {
            "run_id": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "start_time_utc": utc_iso,
            "start_time_us": us_iso,
            "status": "SUCCESS",
            "question_count": len(chosen),
            "submitted_count": sum(1 for r in records if r["submission"].get("submitted")),
        },
    )
    write_summary(settings.data_dir / "latest_summary.md", records, utc_iso, us_iso)

    if settings.strict_open_window and not tournament_open:
        return 2
    return 0
