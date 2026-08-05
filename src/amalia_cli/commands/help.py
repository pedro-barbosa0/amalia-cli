from .registry import Command


def execute(context):
    lines = ["Available commands:", ""]

    for command in context.command_registry.all():
        lines.append(
            f"\n  /{command.name:<12} - {command.description}"
        )

    return "\n".join(lines)


COMMAND = Command(
    name="help",
    description="Show available commands.",
    handler=execute,
)