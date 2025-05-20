# Chatbot TUI

A terminal-based user interface for interacting with AI chatbots, built with [Textual](https://textual.io/).

## Features

- Clean, intuitive terminal interface
- Support for multiple AI models
- Built-in tools for:
  - Executing shell commands
  - Text-to-speech functionality
  - Weather information retrieval
- Markdown rendering for chat messages

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/chatbot-tui.git
cd chatbot-tui

# Install dependencies
pip install -e .
```

## Usage

```bash
# Start the chatbot application
python -m chatbot_tui.main
```

### Keyboard Shortcuts

- `Ctrl+C`: Exit the application
- `Enter`: Send message
- `Esc`: Clear input field

## Project Structure

```
chatbot_tui/
├── __init__.py
├── chatbot.css       # Textual CSS styling
├── main.py           # Application entry point
├── tools.py          # Tool implementations
├── screens/          # Application screens
│   ├── __init__.py
│   └── chat.py       # Main chat interface
└── widgets/          # Custom UI components
    ├── __init__.py
    └── message.py    # Message display widget
```

## Tools

The application includes several built-in tools:

- `execute_cmd`: Run shell commands from within the chat
- `speak`: Convert text to speech
- `get_weather`: Retrieve weather information for a location

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
