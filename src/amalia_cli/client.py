import json

import httpx

from .configuration import Config


class AmaliaClient:
    def __init__(self, config: Config):
        self.config = config

    def chat(self, messages: list[dict]) -> str:
        url = f"{self.config.base_url.rstrip('/')}/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": True,
        }

        if self.config.temperature is not None:
            payload["temperature"] = self.config.temperature

        if self.config.max_completion_tokens is not None:
            payload["max_completion_tokens"] = (
                self.config.max_completion_tokens
            )

        full_response = ""

        with httpx.stream(
            "POST",
            url,
            headers=headers,
            json=payload,
            timeout=None,
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line.startswith("data: "):
                    continue

                data = line[6:]

                if data == "[DONE]":
                    break

                chunk = json.loads(data)

                content = chunk["choices"][0]["delta"].get("content")

                if content:
                    print(content, end="", flush=True)
                    full_response += content

        print()

        return full_response