from contextqa import settings
from langchain.llms import OpenAI
from langchain.memory import (
    CombinedMemory,
    ConversationBufferMemory,
    ConversationSummaryMemory,
    RedisChatMessageHistory,
)
from langchain.schema import BaseMemory

envs = settings()
history_db = RedisChatMessageHistory(session_id="default", url=envs.redis_url)


def _redis() -> BaseMemory:
    return ConversationBufferMemory(chat_memory=history_db)


def _redis_with_summary() -> BaseMemory:
    summary_memory = ConversationSummaryMemory(llm=OpenAI(temperature=0))
    redis_memory = ConversationBufferMemory(chat_memory=history_db, memory_key="chat_history")
    memories = CombinedMemory(memories=[summary_memory, redis_memory])
    return memories


Redis = _redis
RedisSummary = _redis_with_summary
