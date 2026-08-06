from collections.abc import Iterator

from amalia_cli.agent.executor import AgentExecutor

from .client import AmaliaClient
from .conversation import Conversation
from .commands.registry import CommandRegistry
from .mode import Mode
from .agent.session import AgentSession
from .agent.executor import ExecutionResult
class AmaliaAppController:
    def __init__(
        self,
        client: AmaliaClient,
        chat_conversation: Conversation,
        command_registry: CommandRegistry,
        agent_session: AgentSession,
        agent_executor: AgentExecutor,
        config ,
    ):
        self.client = client
        self.chat_conversation = chat_conversation
        self.agent_session = agent_session
        self.command_registry = command_registry
        self.config = config
        self.running = True
        self.mode = Mode.CHAT
        self.agent_executor = agent_executor

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
        if self.mode == Mode.AGENT:
            yield from self.send_agent_message(message)
            return

        yield from self.send_chat_message(message)

    def send_chat_message(
        self,
        message: str,
    ) -> Iterator[str]:
        self.chat_conversation.add_user_message(message)

        full_response = ""

        for chunk in self.client.chat_stream(
            self.chat_conversation.get_messages()
        ):
            full_response += chunk
            yield chunk

        self.chat_conversation.add_assistant_message(
            full_response
        )

    def execute_agent_code(
            self,
            code: str,
        ):
            return self.agent_executor.execute(code)

    def send_agent_message(
        self,
        message: str,
    ) -> Iterator[str]:
        self.agent_session.add_user_message(message)

        full_response = ""

        for chunk in self.client.chat_stream(
            self.agent_session.get_messages(
                include_execution_results=True,
            )
        ):
            full_response += chunk

        clean_code = self.agent_executor.clean_code(
            full_response
        )

        formatted_code = self.format_python_code_block(
            clean_code
        )

        yield formatted_code

        self.agent_session.add_assistant_message(
            clean_code
        )

        result = self.execute_agent_code(
            clean_code,
        )

        self.agent_session.add_turn(
            user_prompt=message,
            generated_code=clean_code,
            execution_result=result,
        )

        yield "\n\n"
        yield f"[exit code: {result.return_code}]\n"

        if result.stdout:
            yield result.stdout

        if result.stderr:
            yield f"\nERROR:\n{result.stderr}"

        yield "\n\n"

        for chunk in self.explain_agent_result_stream(
            user_prompt=message,
            generated_code=clean_code,
            execution_result=result,
        ):
            yield chunk

    def format_python_code_block(
        self,
        code: str,
    ) -> str:
        clean_code = self.agent_executor.clean_code(code)

        return (
            "```python\n"
            f"{clean_code}\n"
            "```"
    )

    def get_active_conversation(self) -> Conversation:
        if self.mode == Mode.CHAT:
            return self.chat_conversation

        return self.agent_session.conversation

    

    def explain_agent_result_stream(
        self,
        user_prompt: str,
        generated_code: str,
        execution_result: ExecutionResult,
    ) -> Iterator[str]:
        messages = [
            {
                "role": "system",
                "content": (
                    "És a AMALIA. "
                    "O utilizador fez um pedido, tu geraste código Python para cumprir esse pedido, "
                    "e esse código foi executado no sistema do utilizador. "
                    "Agora deves explicar de forma curta, clara e útil o que aconteceu. "
                    "Responde em português europeu. "
                    "Não repitas o código completo. "
                    "Não inventes problemas. "
                    "Se o código de saída for 0, assume que a execução correu bem. "
                    "Se stderr estiver vazio, não menciones stderr. "
                    "Se houver erro, explica o erro principal e sugere o próximo passo. "
                    "Máximo: 2 ou 3 frases."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Eu pedi isto:\n{user_prompt}\n\n"
                    f"Tu geraste este código Python para fazer o que eu pedi:\n{generated_code}\n\n"
                    f"O código foi executado no meu sistema e estes foram os resultados:\n\n"
                    f"Código de saída: {execution_result.return_code}\n\n"
                    f"stdout:\n{execution_result.stdout or '<vazio>'}\n\n"
                    f"stderr:\n{execution_result.stderr or '<vazio>'}"
                ),
            },
        ]

        return self.client.chat_stream(messages)