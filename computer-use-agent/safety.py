import re
from pathlib import Path

_SAFETY_MD = Path(__file__).parent / "safety.md"


def _parse_safety_md() -> tuple[list[str], list[str]]:
    text = _SAFETY_MD.read_text()
    forbidden, risky = [], []
    current = None
    for line in text.splitlines():
        lower = line.strip().lower()
        if lower == "## forbidden":
            current = forbidden
        elif lower == "## risky":
            current = risky
        elif line.startswith("- ") and current is not None:
            current.append(line[2:].strip())
    return forbidden, risky


def check(command: str) -> tuple[str, str | None]:
    """Return ('ok'|'forbidden'|'risky', matched_pattern)."""
    forbidden, risky = _parse_safety_md()
    cmd = command.strip()
    for pattern in forbidden:
        if cmd.startswith(pattern):
            return "forbidden", pattern
    for pattern in risky:
        if cmd.startswith(pattern):
            return "risky", pattern
    return "ok", None
