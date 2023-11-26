import asyncio
import time
from typing import AsyncGenerator

from langchain.agents import initialize_agent, AgentType, Agent
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.prompt import DEFAULT_TEMPLATE
from langchain.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from contextqa import settings
from contextqa.agents.tools import searcher
from contextqa.models.schemas import LLMQueryRequest
from contextqa.utils import memory, prompts


_MESSAGES = [
    SystemMessagePromptTemplate.from_template(
        """You are a helpful assistant called ContextQA that answer user inputs. You emphasize your name in every greeting.

    
    
    Example: Hello, I am ContextQA, how can I help you?
    """
    ),
    HumanMessagePromptTemplate.from_template("Hi"),
    AIMessagePromptTemplate.from_template("Hello, I am your assitant ContextQA, how may I help you?"),
    SystemMessagePromptTemplate.from_template(DEFAULT_TEMPLATE),
]


def get_llm_assistant(internet_access: bool) -> tuple[ConversationChain | Agent, AsyncIteratorCallbackHandler]:
    """Return certain LLM assistant based on the system configuration

    Parameters
    ----------
    internet_access : bool
        flag indicating whether an assistant with internet access was requested

    Returns
    -------
    ConversationChain | Agent
    """
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(temperature=0, streaming=True, callbacks=[callback])

    if internet_access:
        return (
            initialize_agent(
                [searcher],
                llm=llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                memory=memory.Redis("default", internet_access=True),
                verbose=settings.debug,
                agent_kwargs={"prefix": prompts.PREFIX},
                handle_parsing_errors=True,
            ),
            callback,
        )
    prompt = ChatPromptTemplate.from_messages(_MESSAGES)
    return ConversationChain(llm=llm, prompt=prompt, memory=memory.Redis("default"), verbose=settings.debug), callback


async def qa_service(params: LLMQueryRequest) -> AsyncGenerator:
    """Chat with the llm

    Parameters
    ----------
    params : LLMQueryRequest
        request body parameters

    Returns
    -------
    AsyncGenerator
    """

    assistant, callback = get_llm_assistant(params.internet_access)
    task = asyncio.create_task(assistant.arun(input=params.message))
    try:
        async for token in callback.aiter():
            yield token
            time.sleep(0.1)
    finally:
        callback.done.set()
    await task
