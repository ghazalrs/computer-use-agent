import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """
    Configuration class for the application.
    """

    # -------------------------------------
    # LLM configuration
    #--------------------------------------

    model_id = os.getenv("model_id", "anthropic/claude-sonnet-4-5")
    openrouter_api_key = os.getenv("openrouter_api_key", "")
    openrouter_base_url = "https://openrouter.ai/api/v1"

    default_max_steps = 20
    default_timeout = 30

    # -------------------------------------
    # Agent configuration
    #--------------------------------------

    # The directory path that the agent can access and operate in.
    root_dir: str = os.path.dirname(os.path.abspath(__file__))

    # The list of commands that the agent can execute.
    allowed_commands: list = field(default_factory=lambda: [
        "cd", "cp", "ls", "cat", "find", "touch", "echo", "grep", "pwd", "mkdir", "wget", "sort", "head", "tail", "du",
    ])

    @property
    def system_prompt(self) -> str:
        """Generate the system prompt for the LLM based on allowed commands."""
        return f"""/think

You are a helpful and very concise Bash assistant with the ability to execute commands in the shell.
You engage with users to help answer questions about bash commands, or execute their intent.
If user intent is unclear, keep engaging with them to figure out what they need and how to best help
them. If they ask question that are not relevant to bash or computer use, decline to answer.

When a command is executed, you will be given the output from that command and any errors. Based on
that, either take further actions or yield control to the user.

The bash interpreter's output and current working directory will be given to you every time a
command is executed. Take that into account for the next conversation.
If there was an error during execution, tell the user what that error was exactly.

You are only allowed to execute the following commands. Break complex tasks into shorter commands from this list:

```
{self.allowed_commands}
```

**Never** attempt to execute a command not in this list. **Never** attempt to execute dangerous commands
like `rm`, `mv`, `rmdir`, `sudo`, etc. If the user asks you to do so, politely refuse.
"""
