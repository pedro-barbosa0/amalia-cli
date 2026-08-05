import argparse
from pathlib import Path

from .client import AmaliaClient
from .configuration import Config
from .conversation import Conversation
from .prompts import PromptManager


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="amalia",
        description="CLI for interacting with the AMALIA language model.",
    )

    parser.add_argument(
        "--prompt",
        help="System prompt to use.",
    )

    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List available system prompts.",
    )

    return parser.parse_args()


def select_prompt(prompt_manager: PromptManager) -> str | None:
    prompts = prompt_manager.list_prompts()

    if not prompts:
        raise RuntimeError(
            f"No prompts found in: {prompt_manager.prompts_directory}"
        )

    print("Available system prompts:\n")

    for index, prompt_name in enumerate(prompts, start=1):
        print(f"  {index}. {prompt_name}")

    print()

    while True:
        selection = input("Select a prompt: ").strip()

        if selection.lower() == "exit":
            return None

        try:
            index = int(selection)
        except ValueError:
            print("Please enter a number or 'exit'.")
            continue

        if 1 <= index <= len(prompts):
            return prompt_manager.get_prompt(prompts[index - 1])

        print("Invalid selection.")

def main():
    args = parse_arguments()

    config = Config()
    client = AmaliaClient(config)

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

    if args.prompt:
        system_prompt = prompt_manager.get_prompt(args.prompt)
    else:
        system_prompt = select_prompt(prompt_manager)
        
    if system_prompt is None:
        return

    conversation = Conversation(system_prompt)

    print("\nAMALIA CLI")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You > ")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if user_input.lower() == "exit":
            break

        if not user_input.strip():
            continue

        conversation.add_user_message(user_input)

        print("AMALIA > ", end="", flush=True)

        assistant_response = client.chat(
            conversation.get_messages()
        )

        conversation.add_assistant_message(assistant_response)


if __name__ == "__main__":
    main()