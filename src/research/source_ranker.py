def deduplicate_and_rank(rows: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for row in sorted(rows, key=lambda x: x.get("score", 0), reverse=True):
        url = row.get("url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(row)
    return out[:6]
