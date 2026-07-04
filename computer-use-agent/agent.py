import argparse
import json
import sys

from rich.console import Console
from rich.prompt import Confirm

from config import MODEL_ID, DEFAULT_MAX_STEPS, DEFAULT_TIMEOUT
from llm import LLMClient
from shell import Shell
from tools import execute

console = Console()


def confirm_execution(cmd: str) -> bool:
    """Ask the user whether the suggested command should be executed."""
    return input(f"    ▶️   Execute '{cmd}'? [y/N]: ").strip().lower() == "y"


def confirm_fn(prompt: str) -> bool:
    return Confirm.ask(f"[yellow]{prompt}[/yellow]")


def run_agent(goal: str, model: str, max_steps: int, timeout: int):
    shell = Shell(timeout=timeout)
    llm = LLMClient(model=model)

    system_prompt = (
        "You are an autonomous terminal agent. "
        "Accomplish the user's goal by issuing tool calls one at a time. "
        "When the goal is complete, respond with a plain text summary and no tool call."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Goal: {goal}\nCurrent directory: {shell.cwd}"},
    ]

    console.rule("[bold blue]Agent started")
    console.print(f"[bold]Goal:[/bold] {goal}")
    console.print(f"[dim]Model: {model}  Max steps: {max_steps}[/dim]\n")

    for step in range(1, max_steps + 1):
        console.rule(f"[dim]Step {step}")
        msg = llm.complete(messages)

        if not msg.tool_calls:
            console.print(f"\n[green]Done:[/green] {msg.content}")
            break

        messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
            {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls
        ]})

        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)

            console.print(f"[bold cyan]Tool:[/bold cyan] {name}")
            console.print(f"[dim]{json.dumps(args, indent=2)}[/dim]")

            result = execute(name, args, shell, confirm_fn)

            console.print(f"[dim]Result:[/dim]\n{result}\n")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
    else:
        console.print("[red]Max steps reached without completion.[/red]")


def main():
    parser = argparse.ArgumentParser(description="Autonomous terminal agent powered by OpenRouter.")
    parser.add_argument("goal", help="Natural language goal for the agent.")
    parser.add_argument("--model", default=MODEL_ID, help="OpenRouter model ID.")
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Per-command timeout in seconds.")
    args = parser.parse_args()

    try:
        run_agent(args.goal, args.model, args.max_steps, args.timeout)
    except KeyboardInterrupt:
        console.print("\n[red]Aborted.[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
