import argparse
from pathlib import Path

from textual import app

from .client import AmaliaClient
from .commands.registry import CommandRegistry
from .configuration import Config
from .conversation import Conversation
from .prompts import PromptManager
from .tui.tui import AmaliaTUI
from .app import AmaliaAppController

class AppContext:
    def __init__(
        self,
        client: AmaliaClient,
        conversation: Conversation,
        prompt_manager: PromptManager,
        command_registry: CommandRegistry,
    ):
        self.client = client
        self.conversation = conversation
        self.prompt_manager = prompt_manager
        self.command_registry = command_registry

        self.running = True


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="amalia",
        description="CLI for interacting with the AMALIA language model.",
    )

    parser.add_argument(
        "--prompt",
        help="System prompt to use for this run.",
    )

    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List available system prompts.",
    )

    parser.add_argument(
        "--config",
        action="store_true",
        help="Configure AMALIA.",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        help="Override the default temperature for this run.",
    )

    parser.add_argument(
        "--max-completion-tokens",
        type=int,
        help="Override the default maximum completion tokens for this run.",
    )

    return parser.parse_args()


def handle_command(user_input: str, context: AppContext) -> bool:
    """
    Handle an application command.

    Returns True if the input was a command,
    False if it should be sent to AMALIA.
    """

    if not user_input.startswith("/"):
        return False

    command_input = user_input[1:].strip()

    if not command_input:
        return True

    parts = command_input.split()

    command_name = parts[0]
    arguments = parts[1:]

    command = context.command_registry.get(command_name)

    if command is None:
        print(
            f"Unknown command: /{command_name}. "
            "Use /help to see available commands."
        )
        return True

    command.handler(context, *arguments)

    return True


def main():
    args = parse_arguments()

    config = Config()

    if args.config:
        config.setup()
        return

    if not config.is_configured():
        print("No AMALIA configuration found.")
        print()

        config.setup()
        print()

    # CLI arguments override persistent configuration
    # for this specific run.
    temperature = (
        args.temperature
        if args.temperature is not None
        else config.temperature
    )

    max_completion_tokens = (
        args.max_completion_tokens
        if args.max_completion_tokens is not None
        else config.max_completion_tokens
    )

    # Apply runtime values to the configuration object used
    # by the client without modifying the persistent .env.
    config.temperature = temperature
    config.max_completion_tokens = max_completion_tokens

    project_root = Path(__file__).resolve().parents[2]
    prompts_directory = project_root / "prompts"

    prompt_manager = PromptManager(prompts_directory)

    if args.list_prompts:
        prompts = prompt_manager.list_prompts()

        if not prompts:
            print("No prompts found.")
            return

        print("Available prompts:\n")

        for prompt_name in prompts:
            print(f"  {prompt_name}")

        return

    # --prompt overrides the configured default for this run.
    # Otherwise, use DEFAULT_PROMPT from configuration.
    prompt_name = (
        args.prompt
        if args.prompt
        else config.default_prompt
    )

    system_prompt = prompt_manager.get_prompt(prompt_name)

    client = AmaliaClient(config)
    conversation = Conversation(system_prompt)
    command_registry = CommandRegistry()
    
    controller = AmaliaAppController(
        client=client,
        conversation=conversation,
        command_registry=command_registry,
    )

    context = AppContext(
        client=client,
        conversation=conversation,
        prompt_manager=prompt_manager,
        command_registry=command_registry,
    )

    app = AmaliaTUI(controller)
    app.run()


if __name__ == "__main__":
    main()