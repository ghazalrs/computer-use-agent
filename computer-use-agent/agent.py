import json
from config import Config
from helpers import Messages, LLM
from bash import Bash

def confirm_execution(cmd: str) -> bool:
    """Ask the user whether the suggested command should be executed."""
    return input(f"    ▶️   Execute '{cmd}'? [y/N]: ").strip().lower() == "y"

def main(config: Config):
    bash = Bash(config)
    # The model
    llm = LLM(config)
    # The conversation history, with the system prompt
    messages = Messages(config.system_prompt)
    print("[INFO] Type 'quit' at any time to exit the agent loop.\n")

    # The main agent loop
    while True:
        # Get user message.
        user = input(f"['{bash.cwd}'] ").strip()
        if user.lower() == "quit":
            print("\n[🤖] Shutting down. Bye!\n")
            break
        if not user:
            continue
        # Always tell the agent where the current working directory is to avoid confusions.
        user += f"\n Current working directory: `{bash.cwd}`"
        messages.add_user_message(user)

        # The tool-call/response loop
        while True:
            print("\n[🤖] Thinking...")
            response, tool_calls = llm.query(messages, [bash.to_json_schema()])

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
                            print("Cancelled.\n")
                            cancelled = True
                            break

                    messages.add_tool_message(tool_call_result, tc.id)

            if cancelled or not tool_calls:
                if not cancelled and response and response.strip():
                    print(response.strip())
                    print("-" * 80 + "\n")
                break

def cli():
    main(Config())

if __name__ == "__main__":
    cli()
