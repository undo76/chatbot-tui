from textual.app import App
from chatbot_tui.screens import ChatScreen


class ChatbotApp(App):
    """A simple chatbot application using Textual."""

    SCREENS = {
        "chat": ChatScreen,
    }
    CSS_PATH = "chatbot.css"
    TITLE = "Chatbot TUI"

    async def on_mount(self) -> None:
        await self.push_screen("chat")


app = ChatbotApp()

if __name__ == "__main__":
    app.run()
