import json
from pathlib import Path
from shell import Shell
from safety import check


def execute(tool_name: str, tool_args: dict, shell: Shell, confirm_fn) -> str:
    if tool_name == "bash":
        return _bash(tool_args["command"], shell, confirm_fn)
    elif tool_name == "read_file":
        return _read_file(tool_args["path"])
    elif tool_name == "write_file":
        return _write_file(tool_args["path"], tool_args["content"], confirm_fn)
    elif tool_name == "str_replace":
        return _str_replace(tool_args["path"], tool_args["old_str"], tool_args["new_str"], confirm_fn)
    else:
        return f"Unknown tool: {tool_name}"


def _bash(command: str, shell: Shell, confirm_fn) -> str:
    status, pattern = check(command)
    if status == "forbidden":
        return f"Forbidden: command matches blocked pattern '{pattern}'."
    if status == "risky":
        if not confirm_fn(f"Risky command (matches '{pattern}'): {command}"):
            return "User declined to run risky command."
    else:
        if not confirm_fn(f"Run: {command}"):
            return "User declined."

    result = shell.run(command)
    parts = []
    if result["stdout"]:
        parts.append(result["stdout"])
    if result["stderr"]:
        parts.append(f"[stderr] {result['stderr']}")
    parts.append(f"[cwd] {result['cwd']}  [rc] {result['returncode']}")
    return "\n".join(parts)


def _read_file(path: str) -> str:
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


def _write_file(path: str, content: str, confirm_fn) -> str:
    if not confirm_fn(f"Write file: {path}"):
        return "User declined."
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"Wrote {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def _str_replace(path: str, old_str: str, new_str: str, confirm_fn) -> str:
    if not confirm_fn(f"Edit file: {path}"):
        return "User declined."
    try:
        p = Path(path)
        text = p.read_text()
        if old_str not in text:
            return f"String not found in {path}."
        p.write_text(text.replace(old_str, new_str, 1))
        return f"Replaced in {path}"
    except Exception as e:
        return f"Error editing file: {e}"
