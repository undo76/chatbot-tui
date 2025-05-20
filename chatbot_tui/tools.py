import subprocess
from typing import Annotated
from toolkitr import ToolRegistry

tools = ToolRegistry()


@tools.tool()
async def execute_cmd(
    cmd: Annotated[str, "Command to execute"],
    cwd: Annotated[str, "Current working directory"],
):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, shell=True)
    if result.returncode != 0:
        raise Exception("Failed to execute command:\n" + result.stderr)
    return result.stdout


@tools.tool()
async def speak(text: Annotated[str, "Text to speak"]):
    """Speak the given text using the system's text-to-speech engine."""
    subprocess.run(["say", text], check=True)
    return "Spoken: " + text


@tools.tool()
async def get_weather(
    location: Annotated[str, "City name"],
):
    """Returns the weather for a given location."""
    result = subprocess.run(
        f"curl -i 'https://wttr.in/{location}?format=j1'",
        check=True,
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Exception("Failed to get weather data:\n" + result.stderr)
    return result.stdout


if __name__ == "__main__":
    # Example usage
    import asyncio
    import rich
    import json

    rich.print("Tool defintions:")
    rich.print(json.dumps(tools.definitions(), indent=2))

    async def main():
        print(await execute_cmd("echo Hello, World!", "."))
        print(await speak("Hello, World!"))
        print(await get_weather("Brussels"))

    asyncio.run(main())
