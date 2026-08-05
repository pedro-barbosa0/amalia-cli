from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Markdown, Static
from textual.theme import Theme

from ..app import AmaliaAppController


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
        controller: AmaliaAppController,
    ) -> None:
        super().__init__(ansi_color=True)

        self.controller = controller

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
        self.title = "Amalia"
        self.sub_title = "CLI"

    def on_input_submitted(
            self,
            event: Input.Submitted,
    ) -> None:
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