from typing import Literal

from langchain.llms import OpenAI
from langchain.memory import (
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
    RedisChatMessageHistory,
)
from langchain.schema import BaseMemory

from contextqa import settings

envs = settings()
_PROMPT_KEYS = {
    "default": {"input_key": "input", "memory_key": "chat_history" if envs.enable_internet_access else "history"},
    "context": {"input_key": "question", "memory_key": "chat_history"},
}


def _requires_raw(session: str) -> bool:
    return session != "default" or envs.enable_internet_access


def _redis(session: Literal["default", "context"] = "default") -> BaseMemory:
    history_db = RedisChatMessageHistory(session_id=session, url=envs.redis_url)
    return ConversationBufferWindowMemory(
        chat_memory=history_db,
        max_token_limit=1000,
        k=5,
        return_messages=_requires_raw(session),
        **_PROMPT_KEYS[session]
    )


def _redis_with_summary(session: Literal["default", "context"] = "default") -> BaseMemory:
    history_db = RedisChatMessageHistory(session_id=session, url=envs.redis_url)
    memory = ConversationSummaryBufferMemory(
        llm=OpenAI(temperature=0),
        chat_memory=history_db,
        return_messages=_requires_raw(session),
        max_token_limit=1000,
        **_PROMPT_KEYS[session]
    )
    return memory


RedisSummaryMemory = _redis_with_summary
Redis = _redis
