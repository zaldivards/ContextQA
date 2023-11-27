from typing import AsyncGenerator

from langchain.agents import initialize_agent, AgentType, Agent
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.callbacks.streaming_aiter_final_only import AsyncFinalIteratorCallbackHandler
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
from contextqa.agents.tools import searcher
from contextqa.utils.streaming import stream


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


def get_llm_assistant(internet_access: bool) -> tuple[ConversationChain | Agent, AsyncCallbackHandler]:
    """Return certain LLM assistant based on the system configuration

    Parameters
    ----------
    internet_access : bool
        flag indicating whether an assistant with internet access was requested

    Returns
    -------
    ConversationChain | Agent, AsyncCallbackHandler
    """

    if internet_access:
        callback = AsyncFinalIteratorCallbackHandler(
            answer_prefix_tokens=["Final", "Answer", '",', "", '"', "action", "_input", '":', '"']
        )
        llm = ChatOpenAI(temperature=0, streaming=True, callbacks=[callback])
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
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(temperature=0, streaming=True, callbacks=[callback])
    prompt = ChatPromptTemplate.from_messages(_MESSAGES)
    return ConversationChain(llm=llm, prompt=prompt, memory=memory.Redis("default"), verbose=settings.debug), callback


def qa_service(params: LLMQueryRequest) -> AsyncGenerator:
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
    return stream(assistant.arun(input=params.message), callback)
