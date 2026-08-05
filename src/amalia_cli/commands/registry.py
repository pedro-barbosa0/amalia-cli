import importlib
import pkgutil
from dataclasses import dataclass
from typing import Callable


@dataclass
class Command:
    name: str
    description: str
    handler: Callable


class CommandRegistry:
    def __init__(self):
        self.commands: dict[str, Command] = {}
        self._discover_commands()

    def _discover_commands(self):
        package_name = "amalia_cli.commands"
        package = importlib.import_module(package_name)

        for module_info in pkgutil.iter_modules(package.__path__):
            module_name = module_info.name

            if module_name.startswith("_") or module_name == "registry":
                continue

            module = importlib.import_module(
                f"{package_name}.{module_name}"
            )

            command = getattr(module, "COMMAND", None)

            if command is None:
                continue

            self.register(command)

    def register(self, command: Command):
        if command.name in self.commands:
            raise ValueError(
                f"Duplicate command: /{command.name}"
            )

        self.commands[command.name] = command

    def get(self, name: str) -> Command | None:
        return self.commands.get(name)

    def all(self) -> list[Command]:
        return sorted(
            self.commands.values(),
            key=lambda command: command.name
        )