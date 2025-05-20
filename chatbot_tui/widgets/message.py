from typing import Literal
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.containers import HorizontalGroup
from textual.widgets import Markdown, Static


class Message(HorizontalGroup):
    """A simple message widget for displaying chat messages."""

    role = reactive("assistant", recompose=True)
    message = reactive("", layout=True)

    def __init__(self, message: str, *, role: Literal["user", "assistant"]) -> None:
        super().__init__()
        self.role = role
        self.message = message

    def on_mount(self) -> None:
        """Set the initial state of the message widget."""
        self.set_classes("message")
        self.set_class(self.role == "assistant", "assistant")
        self.set_class(self.role == "user", "user")

    def compose(self) -> ComposeResult:
        if self.role == "user":
            yield Static(
                self.message,
                id="bubble",
                markup=False,
            )
        elif self.role == "assistant":
            yield Markdown(self.message, id="bubble")
        else:
            raise ValueError(f"Invalid role: {self.role}")

    async def watch_message(self, message: str) -> None:
        """Update the message content when the message changes."""
        if self.role == "user":
            self.query_one("#bubble", Static).update(message)
        elif self.role == "assistant":
            self.query_one("#bubble", Markdown).update(message)
