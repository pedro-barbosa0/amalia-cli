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

    def save(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float | None,
        max_completion_tokens: int | None,
        default_prompt: str,
    ) -> None:
        if not api_key.strip():
            raise ValueError("API key cannot be empty.")

        if not base_url.strip():
            raise ValueError("Base URL cannot be empty.")

        if not model.strip():
            raise ValueError("Model cannot be empty.")

        if not default_prompt.strip():
            raise ValueError("Default prompt cannot be empty.")

        self.api_key = api_key.strip()
        self.base_url = base_url.strip()
        self.model = model.strip()
        self.temperature = temperature
        self.max_completion_tokens = max_completion_tokens
        self.default_prompt = default_prompt.strip()

        self._write_env()

    def _write_env(self) -> None:
        temperature = (
            str(self.temperature)
            if self.temperature is not None
            else ""
        )

        max_tokens = (
            str(self.max_completion_tokens)
            if self.max_completion_tokens is not None
            else ""
        )

        content = (
            f"API_KEY={self.api_key}\n"
            f"BASE_URL={self.base_url}\n"
            f"MODEL={self.model}\n"
            f"TEMPERATURE={temperature}\n"
            f"MAX_COMPLETION_TOKENS={max_tokens}\n"
            f"DEFAULT_PROMPT={self.default_prompt}\n"
        )

        self.env_path.write_text(
            content,
            encoding="utf-8",
        )

    # Kept for backwards compatibility with the CLI configuration
    # flow. The TUI should use save() instead.
    def setup(self) -> None:
        print("AMALIA CLI configuration")
        print()

        current_api_key = self.api_key
        current_base_url = self.base_url
        current_model = self.model
        current_temperature = self.temperature
        current_max_tokens = self.max_completion_tokens
        current_prompt = self.default_prompt

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

        parsed_temperature = None

        if temperature:
            try:
                parsed_temperature = float(temperature)
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

        parsed_max_tokens = None

        if max_tokens:
            try:
                parsed_max_tokens = int(max_tokens)
            except ValueError as exc:
                raise ValueError(
                    "Max completion tokens must be a valid integer."
                ) from exc

        default_prompt = input(
            f"Default prompt [{current_prompt}]: "
        ).strip()

        if not default_prompt:
            default_prompt = current_prompt

        self.save(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=parsed_temperature,
            max_completion_tokens=parsed_max_tokens,
            default_prompt=default_prompt,
        )

        print()
        print(f"Configuration saved to {self.env_path}")