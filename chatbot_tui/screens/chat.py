import asyncio
from typing import cast
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionToolParam
from openai.types.chat.chat_completion_chunk import (
    ChoiceDeltaToolCall,
)
from textual.containers import HorizontalGroup, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Select
from textual.events import Key
from ..tools import tools
from chatbot_tui.widgets.message import Message


class ChatScreen(Screen):
    """Main chat screen"""

    MODEL_OPTIONS = [
        ("GPT 4.1 Mini", "gpt-4.1-mini"),
        ("GPT 4 Turbo", "gpt-4-turbo"),
        ("GPT 3.5 Turbo", "gpt-3.5-turbo"),
    ]
    DEFAULT_MODEL = "gpt-4.1-mini"

    history: list = [{"role": "system", "content": "You are a helpful assistant."}]

    async def on_mount(self):
        """Mount the chat screen and add a message widget."""
        self.query_exactly_one(".input-group Input", Input).focus()

    def compose(self):
        yield Header()
        yield Select(
            options=self.MODEL_OPTIONS, value=self.DEFAULT_MODEL, id="model_selector"
        )
        yield VerticalScroll(id="messages")
        yield HorizontalGroup(
            Input(),
            Button("Send", variant="primary", id="send"),
            classes="input-group",
        )
        yield Footer()

    async def on_key(self, event: Key) -> None:
        if event.key == "enter":
            event.stop()
            await self.send()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send":
            event.stop()
            await self.send()

    async def send(self):
        input_w = self.query_one(".input-group Input", Input)
        text = input_w.value.strip()
        input_w.value = ""
        if not text:
            return

        self.run_worker(self.complete(text))

    async def complete(self, prompt: str):
        messages = self.query_one("#messages", VerticalScroll)
        self.history.append({"role": "user", "content": prompt})
        user_message = Message(prompt, role="user")
        messages.scroll_end()

        await messages.mount(user_message)
        for _ in range(10):
            message = Message("..", role="assistant")
            await messages.mount(message)

            model_selector = self.query_one("#model_selector", Select)
            selected_model = model_selector.value
            if selected_model is None:  # Handle case where value might be None
                selected_model = self.DEFAULT_MODEL

            client = AsyncOpenAI()
            response = await client.chat.completions.create(
                model=selected_model,  # Use the selected model here
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    *self.history,
                ],
                stream=True,
                tools=cast(list[ChatCompletionToolParam], tools.definitions()),
            )

            full_reply = ""
            final_tool_calls: dict[int, ChoiceDeltaToolCall] = {}
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_reply = message.message + content
                    message.message = full_reply
                    messages.scroll_end()

                for tool_call in chunk.choices[0].delta.tool_calls or []:
                    index = tool_call.index

                    if index not in final_tool_calls:
                        final_tool_calls[index] = tool_call

                    assert tool_call.function
                    final_tool_calls[index].function.arguments += (  # pyright: ignore
                        tool_call.function.arguments or ""
                    )

            self.history.append(
                {
                    "role": "assistant",
                    "content": full_reply,
                    "tool_calls": list(final_tool_calls.values()) or None,
                }
            )

            if final_tool_calls:
                tools_as_str = "\n".join(
                    f"\n```json\n{tool_call.function.model_dump_json()}\n```"  # pyright: ignore
                    for tool_call in final_tool_calls.values()
                )
                message.message += tools_as_str
                messages.scroll_end()

                tool_status_messages_to_remove = []
                for tool_call in final_tool_calls.values():
                    tool_name = tool_call.function.name
                    status_message_widget = Message(
                        f"Executing tool: {tool_name}...", role="tool_status"
                    )
                    await messages.mount(status_message_widget)
                    tool_status_messages_to_remove.append(status_message_widget)
                messages.scroll_end()

                tool_results = await asyncio.gather(
                    *(
                        tools.smart_tool_call(tool_call.model_dump())  # pyright: ignore
                        for tool_call in final_tool_calls.values()
                    )
                )
                self.history.extend(r.message for r in tool_results)

                for status_msg in tool_status_messages_to_remove:
                    await status_msg.remove()
            else:
                return
