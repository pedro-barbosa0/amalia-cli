from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Markdown, Static
from textual.theme import Theme

from ..app import AmaliaAppController
from ..configuration import Config
from ..prompts import PromptManager
from .setup import ConfigurationScreen
from ..client import AmaliaClient
from ..conversation import Conversation
from ..commands.registry import CommandRegistry

terminal_theme = Theme(
    name="terminal",
    primary="ansi_red",
    secondary="ansi_yellow",
    accent="ansi_cyan",
    foreground="ansi_white",
    background="ansi_black",
    surface="ansi_black",
    panel="ansi_black",
    dark=True,
)


class AmaliaTUI(App):
    """AMALIA terminal user interface."""

    TITLE = "AMALIA"
    CSS_PATH = "styles.tcss"

    def __init__(
        self,
        controller: AmaliaAppController | None,
        config: Config,
        prompt_manager: PromptManager,
    ) -> None:
        super().__init__(ansi_color=True)

        self.controller = controller
        self.config = config
        self.prompt_manager = prompt_manager

        self.register_theme(terminal_theme)
        self.theme = "terminal"

        self.current_response = ""
        self.response_widget: Markdown | None = None

    def compose(self) -> ComposeResult:
        yield Header()

        with VerticalScroll(id="messages"):
            yield Markdown(
                "**AMALIA**\n\nWelcome to AMALIA.",
                classes="message assistant",
            )

        yield Input(
            placeholder="Write a message...",
            id="input",
        )

        yield Footer()

    def on_mount(self) -> None:
        self.title = "AMALIA"
        self.sub_title = "CLI"

        if not self.config.is_configured():
            self.open_configuration(first_run=True)

    def on_input_submitted(
        self,
        event: Input.Submitted,
    ) -> None:
        if self.controller is None:
            return

        message = event.value.strip()

        if not message:
            return

        command_result = self.controller.handle_command(message)

        if command_result is not None:
            event.input.value = ""

            if command_result:
                self.add_assistant_message(command_result)

            if not self.controller.running:
                self.exit()

            return

        event.input.value = ""

        self.add_user_message(message)

        self.current_response = ""
        self.response_widget = self.add_assistant_message("")

        self.stream_response(message)

    @work(thread=True, exclusive=True)
    def stream_response(
        self,
        message: str,
    ) -> None:
        if self.controller is None:
            return

        try:
            for chunk in self.controller.send_message(message):
                self.call_from_thread(
                    self.append_response,
                    chunk,
                )

        except Exception as exc:
            self.call_from_thread(
                self.show_error,
                str(exc),
            )

    def append_response(
        self,
        chunk: str,
    ) -> None:
        self.current_response += chunk

        if self.response_widget is None:
            return

        self.response_widget.update(
            f"**AMALIA**\n\n{self.current_response}"
        )

        messages = self.query_one(
            "#messages",
            VerticalScroll,
        )

        messages.scroll_end(animate=False)

    def show_error(
        self,
        error: str,
    ) -> None:
        if self.response_widget is not None:
            self.response_widget.update(
                f"**AMALIA**\n\n⚠️ Error: {error}"
            )

    def add_user_message(
        self,
        message: str,
    ) -> None:
        messages = self.query_one(
            "#messages",
            VerticalScroll,
        )

        messages.mount(
            Static(
                f"[bold]You[/bold]\n{message}",
                classes="message user",
            )
        )

        messages.scroll_end(animate=False)

    def add_assistant_message(
        self,
        message: str,
    ) -> Markdown:
        messages = self.query_one(
            "#messages",
            VerticalScroll,
        )

        widget = Markdown(
            f"**AMALIA**\n\n{message}",
            classes="message assistant",
        )

        messages.mount(widget)
        messages.scroll_end(animate=False)

        return widget

    def open_configuration(
        self,
        first_run: bool = False,
    ) -> None:
        self.push_screen(
            ConfigurationScreen(
                config=self.config,
                prompt_manager=self.prompt_manager,
                first_run=first_run,
            ),
            self.configuration_finished,
        )

    def configuration_finished(
        self,
        result: bool | None,
    ) -> None:
        if not result:
            if not self.config.is_configured():
                self.exit()

            return

        self._initialize_controller()

        messages = self.query_one(
            "#messages",
            VerticalScroll,
        )

        messages.mount(
            Markdown(
                "**AMALIA**\n\nConfiguration saved. "
                "I'm ready.",
                classes="message assistant",
            )
        )

        messages.scroll_end(animate=False)

        self.query_one("#input", Input).focus()

    def _initialize_controller(self) -> None:
        prompt_name = self.config.default_prompt

        system_prompt = self.prompt_manager.get_prompt(
            prompt_name
        )

        client = AmaliaClient(self.config)

        conversation = Conversation(system_prompt)

        command_registry = CommandRegistry()

        self.controller = AmaliaAppController(
            client=client,
            conversation=conversation,
            command_registry=command_registry,
            config=self.config,
        )