from pathlib import Path
from bash import Bash

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "exec_bash_command",
            "description": "Execute a bash command and return stdout/stderr and the working directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {"type": "string", "description": "The bash command to execute."},
                },
                "required": ["cmd"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a file by path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative path to the file."},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file, creating it if it does not exist or overwriting it if it does.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative path to the file."},
                    "content": {"type": "string", "description": "The content to write to the file."},
                },
                "required": ["path", "content"],
            },
        },
    },
]


def execute(tool_name: str, args: dict, bash: Bash) -> dict:
    if tool_name == "exec_bash_command":
        return bash.exec_bash_command(args.get("cmd", ""))
    elif tool_name == "read_file":
        return _read_file(args.get("path", ""), bash.cwd)
    elif tool_name == "write_file":
        return _write_file(args.get("path", ""), args.get("content", ""), bash.cwd)
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def _read_file(path: str, cwd: str) -> dict:
    try:
        p = Path(path) if Path(path).is_absolute() else Path(cwd) / path
        return {"content": p.read_text()}
    except Exception as e:
        return {"error": str(e)}


def _write_file(path: str, content: str, cwd: str) -> dict:
    try:
        p = Path(path) if Path(path).is_absolute() else Path(cwd) / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return {"success": f"Wrote {p}"}
    except Exception as e:
        return {"error": str(e)}
