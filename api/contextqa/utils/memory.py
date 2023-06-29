from contextqa import settings
from langchain.llms import OpenAI
from langchain.memory import (
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
    ConversationSummaryMemory,
    RedisChatMessageHistory,
)
from langchain.schema import BaseMemory

envs = settings()
history_db = RedisChatMessageHistory(session_id="default", url=envs.redis_url)


def _redis() -> BaseMemory:
    return ConversationBufferWindowMemory(
        chat_memory=history_db,
        input_key="question",
        memory_key="chat_history",
        max_token_limit=1000,
        k=5,
        return_messages=True,
    )


def _summary_memory() -> BaseMemory:
    return ConversationSummaryMemory(llm=OpenAI(temperature=0), input_key="question")


def _redis_with_summary() -> BaseMemory:
    memory = ConversationSummaryBufferMemory(
        llm=OpenAI(temperature=0),
        input_key="question",
        memory_key="chat_history",
        chat_memory=history_db,
        return_messages=True,
        max_token_limit=1000,
    )
    return memory


RedisSummaryMemory = _redis_with_summary
Redis = _redis
