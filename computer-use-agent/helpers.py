from typing import Any, Dict, List, Tuple
from openai import OpenAI

from config import Config

class Messages:
    """
    An abstraction for a list of system/user/assistant/tool messages.
    """

    def __init__(self, system_message: str = ""):
        self.system_message = None
        self.messages = []
        self.set_system_message(system_message)

    def set_system_message(self, message):
        self.system_message = {"role": "system", "content": message}

    def add_user_message(self, message):
        self.messages.append({"role": "user", "content": message})

    def add_assistant_message(self, message):
        self.messages.append({"role": "assistant", "content": message})

    def add_assistant_turn(self, content: str, tool_calls):
        msg = {"role": "assistant", "content": content or ""}
        if tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in tool_calls
            ]
        self.messages.append(msg)

    def add_tool_message(self, message, id):
        import json
        content = json.dumps(message) if isinstance(message, dict) else str(message)
        self.messages.append({"role": "tool", "content": content, "tool_call_id": id})

    def to_list(self) -> List[Dict[str, str]]:
        """
        Convert to a list of messages.
        """
        return [self.system_message] + self.messages

class LLM:
    """
    An abstraction to prompt an LLM with OpenAI compatible endpoint.
    """

    def __init__(self, config: Config):
        super().__init__()
        self.client = OpenAI(base_url=config.openrouter_base_url, api_key=config.openrouter_api_key)
        self.config = config
        print(f"Using model '{config.openrouter_model_name}' from '{config.openrouter_base_url}'")

    def query(
        self,
        messages: Messages,
        tools: List[Dict[str, Any]],
        max_tokens=None,
    ) -> Tuple[str, List[Dict[str, Any]], Any]:
        completion = self.client.chat.completions.create(
            model=self.config.openrouter_model_name,
            messages=messages.to_list(),
            tools=tools,
            temperature=self.config.openrouter_temperature,
            top_p=self.config.openrouter_top_p,
            max_tokens=max_tokens,
            stream=False
        )

        return (
            completion.choices[0].message.content,
            completion.choices[0].message.tool_calls or [],
            completion.usage,
            completion.id,
        )