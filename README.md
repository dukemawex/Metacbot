# Metacbot - Metaculus Tournament Sentinel

A modular, automated sentinel for a Metaculus tournament/project (default **32916**, "Current AI Tournament").

## Secrets and safety

The bot reads configuration **only** from environment variables (GitHub Secrets in Actions):

- `METACULUS_TOKEN` (preferred)
- `METACULUS_API_KEY` (fallback alias)
- `EXA_API_KEY`
- `OPENROUTER_API_KEY`

- `TOURNAMENT_ID` (project/tournament identifier; accepts numeric ID like `32916` or slug like `spring-aib-2026`)

`TOURNAMENT_ID` should be the Metaculus project/tournament identifier from the tournament page URL (slug) or from API payload IDs (numeric).

Secrets are never hardcoded.

## File tree

```text
.github/workflows/{ci.yml,scheduler.yml}
src/
  main.py
  config/{settings.py,constants.py,timezone.py,logging.yaml}
  metaculus/{client.py,schemas.py,selection.py,windows.py,state.py}
  research/{exa_client.py,retrieval.py,source_ranker.py,evidence.py}
  llm/{openrouter_client.py,roles.py,structured.py,prompts/*.md}
  forecasting/{baselines.py,features.py,ensemble.py,validators.py,stats/*}
  execution/{runner.py,submitter.py,risk.py,dedupe.py}
  storage/{csv_logger.py,jsonl_logger.py,report.py,git_commit.py}
data/
tests/
```

## Architecture overview

Every run (30-minute schedule):

1. Load tournament/questions for `TOURNAMENT_ID` (default `32916`)
2. Determine open-window status (tournament and each question)
3. Select eligible questions
4. Retrieve evidence (Exa)
5. Run multi-role LLM pipeline (OpenRouter)
6. Compute baseline + type-aware statistical forecast
7. Ensemble + validation
8. Submit when secrets exist and the market is open
9. Log outputs to `data/runs.csv`, `data/forecasts.csv`, `data/forecasts.jsonl`, and `data/latest_summary.md`

## Open-window behavior (America/New_York)

Window checks use `America/New_York` logic with UTC+US timestamp logging. If a market is not open, the bot skips submission and logs `market closed/not open` with one of:

- `CLOSED_WINDOW`
- `LOCKED`
- `RESOLVED`
- `NOT_YET_OPEN`

If `STRICT_OPEN_WINDOW` behavior is needed, it can be added as a code change.

## Live mode

```bash
export METACULUS_TOKEN=...
export EXA_API_KEY=...
export OPENROUTER_API_KEY=...
python -m src.main
```

⚠️ The bot always runs in live mode and can submit real forecasts.

## CI and Scheduler

- `ci.yml`: `ruff` + `pytest`
- `scheduler.yml`: runs every 30 minutes (`*/30 * * * *`), uploads artifacts, and commits `data/` updates.
