from .registry import Command


def execute(context):
    context.running = False


COMMAND = Command(
    name="exit",
    description="Exit AMALIA CLI.",
    handler=execute,
)