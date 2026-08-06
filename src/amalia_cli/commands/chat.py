from amalia_cli.mode import Mode

from .registry import Command


def execute(context):
    context.mode = Mode.CHAT
    return "Conversation mode enabled."


COMMAND = Command(
    name="chat",
    description="Switch to conversation mode.",
    handler=execute,
)