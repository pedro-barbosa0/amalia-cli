from pathlib import Path


class PromptManager:
    def __init__(self, prompts_directory: Path):
        self.prompts_directory = prompts_directory

    def list_prompts(self) -> list[str]:
        if not self.prompts_directory.exists():
            return []

        return sorted(
            path.stem
            for path in self.prompts_directory.glob("*.md")
            if path.is_file()
        )

    def get_prompt(self, name: str) -> str:
        prompt_path = self.prompts_directory / f"{name}.md"

        if not prompt_path.is_file():
            raise FileNotFoundError(
                f"Prompt '{name}' was not found."
            )

        return prompt_path.read_text(encoding="utf-8").strip()