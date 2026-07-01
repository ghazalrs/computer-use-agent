# computer-use-agent

A terminal-focused computer use CLI agent powered by an LLM via OpenRouter.

## Project Goal

Build an agentic CLI tool that accepts a natural language goal and autonomously executes bash commands and file operations to accomplish it — similar to Claude Code but configurable with any OpenRouter model.

## Architecture

```
agent.py        # agentic loop + CLI entry point
llm.py          # OpenRouter client, tool definitions
shell.py        # stateful bash session (tracks cwd)
tools.py        # tool executor (routes LLM tool calls)
safety.py       # forbidden/risky command checks (reads safety.md)
config.py       # model, timeouts, defaults
safety.md       # forbidden and risky command lists (user-editable)
.env            # OPENROUTER_API_KEY, MODEL_ID
pyproject.toml  # package config + CLI entry point
requirements.txt
```

## Agentic Loop

1. User provides a natural language goal via CLI
2. Agent sends goal + current cwd to LLM with tool definitions
3. LLM returns a tool call (bash command or file operation)
4. Safety check runs against safety.md
5. User confirms before execution
6. Output is captured and fed back to LLM
7. Repeat until LLM signals completion or user aborts (Ctrl+C)

## Tools

- `bash` — run a shell command, returns stdout/stderr/cwd
- `read_file` — read a file's contents
- `write_file` — write/overwrite a file
- `str_replace` — edit a specific part of a file

## Safety Model

Defined in `safety.md` with two sections:

- **Forbidden** — blocked unconditionally, even if user confirms (e.g. `rm -rf`, `dd`, `mkfs`, `shutdown`)
- **Risky** — allowed only after explicit user confirmation with a warning (e.g. `rm`, `sudo`, `git push`)

Check is prefix-based (e.g. any command starting with `rm -rf` is forbidden).

## Shell

- Single stateful bash session per run
- `cwd` tracked by appending `; echo __END__; pwd` to each command and parsing output
- `$` and backtick characters blocked to prevent command injection
- Configurable timeout per command (default: 30s)

## CLI Usage

After installation (`pip install -e .`), the tool is available as `agent` system-wide:

```bash
agent "set up a flask project in ~/projects/myapp"
agent "find all TODO comments in this repo" --model google/gemini-2.5-pro
agent "..." --max-steps 30 --timeout 60
```

The activation word `agent` is a placeholder — rename it in `pyproject.toml` under `[project.scripts]` once a final name is chosen:

```toml
[project.scripts]
agent = "agent:main"
```

## Key Design Decisions

- **Blocklist over allowlist** — agent can run any command except explicitly forbidden/risky ones, making it more flexible than an allowlist approach
- **Markdown safety config** — `safety.md` is user-editable without touching Python code
- **Stateful shell via cwd trick** — appending `; echo __END__; pwd` tracks directory changes without a persistent subprocess
- **Strip `</think>` tags** — reasoning model output (DeepSeek, Nemotron, etc.) has thinking tokens stripped before storing in conversation history to save context
- **OpenRouter** — model-agnostic; swap models via `.env` or `--model` flag

## Installation

```bash
cd ~/projects/computer-use-agent
pip install -e .
```

This installs the package in editable mode and registers the `agent` command in your PATH via `pyproject.toml`.

## Dependencies

```
openai          # OpenRouter uses OpenAI-compatible API
rich            # terminal output
python-dotenv
```

## Environment Variables

```
OPENROUTER_API_KEY=...
MODEL_ID=anthropic/claude-sonnet-4-5   # or any OpenRouter model
```

## Sharing / Distribution

### Option 1 — GitHub + pip (recommended while in development)
Push to GitHub. Others install with:
```bash
pip install git+https://github.com/yourname/computer-use-agent.git
```
No PyPI account needed. The `agent` command is available after install.

### Option 2 — PyPI (for stable releases)
Publish to pypi.org so anyone can install with:
```bash
pip install <your-chosen-name>
```
Requires a PyPI account and `twine`. The package name must be unique on PyPI — finalize the activation word before publishing.

### Option 3 — Homebrew tap (macOS-native feel)
Create a Homebrew tap so Mac users can install with:
```bash
brew install yourname/tap/<name>
```

### Option 4 — Single-file script (zero friction)
Bundle into one file and share directly. Users run `python agent.py "..."` with no install step.
