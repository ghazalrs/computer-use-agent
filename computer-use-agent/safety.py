FORBIDDEN = [
    "rm -rf",
    "dd",
    "mkfs",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    ":(){ :|:& };:",
    "chmod -R 777 /",
    "chown -R",
    "> /dev/sda",
]

RISKY = [
    "rm",
    "sudo",
    "git push",
    "git reset --hard",
    "git clean",
    "mv",
    "chmod",
    "chown",
    "kill",
    "pkill",
    "curl",
    "wget",
    "pip install",
    "npm install",
]


def check(command: str) -> tuple[str, str | None]:
    """Return ('ok'|'forbidden'|'risky', matched_pattern)."""
    cmd = command.strip()
    for pattern in FORBIDDEN:
        if cmd.startswith(pattern):
            return "forbidden", pattern
    for pattern in RISKY:
        if cmd.startswith(pattern):
            return "risky", pattern
    return "ok", None
