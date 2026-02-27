from __future__ import annotations

import json
import time
from urllib import request

from src.config.settings import Settings


class OpenRouterClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = "openrouter/auto"

    def chat_json(self, prompt: str) -> dict:
        if not self.settings.openrouter_api_key:
            return {"summary": "Offline mode fallback", "probability": 0.5, "confidence": 0.2}

        body = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
            }
        ).encode("utf-8")
        req = request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            method="POST",
            data=body,
            headers={
                "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
        )
        for i in range(self.settings.retries):
            try:
                with request.urlopen(req, timeout=self.settings.timeout_seconds) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data["choices"][0]["message"]["content"]
                    return json.loads(content)
            except Exception:
                if i == self.settings.retries - 1:
                    raise
                time.sleep(2**i)
        return {}
