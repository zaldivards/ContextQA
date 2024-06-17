import json
from typing import Literal

from langchain.memory import (
    ConversationBufferWindowMemory,
    RedisChatMessageHistory,
    ChatMessageHistory,
)
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict

from contextqa.models import ExtraSettings
from contextqa.utils.settings import get_or_set


_PROMPT_KEYS = {
    "default": {"input_key": "input", "memory_key": "history"},
    "defaultv2": {"input_key": "input", "memory_key": "chat_history"},
    "context": {"input_key": "question", "memory_key": "chat_history", "output_key": "answer"},
}

_LOCAL_MEMORY = ChatMessageHistory()


class LimitedRedisMemory(RedisChatMessageHistory):
    """RedisChatMessageHistory with a limited offset"""

    def __init__(self, session_id: str, url: str, messages_limit: int = 15):
        super().__init__(session_id, url)
        self.messages_limit = messages_limit

    @property
    def messages(self) -> list[BaseMessage]:  # type: ignore
        """Retrieve the messages from Redis"""
        _items = self.redis_client.lrange(self.key, 0, self.messages_limit)
        items = [json.loads(m.decode("utf-8")) for m in _items[::-1]]
        messages = messages_from_dict(items)
        return messages


def _prompt_keys(kind: str, internet_access: bool = False) -> dict[str, str]:
    if internet_access:
        return _PROMPT_KEYS["defaultv2"]
    return _PROMPT_KEYS[kind]


def _requires_raw(session: str, internet_access: bool) -> bool:
    return session != "default" or internet_access


def runnable_memory(
    session: Literal["default", "context"] = "default",
    internet_access: bool = False,
    buffer: bool = False,
) -> BaseChatMessageHistory | ConversationBufferWindowMemory:
    """Function to retrieve the appropriate chat message history based on the session type and existing memory settings

    Parameters
    ----------
    session : Literal["default", "context"], optional
        The type of session for which the chat message history is needed, by default "default"
    internet_access : bool, optional
        Wheter or not configure the chat message history for assistants with internet access
    buffer : bool, optional
        Whether to return a regular or buffered cgat history, by default False

    Returns
    -------
    BaseChatMessageHistory | ConversationBufferWindowMemory
    """
    memory_settings: ExtraSettings = get_or_set("extra")
    if memory_settings.memory.kind == "Local":
        _LOCAL_MEMORY.messages = _LOCAL_MEMORY.messages[-15:]
        chat_history = _LOCAL_MEMORY
    else:
        if buffer:
            chat_history = RedisChatMessageHistory(session_id=session, url=memory_settings.memory.url)
        else:
            chat_history = LimitedRedisMemory(session_id=session, url=memory_settings.memory.url)
    if not buffer:
        return chat_history
    return ConversationBufferWindowMemory(
        chat_memory=chat_history,
        max_token_limit=1000,
        k=5,
        return_messages=_requires_raw(session, internet_access),
        **_prompt_keys(session, internet_access),
    )
