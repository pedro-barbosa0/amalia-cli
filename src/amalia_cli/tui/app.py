from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Markdown, Static
from textual.theme import Theme

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

class AmaliaApp(App):
    """AMALIA TUI."""

    TITLE = "AMALIA CLI"
    CSS_PATH = "styles.tcss"

    def __init__(self) -> None:
        super().__init__(ansi_color=True)
        self.register_theme(terminal_theme)
        self.theme = "terminal"

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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()

        if not message:
            return

        event.input.value = ""

        self.add_user_message(message)

        # Temporary fake response.
        response = (
            "Olá! Recebi a tua mensagem.\n\n"
            "Podes agora testar **Markdown** aqui:\n\n"
            "- listas\n"
            "- **bold**\n"
            "- `inline code`\n\n"
            "```python\n"
            "print('AMALIA')\n"
            "```"
        )

        self.add_assistant_message(response)

    def add_user_message(self, message: str) -> None:
        messages = self.query_one("#messages", VerticalScroll)

        messages.mount(
            Static(
                f"[bold]You[/bold]\n{message}",
                classes="message user",
            )
        )

        messages.scroll_end(animate=False)

    def add_assistant_message(self, message: str) -> None:
        messages = self.query_one("#messages", VerticalScroll)

        messages.mount(
            Markdown(
                f"**AMALIA**\n\n{message}",
                classes="message assistant",
            )
        )

        messages.scroll_end(animate=False)


if __name__ == "__main__":
    AmaliaApp().run()