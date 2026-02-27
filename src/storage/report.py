from pathlib import Path


def write_summary(path: Path, records: list[dict], utc_iso: str, us_iso: str) -> None:
    submitted = sum(1 for r in records if r["submission"].get("submitted"))
    lines = [
        "# Metacbot Latest Summary",
        "",
        f"- Run UTC: {utc_iso}",
        f"- Run America/New_York: {us_iso}",
        f"- Questions processed: {len(records)}",
        f"- Submissions made: {submitted}",
        "",
        "## Questions",
    ]
    for row in records:
        lines.append(
            f"- Q{row['question_id']}: {row['open_status']} | submission={row['submission'].get('status')}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
