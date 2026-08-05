import json
from collections.abc import Iterator

import httpx

from .configuration import Config


class AmaliaClient:
    def __init__(self, config: Config):
        self.config = config

    def chat_stream(
        self,
        messages: list[dict],
    ) -> Iterator[str]:
        url = f"{self.config.base_url}/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_completion_tokens": self.config.max_completion_tokens,
            "stream": True,
        }

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
                    yield content

    def chat(
        self,
        messages: list[dict],
    ) -> str:
        full_response = ""

        for chunk in self.chat_stream(messages):
            full_response += chunk

        return full_response