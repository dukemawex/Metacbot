from __future__ import annotations

import json
import time
from urllib import request

from src.config.settings import Settings


class ExaClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def search(self, query: str) -> list[dict]:
        if not self.settings.exa_api_key:
            fixture = self.settings.fixtures_dir / "exa_results.json"
            data = json.loads(fixture.read_text(encoding="utf-8"))
            return data.get("results", [])

        body = json.dumps({"query": query, "numResults": 5, "type": "neural"}).encode("utf-8")
        req = request.Request(
            "https://api.exa.ai/search",
            method="POST",
            data=body,
            headers={
                "x-api-key": self.settings.exa_api_key,
                "Content-Type": "application/json",
            },
        )
        for i in range(self.settings.retries):
            try:
                with request.urlopen(req, timeout=self.settings.timeout_seconds) as resp:
                    return json.loads(resp.read().decode("utf-8")).get("results", [])
            except Exception:
                if i == self.settings.retries - 1:
                    raise
                time.sleep(2**i)
        return []
