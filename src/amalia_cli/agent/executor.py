from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    return_code: int


class AgentExecutor:
    def __init__(
        self,
        working_directory: Path,
    ) -> None:
        self.working_directory = working_directory

    def execute(
        self,
        code: str,
    ) -> ExecutionResult:
        """
        Real executor.
        Do not call this yet.
        """

        amalia_directory = (
            self.working_directory / ".amalia"
        )

        amalia_directory.mkdir(
            exist_ok=True,
        )

        generated_file = (
            amalia_directory / "generated.py"
        )

        code = self.clean_code(code)

        generated_file.write_text(
            code,
            encoding="utf-8",
        )

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(generated_file),
                ],
                cwd=self.working_directory,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                stdout=exc.stdout or "",
                stderr=exc.stderr or "Execution timed out.",
                return_code=124,
            )

        return ExecutionResult(
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode,
        )

    def execute_dummy(
        self,
        code: str,
    ) -> ExecutionResult:
        """
        Fake executor for testing.
        """

        amalia_directory = (
            self.working_directory / ".amalia"
        )

        amalia_directory.mkdir(
            exist_ok=True,
        )

        generated_file = (
            amalia_directory / "generated.py"
        )

        code = self.clean_code(code)

        generated_file.write_text(
            code,
            encoding="utf-8",
        )

        return ExecutionResult(
            stdout=(
                "Olá Mundo"
            ),
            stderr="",
            return_code=0,
        )

    @staticmethod
    def clean_code(code: str) -> str:
        code = code.strip()

        if code.startswith("```python"):
            code = code[len("```python"):]

        elif code.startswith("```"):
            code = code[3:]

        if code.endswith("```"):
            code = code[:-3]

        return code.strip()