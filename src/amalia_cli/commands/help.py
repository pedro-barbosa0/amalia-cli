from .registry import Command


def execute(context):
    print("\nAvailable commands:\n")

    for command in context.command_registry.all():
        print(f"  /{command.name:<12} {command.description}")

    print()


COMMAND = Command(
    name="help",
    description="Show available commands.",
    handler=execute,
)