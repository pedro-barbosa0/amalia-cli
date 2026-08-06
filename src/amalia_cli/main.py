import argparse
from pathlib import Path

from .app import AmaliaAppController
from .client import AmaliaClient
from .commands.registry import CommandRegistry
from .configuration import Config
from .conversation import Conversation
from .prompts import PromptManager
from .tui.tui import AmaliaTUI
from .agent.session import AgentSession
from .agent.executor import AgentExecutor

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


def main():
    args = parse_arguments()

    config = Config()

    project_root = Path(__file__).resolve().parents[2]
    prompts_directory = project_root / "prompts"

    prompt_manager = PromptManager(prompts_directory)

    # --list-prompts does not require AMALIA configuration.
    if args.list_prompts:
        prompts = prompt_manager.list_prompts()

        if not prompts:
            print("No prompts found.")
            return

        print("Available prompts:\n")

        for prompt_name in prompts:
            print(f"  {prompt_name}")

        return

    # Explicit --config remains available as a CLI fallback.
    if args.config:
        config.setup()
        return

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

    config.temperature = temperature
    config.max_completion_tokens = max_completion_tokens

    # If configuration doesn't exist yet, the TUI will open
    # the first-run configuration screen.
    if config.is_configured():
        prompt_name = (
            args.prompt
            if args.prompt
            else config.default_prompt
        )

        system_prompt = prompt_manager.get_prompt(prompt_name)

        client = AmaliaClient(config)

        chat_conversation = Conversation(system_prompt)
        agent_session = AgentSession(prompt_manager.get_prompt("coding"))
        command_registry = CommandRegistry()
        agent_executor = AgentExecutor(working_directory=project_root,)
        controller = AmaliaAppController(
            client=client,
            chat_conversation=chat_conversation,
            agent_session=agent_session,
            agent_executor=agent_executor,
            command_registry=command_registry,
            config=config,
        )

        tui = AmaliaTUI(
            controller=controller,
            config=config,
            prompt_manager=prompt_manager,
        )

    else:
        # The controller cannot be created yet because there is
        # no valid configuration/client.
        tui = AmaliaTUI(
            controller=None,
            config=config,
            prompt_manager=prompt_manager,
        )

    tui.run()


if __name__ == "__main__":
    main()