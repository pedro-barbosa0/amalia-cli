import os
from getpass import getpass
from pathlib import Path

from dotenv import load_dotenv


class Config:
    def __init__(self, env_path: Path | None = None):
        self.env_path = env_path or Path(".env")

        load_dotenv(self.env_path, override=True)

        self.api_key = os.getenv("API_KEY")
        self.base_url = os.getenv("BASE_URL")
        self.model = os.getenv("MODEL")

        self.temperature = self._get_float("TEMPERATURE")
        self.max_completion_tokens = self._get_int(
            "MAX_COMPLETION_TOKENS"
        )

        self.default_prompt = os.getenv(
            "DEFAULT_PROMPT",
            "default",
        )

    @staticmethod
    def _get_float(name: str) -> float | None:
        value = os.getenv(name)

        if value is None or value.strip() == "":
            return None

        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(
                f"{name} must be a valid number."
            ) from exc

    @staticmethod
    def _get_int(name: str) -> int | None:
        value = os.getenv(name)

        if value is None or value.strip() == "":
            return None

        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(
                f"{name} must be a valid integer."
            ) from exc

    def is_configured(self) -> bool:
        return bool(
            self.api_key
            and self.base_url
            and self.model
        )

    def setup(self):
        print("AMALIA CLI configuration")
        print()

        current_api_key = self.api_key
        current_base_url = self.base_url
        current_model = self.model
        current_temperature = self.temperature
        current_max_tokens = self.max_completion_tokens
        current_default_prompt = self.default_prompt

        if current_api_key:
            api_key = getpass(
                "API key [press Enter to keep current]: "
            )

            if not api_key:
                api_key = current_api_key
        else:
            api_key = getpass("API key: ")

        base_url = input(
            f"Base URL [{current_base_url or 'http://127.0.0.1:8001'}]: "
        ).strip()

        if not base_url:
            base_url = current_base_url or "http://127.0.0.1:8001"

        model = input(
            f"Model [{current_model or 'amalia-9b-0626-dpo'}]: "
        ).strip()

        if not model:
            model = current_model or "amalia-9b-0626-dpo"

        temperature = input(
            "Default temperature "
            f"[{current_temperature if current_temperature is not None else 'server default'}]: "
        ).strip()

        if not temperature:
            temperature = (
                str(current_temperature)
                if current_temperature is not None
                else ""
            )

        if temperature:
            try:
                float(temperature)
            except ValueError as exc:
                raise ValueError(
                    "Temperature must be a valid number."
                ) from exc

        max_tokens = input(
            "Default max completion tokens "
            f"[{current_max_tokens if current_max_tokens is not None else 'server default'}]: "
        ).strip()

        if not max_tokens:
            max_tokens = (
                str(current_max_tokens)
                if current_max_tokens is not None
                else ""
            )

        if max_tokens:
            try:
                int(max_tokens)
            except ValueError as exc:
                raise ValueError(
                    "Max completion tokens must be a valid integer."
                ) from exc

        default_prompt = input(
            f"Default system prompt [{current_default_prompt}]: "
        ).strip()

        if not default_prompt:
            default_prompt = current_default_prompt

        self._write_env(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            default_prompt=default_prompt,
        )

        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = float(temperature) if temperature else None
        self.max_completion_tokens = (
            int(max_tokens) if max_tokens else None
        )
        self.default_prompt = default_prompt

        print()
        print(f"Configuration saved to {self.env_path}")

    def _write_env(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: str,
        max_completion_tokens: str,
        default_prompt: str,
    ):
        content = (
            f"API_KEY={api_key}\n"
            f"BASE_URL={base_url}\n"
            f"MODEL={model}\n"
            f"TEMPERATURE={temperature}\n"
            f"MAX_COMPLETION_TOKENS={max_completion_tokens}\n"
            f"DEFAULT_PROMPT={default_prompt}\n"
        )

        self.env_path.write_text(
            content,
            encoding="utf-8",
        )