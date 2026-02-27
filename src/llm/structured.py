from __future__ import annotations

import json
import re


def parse_strict_json(raw: str | dict, retries: int = 2) -> dict:
    if isinstance(raw, dict):
        return raw
    candidate = raw
    for _ in range(retries + 1):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", candidate, flags=re.S)
            if not match:
                continue
            candidate = match.group(0)
    raise ValueError("Could not parse strict JSON")
