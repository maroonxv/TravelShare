import os
from importlib import import_module
from typing import Generator, List

from app_ai.domain.demand_interface.i_llm_client import ILlmClient
from app_ai.domain.entity.ai_message import AiMessage


class LangChainDeepSeekAdapter(ILlmClient):
    def __init__(self):
        self.llm = None
        self._message_classes = None
        self._unavailable_reason = None

        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        if not api_key:
            self._set_unavailable_reason("DEEPSEEK_API_KEY not found.")
            return

        try:
            chat_openai_cls, message_classes = self._load_langchain_dependencies()
            self._message_classes = message_classes
            self.llm = chat_openai_cls(
                model="deepseek-chat",
                api_key=api_key,
                base_url=base_url,
                streaming=True,
            )
        except ModuleNotFoundError as exc:
            missing_module = exc.name or "langchain_openai"
            self._set_unavailable_reason(
                f"Optional AI dependency '{missing_module}' is not installed."
            )
        except Exception as exc:
            self._set_unavailable_reason(f"Failed to initialize LLM client: {exc}")

    @staticmethod
    def _load_langchain_dependencies():
        chat_openai_module = import_module("langchain_openai")
        messages_module = import_module("langchain_core.messages")
        return chat_openai_module.ChatOpenAI, (
            messages_module.SystemMessage,
            messages_module.HumanMessage,
            messages_module.AIMessage,
        )

    def _set_unavailable_reason(self, reason: str) -> None:
        self._unavailable_reason = reason
        print(f"Warning: {reason}")

    def _convert_messages(self, messages: List[AiMessage], system_prompt: str):
        if not self._message_classes:
            raise RuntimeError(self._unavailable_reason or "LLM message classes are unavailable.")

        system_message_cls, human_message_cls, ai_message_cls = self._message_classes
        lc_messages = [system_message_cls(content=system_prompt)]

        for msg in messages:
            if msg.role == "user":
                lc_messages.append(human_message_cls(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(ai_message_cls(content=msg.content))

        return lc_messages

    def _get_unavailable_error(self) -> str:
        return self._unavailable_reason or "LLM not configured."

    def stream_chat(self, messages: List[AiMessage], system_prompt: str) -> Generator[str, None, None]:
        if not self.llm:
            yield f"Error: {self._get_unavailable_error()}"
            return

        lc_messages = self._convert_messages(messages, system_prompt)

        try:
            for chunk in self.llm.stream(lc_messages):
                if chunk.content:
                    yield chunk.content
        except Exception as exc:
            yield f"Error calling LLM: {exc}"

    def chat(self, messages: List[AiMessage], system_prompt: str) -> str:
        if not self.llm:
            return f"Error: {self._get_unavailable_error()}"

        try:
            lc_messages = self._convert_messages(messages, system_prompt)
            response = self.llm.invoke(lc_messages)
            return response.content
        except Exception as exc:
            return f"Error calling LLM: {exc}"
