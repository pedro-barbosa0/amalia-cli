from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from amalia_cli.configuration import Config
from amalia_cli.prompts import PromptManager


class TextInputScreen(ModalScreen[str | None]):
    """Small modal used to edit a text value."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    def __init__(
        self,
        title: str,
        value: str,
        placeholder: str = "",
        password: bool = False,
    ) -> None:
        super().__init__()

        self.title = title
        self.value = value
        self.placeholder = placeholder
        self.password = password

    def compose(self) -> ComposeResult:
        with Container(id="edit-dialog"):
            yield Label(self.title, id="edit-title")

            yield Input(
                value=self.value,
                placeholder=self.placeholder,
                password=self.password,
                id="edit-input",
            )

            yield Label(
                "Enter = OK    Esc = Cancel",
                id="edit-help",
            )

    def on_mount(self) -> None:
        self.query_one("#edit-input", Input).focus()

    def on_input_submitted(
        self,
        event: Input.Submitted,
    ) -> None:
        self.dismiss(event.value.strip())

    def action_cancel(self) -> None:
        self.dismiss(None)


class PromptSelectScreen(ModalScreen[str | None]):
    """Small modal used to select the default prompt."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    def __init__(
        self,
        prompts: list[str],
        current_prompt: str | None,
    ) -> None:
        super().__init__()

        self.prompts = prompts
        self.current_prompt = current_prompt

    def compose(self) -> ComposeResult:
        with Container(id="prompt-dialog"):
            yield Label("Select default prompt", id="prompt-title")

            with ListView(id="prompt-list"):
                for prompt in self.prompts:
                    marker = "*" if prompt == self.current_prompt else " "
                    yield ListItem(
                        Static(f"[{marker}] {prompt}"),
                        id=f"prompt-{prompt}",
                    )

            yield Label(
                "Up/Down = Move    Enter = Select    Esc = Cancel",
                id="prompt-help",
            )

    def on_mount(self) -> None:
        prompt_list = self.query_one("#prompt-list", ListView)
        prompt_list.focus()

    def on_list_view_selected(
        self,
        event: ListView.Selected,
    ) -> None:
        if event.item.id is None:
            return

        prompt = event.item.id.removeprefix("prompt-")
        self.dismiss(prompt)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ConfigurationScreen(ModalScreen[bool]):
    """AMALIA configuration screen, menuconfig-style."""

    BINDINGS = [
        Binding("up","move_up","Move up",show=True,),
        Binding("down","move_down","Move down",show=True,),
        Binding("enter","edit_selected","Edit",show=True,),
        Binding("s","save","Save",show=True,),
        Binding("ctrl+s","save","Save",show=True,),
        Binding("escape","cancel","Cancel",show=True,),
        Binding("c","cancel","Cancel",show=True,),
    ]

    FIELD_ORDER = [
        "api_key",
        "base_url",
        "model",
        "temperature",
        "max_completion_tokens",
        "default_prompt",
    ]

    FIELD_LABELS = {
        "api_key": "API Key",
        "base_url": "Base URL",
        "model": "Model",
        "temperature": "Temperature",
        "max_completion_tokens": "Max completion tokens",
        "default_prompt": "Default prompt",
    }

    FIELD_HELP = {
        "api_key": (
            "API key used to authenticate with the AMALIA-compatible API. "
            "This value is stored in your local configuration."
        ),
        "base_url": (
            "Base URL of the local or remote OpenAI-compatible server. "
            "Example: http://127.0.0.1:8001"
        ),
        "model": (
            "Model name sent to the server. "
            "Example: amalia-9b-0626-dpo"
        ),
        "temperature": (
            "Optional sampling temperature. Leave empty to use the server default."
        ),
        "max_completion_tokens": (
            "Optional maximum number of completion tokens. "
            "Leave empty to use the server default."
        ),
        "default_prompt": (
            "Default system prompt/profile used by AMALIA."
        ),
    }

    def __init__(
        self,
        config: Config,
        prompt_manager: PromptManager,
        first_run: bool = False,
    ) -> None:
        super().__init__()

        self.config = config
        self.prompt_manager = prompt_manager
        self.first_run = first_run

        self.values: dict[str, str] = {
            "api_key": self.config.api_key or "",
            "base_url": self.config.base_url or "http://127.0.0.1:8001",
            "model": self.config.model or "amalia-9b-0626-dpo",
            "temperature": (
                str(self.config.temperature)
                if self.config.temperature is not None
                else ""
            ),
            "max_completion_tokens": (
                str(self.config.max_completion_tokens)
                if self.config.max_completion_tokens is not None
                else ""
            ),
            "default_prompt": self.config.default_prompt or "",
        }

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="configuration-root"):
            with Vertical(id="configuration-panel"):
                
                with Horizontal(id="configuration-body"):
                    with ListView(id="configuration-menu"):
                        for field in self.FIELD_ORDER:
                            yield self.make_field_item(field)
                 
                yield Label("", id="error")

                with Horizontal(id="bottom-row"):
                    with Vertical(id="configuration-actions"):
                        if not self.first_run:
                            yield Button(
                                "Cancel",
                                id="cancel",
                                variant="default",
                            )

                        yield Button(
                            "Save",
                            id="save",
                            variant="primary",
                        )
                    with Vertical(id="configuration-help"):
                        yield Static("", id="help-text")

                
        yield Footer()

    def on_mount(self) -> None:
        menu = self.query_one("#configuration-menu", ListView)
        menu.focus()

        self.update_help_for_selected()

    def make_field_item(
        self,
        field: str,
    ) -> ListItem:
        return ListItem(
            Static(
                self.render_field_line(field),
                classes="configuration-row-text",
            ),
            id=f"field-{field}",
        )

    def render_field_line(
        self,
        field: str,
    ) -> str:
        label = self.FIELD_LABELS[field]
        value = self.values[field]

        if field == "api_key" and value:
            display_value = "*" * min(len(value), 12)

        elif value:
            display_value = value

        else:
            display_value = "<empty>"

        return f"{label:<24} {display_value}"

    def selected_field(self) -> str | None:
        menu = self.query_one("#configuration-menu", ListView)
        item = menu.highlighted_child

        if item is None or item.id is None:
            return None

        if not item.id.startswith("field-"):
            return None

        return item.id.removeprefix("field-")

    def update_field_row(
        self,
        field: str,
    ) -> None:
        item = self.query_one(f"#field-{field}", ListItem)
        row_text = item.query_one(Static)
        row_text.update(self.render_field_line(field))

    def update_help_for_selected(self) -> None:
        field = self.selected_field()

        if field is None:
            return

        help_text = self.query_one("#help-text", Static)
        help_text.update(self.FIELD_HELP[field])

    def on_list_view_highlighted(
        self,
        event: ListView.Highlighted,
    ) -> None:
        self.update_help_for_selected()

    def on_list_view_selected(
        self,
        event: ListView.Selected,
    ) -> None:
        self.edit_selected_field()

    def action_edit_selected(self) -> None:
        self.edit_selected_field()

    def edit_selected_field(self) -> None:
        field = self.selected_field()

        if field is None:
            return

        if field == "default_prompt":
            self.edit_prompt()
            return

        title = f"Edit {self.FIELD_LABELS[field]}"
        value = self.values[field]

        placeholder = ""

        if field == "api_key":
            placeholder = "Enter API key"

        elif field == "base_url":
            placeholder = "http://127.0.0.1:8001"

        elif field == "model":
            placeholder = "Model name"

        elif field == "temperature":
            placeholder = "Server default"

        elif field == "max_completion_tokens":
            placeholder = "Server default"

        self.app.push_screen(
            TextInputScreen(
                title=title,
                value=value,
                placeholder=placeholder,
                password=(field == "api_key"),
            ),
            lambda new_value: self.on_text_value_edited(field, new_value),
        )

    def on_text_value_edited(
        self,
        field: str,
        new_value: str | None,
    ) -> None:
        if new_value is None:
            return

        self.values[field] = new_value
        self.update_field_row(field)

        self.query_one("#configuration-menu", ListView).focus()

    def edit_prompt(self) -> None:
        prompts = self.prompt_manager.list_prompts()

        self.app.push_screen(
            PromptSelectScreen(
                prompts=prompts,
                current_prompt=self.values["default_prompt"],
            ),
            self.on_prompt_selected,
        )

    def on_prompt_selected(
        self,
        prompt: str | None,
    ) -> None:
        if prompt is None:
            return

        self.values["default_prompt"] = prompt
        self.update_field_row("default_prompt")

        self.query_one("#configuration-menu", ListView).focus()

    def on_button_pressed(
        self,
        event: Button.Pressed,
    ) -> None:
        if event.button.id == "save":
            self.save_configuration()

        elif event.button.id == "cancel":
            self.cancel_configuration()

    def action_save(self) -> None:
        self.save_configuration()

    def action_cancel(self) -> None:
        self.cancel_configuration()

    def cancel_configuration(self) -> None:
        if self.first_run and not self.config.is_configured():
            self.show_error(
                "Please complete the configuration before continuing."
            )
            return

        self.dismiss(False)

    def save_configuration(self) -> None:
        api_key = self.values["api_key"].strip()
        base_url = self.values["base_url"].strip()
        model = self.values["model"].strip()
        temperature_text = self.values["temperature"].strip()
        max_tokens_text = self.values["max_completion_tokens"].strip()
        default_prompt = self.values["default_prompt"].strip()

        try:
            if not api_key:
                raise ValueError("API key cannot be empty.")

            if not base_url:
                raise ValueError("Base URL cannot be empty.")

            if not model:
                raise ValueError("Model cannot be empty.")

            if temperature_text:
                try:
                    temperature = float(temperature_text)
                except ValueError as exc:
                    raise ValueError(
                        "Temperature must be a valid number."
                    ) from exc
            else:
                temperature = None

            if max_tokens_text:
                try:
                    max_completion_tokens = int(max_tokens_text)
                except ValueError as exc:
                    raise ValueError(
                        "Max completion tokens must be a valid integer."
                    ) from exc
            else:
                max_completion_tokens = None

            prompts = self.prompt_manager.list_prompts()

            if not default_prompt or default_prompt not in prompts:
                raise ValueError("Please select a default prompt.")

            self.config.save(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_completion_tokens=max_completion_tokens,
                default_prompt=default_prompt,
            )

        except ValueError as exc:
            self.show_error(str(exc))
            return

        self.dismiss(True)

    def show_error(
        self,
        message: str,
    ) -> None:
        self.query_one("#error", Label).update(message)