import json
from typing import Literal

from langchain_openai import OpenAI
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory, RedisChatMessageHistory
from langchain.schema import BaseMemory
from langchain_core.messages import BaseMessage, messages_from_dict

from contextqa import settings

_PROMPT_KEYS = {
    "default": {"input_key": "input", "memory_key": "history"},
    "defaultv2": {"input_key": "input", "memory_key": "chat_history"},
    "context": {"input_key": "question", "memory_key": "chat_history", "output_key": "answer"},
}


class LimitedRedisMemory(RedisChatMessageHistory):
    """RedisChatMessageHistory with a limited offset"""

    def __init__(self, session_id: str, url: str, messages_limit: int = 10):
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


def _redis(
    session: Literal["default", "context"] = "default", internet_access: bool = False, buffer: bool = False
) -> RedisChatMessageHistory | ConversationBufferWindowMemory:
    history_db = LimitedRedisMemory(session_id=session, url=settings.redis_url)
    if not buffer:
        return history_db
    return ConversationBufferWindowMemory(
        chat_memory=RedisChatMessageHistory(session_id=session, url=settings.redis_url),
        max_token_limit=1000,
        k=5,
        return_messages=_requires_raw(session, internet_access),
        **_prompt_keys(session, internet_access),
    )


def _redis_with_summary(session: Literal["default", "context"] = "default") -> RedisChatMessageHistory:
    history_db = LimitedRedisMemory(session_id=session, url=settings.redis_url)
    memory = ConversationSummaryBufferMemory(
        llm=OpenAI(temperature=0),
        chat_memory=history_db,
        return_messages=_requires_raw(session, False),
        max_token_limit=1000,
        **_prompt_keys(session),
    )
    return memory


RedisSummaryMemory = _redis_with_summary
Redis = _redis
