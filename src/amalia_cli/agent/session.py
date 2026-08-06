from __future__ import annotations

from dataclasses import dataclass

from amalia_cli.conversation import Conversation


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    return_code: int


@dataclass
class AgentTurn:
    user_prompt: str
    generated_code: str
    execution_result: ExecutionResult | None = None


class AgentSession:
    def __init__(
        self,
        system_prompt: str,
    ) -> None:
        self.conversation = Conversation(system_prompt)
        self.turns: list[AgentTurn] = []

    def add_user_message(
        self,
        content: str,
    ) -> None:
        self.conversation.add_user_message(content)

    def add_assistant_message(
        self,
        content: str,
    ) -> None:
        self.conversation.add_assistant_message(content)

    def add_turn(
        self,
        user_prompt: str,
        generated_code: str,
        execution_result: ExecutionResult | None = None,
    ) -> None:
        self.turns.append(
            AgentTurn(
                user_prompt=user_prompt,
                generated_code=generated_code,
                execution_result=execution_result,
            )
        )

    def get_messages(
        self,
        include_execution_results: bool = True,
    ) -> list[dict]:
        messages = self.conversation.get_messages()

        if not include_execution_results:
            return messages

        if not self.turns:
            return messages

        result_messages = []

        for turn in self.turns:
            if turn.execution_result is None:
                continue

            result_messages.append(
                {
                    "role": "system",
                    "content": (
                        "Previous agent execution result:\n\n"
                        f"User request:\n{turn.user_prompt}\n\n"
                        f"Generated code:\n{turn.generated_code}\n\n"
                        "Execution result:\n"
                        f"Return code: {turn.execution_result.return_code}\n\n"
                        f"stdout:\n{turn.execution_result.stdout}\n\n"
                        f"stderr:\n{turn.execution_result.stderr}"
                    ),
                }
            )

        if not result_messages:
            return messages

        if messages and messages[-1]["role"] == "user":
            current_user_message = messages[-1]
            previous_messages = messages[:-1]

            return [
                *previous_messages,
                *result_messages,
                current_user_message,
            ]

        return [
            *messages,
            *result_messages,
        ]