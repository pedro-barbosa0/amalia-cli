from amalia_cli.mode import Mode

from .registry import Command


def execute(context):
    context.mode = Mode.AGENT
    return "Agent mode enabled."


COMMAND = Command(
    name="agent",
    description="Switch to agent mode.",
    handler=execute,
)