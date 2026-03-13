import os
from unittest.mock import patch

from app_ai.domain.entity.ai_message import AiMessage
from app_ai.infrastructure.llm.langchain_deepseek_adapter import LangChainDeepSeekAdapter


def test_adapter_gracefully_handles_missing_langchain_dependency():
    missing_dependency = ModuleNotFoundError("No module named 'langchain_openai'")
    missing_dependency.name = "langchain_openai"

    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=False):
        with patch.object(
            LangChainDeepSeekAdapter,
            "_load_langchain_dependencies",
            side_effect=missing_dependency,
        ):
            adapter = LangChainDeepSeekAdapter()

    messages = [AiMessage(role="user", content="Hello")]

    assert adapter.llm is None
    assert "langchain_openai" in adapter.chat(messages, "system prompt")
    assert list(adapter.stream_chat(messages, "system prompt")) == [
        "Error: Optional AI dependency 'langchain_openai' is not installed."
    ]
