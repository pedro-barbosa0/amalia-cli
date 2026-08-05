from collections.abc import Iterator

from .client import AmaliaClient
from .conversation import Conversation
from .commands.registry import CommandRegistry


class AmaliaAppController:
    def __init__(
        self,
        client: AmaliaClient,
        conversation: Conversation,
        command_registry: CommandRegistry,
    ):
        self.client = client
        self.conversation = conversation
        self.command_registry = command_registry

        self.running = True

    def handle_command(self, user_input: str) -> str | None:
        """
        Handle an application command.

        Returns:
            A message to display in the TUI if the input was a command.
            None if the input should be sent to AMALIA.
        """

        if not user_input.startswith("/"):
            return None

        command_input = user_input[1:].strip()

        if not command_input:
            return ""

        parts = command_input.split()

        command_name = parts[0]
        arguments = parts[1:]

        command = self.command_registry.get(command_name)

        if command is None:
            return (
                f"Unknown command: /{command_name}. "
                "Use /help to see available commands."
            )

        result = command.handler(self, *arguments)

        if result is None:
            return ""

        return str(result)

    def send_message(
        self,
        message: str,
    ) -> Iterator[str]:
        self.conversation.add_user_message(message)

        full_response = ""

        for chunk in self.client.chat_stream(
            self.conversation.get_messages()
        ):
            full_response += chunk
            yield chunk

        self.conversation.add_assistant_message(
            full_response
        )