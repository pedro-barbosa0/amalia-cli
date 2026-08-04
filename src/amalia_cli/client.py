import json

import httpx

from .configuration import Config


class AmaliaClient:
    def __init__(self, config: Config):
        self.base_url = config.base_url.rstrip("/")
        self.api_key = config.api_key
        self.model = config.model

    def chat(self, messages: list[dict]) -> str:
        url = f"{self.base_url}/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "stream": True,
        }

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