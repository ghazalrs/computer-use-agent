import subprocess
import os

_SENTINEL = "__END__"
_BLOCKED = ("$", "`")


class Shell:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.cwd = os.path.expanduser("~")

    def run(self, command: str) -> dict:
        for ch in _BLOCKED:
            if ch in command:
                return {"stdout": "", "stderr": f"Blocked character '{ch}' in command.", "cwd": self.cwd, "returncode": 1}

        wrapped = f"cd {self.cwd} && {command} ; echo {_SENTINEL} ; pwd"
        try:
            result = subprocess.run(
                ["bash", "-c", wrapped],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": f"Command timed out after {self.timeout}s.", "cwd": self.cwd, "returncode": 124}

        stdout = result.stdout
        if _SENTINEL in stdout:
            parts = stdout.rsplit(_SENTINEL, 1)
            stdout = parts[0].rstrip("\n")
            new_cwd = parts[1].strip()
            if new_cwd:
                self.cwd = new_cwd

        return {
            "stdout": stdout,
            "stderr": result.stderr,
            "cwd": self.cwd,
            "returncode": result.returncode,
        }
