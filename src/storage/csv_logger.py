from __future__ import annotations

import csv
from pathlib import Path


def _append(path: Path, row: dict, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in fieldnames})


def append_run_row(path: Path, row: dict) -> None:
    _append(path, row, ["run_id", "start_time_utc", "start_time_us", "status", "question_count", "submitted_count"])


def append_forecast_row(path: Path, row: dict) -> None:
    _append(
        path,
        row,
        ["run_time_utc", "run_time_us", "question_id", "question_title", "question_type", "open_status", "tournament_status", "submission"],
    )
