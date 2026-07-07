import json
import time
import urllib.request
import questionary
from rich.console import Console
from rich.rule import Rule
from config import Config
from helpers import Messages, LLM
from bash import Bash

console = Console()

BANNER = r"""
                           _
     /\                   | |
    /  \   __ _  ___ _ __ | |_
   / /\ \ / _` |/ _ \ '_ \| __|
  / ____ \ (_| |  __/ | | | |_
 /_/    \_\__, |\___|_| |_|\__|
           __/ |
          |___/
"""

def fetch_cost(generation_id: str, api_key: str) -> str:
    url = f"https://openrouter.ai/api/v1/generation?id={generation_id}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            cost = data.get("data", {}).get("total_cost")
            if cost is not None:
                return f"${cost:.4f}"
    except Exception:
        pass
    return "n/a"

def print_banner():
    console.print(f"[bold cyan]{BANNER}[/bold cyan]")
    console.print(Rule(style="dim"))
    console.print()

def confirm_execution(cmd: str) -> bool:
    console.print(f"\nbash [bold]{cmd}[/bold]")
    console.print(Rule(style="dim"))
    choice = questionary.select(
        "bash requires approval",
        choices=["Yes", "No"],
        qmark="",
        style=questionary.Style([("selected", "fg:cyan bold"), ("pointer", "fg:cyan bold")]),
    ).ask()
    return choice == "Yes"

def main(config: Config):
    print_banner()
    bash = Bash(config)
    llm = LLM(config)
    messages = Messages(config.system_prompt)
    console.print("Type [bold cyan]quit[/bold cyan] at any time to exit.\n")

    # The main agent loop
    while True:
        # Get user message.
        console.print(f"You're currently in [bold cyan]{bash.cwd}[/bold cyan]")
        user = input("> ").strip()
        if user.lower() == "quit":
            print("\nShutting down. Bye!\n")
            break
        if not user:
            continue
        # Always tell the agent where the current working directory is to avoid confusions.
        user += f"\n Current working directory: `{bash.cwd}`"
        messages.add_user_message(user)

        # The tool-call/response loop
        while True:
            start = time.time()
            with console.status("[bold cyan]Thinking...", spinner_style="cyan"):
                response, tool_calls, usage, generation_id = llm.query(messages, [bash.to_json_schema()])
            elapsed = time.time() - start

            if response:
                response = response.strip()
                # Do not store the thinking part to save context space
                if "</think>" in response:
                    response = response.split("</think>")[-1].strip()

            # Always record the assistant turn (text + tool calls) before executing
            messages.add_assistant_turn(response or "", tool_calls)

            # Process tool calls
            cancelled = False
            if tool_calls:
                for tc in tool_calls:
                    function_name = tc.function.name
                    function_args = json.loads(tc.function.arguments)

                    # Ensure it's calling the right tool
                    if function_name != "exec_bash_command" or "cmd" not in function_args:
                        tool_call_result = json.dumps({"error": "Incorrect tool or function argument"})
                    else:
                        command = function_args["cmd"]
                        # Confirm execution with the user
                        if confirm_execution(command):
                            tool_call_result = bash.exec_bash_command(command)
                        else:
                            print("Rejected\n")
                            cancelled = True
                            break

                    messages.add_tool_message(tool_call_result, tc.id)

            if cancelled or not tool_calls:
                if not cancelled and response and response.strip():
                    console.print(response.strip())
                credits = getattr(usage, "total_tokens", 0)
                console.print(f"\n[dim]✓  Credits: {credits} • Time: {elapsed:.1f}s[/dim]\n")
                break

def cli():
    main(Config())

if __name__ == "__main__":
    cli()
