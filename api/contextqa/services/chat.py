from typing import AsyncGenerator

from langchain import hub
from langchain.agents import AgentExecutor, create_json_chat_agent
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables.history import RunnableWithMessageHistory

from contextqa.agents.tools import searcher
from contextqa.models.schemas import LLMQueryRequest
from contextqa.utils import memory
from contextqa.utils.streaming import consumer_producer


_MESSAGES = [
    (
        "system",
        "You are a helpful assistant called ContextQA that answers user inputs and questions",
    ),
    (
        "system",
        "Use markdown to pretty format texts and code blocks, use full language names",
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
]


def get_llm_assistant(internet_access: bool, llm: BaseChatModel) -> RunnableWithMessageHistory:
    """Return certain LLM assistant based on the system configuration

    Parameters
    ----------
    internet_access : bool
        flag indicating whether an assistant with internet access was requested
    llm : BaseChatModel

    Returns
    -------
    RunnableWithMessageHistory
    """
    tools = [searcher]
    if internet_access:
        prompt = hub.pull("hwchase17/react-chat-json")
        agent = create_json_chat_agent(
            llm=llm,
            prompt=prompt,
            tools=tools,
        )
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return RunnableWithMessageHistory(
            agent_executor,
            memory.runnable_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
    prompt = ChatPromptTemplate.from_messages(_MESSAGES)
    chain = prompt | llm
    chain_with_history = RunnableWithMessageHistory(
        chain, memory.runnable_memory, input_messages_key="input", history_messages_key="history"
    )
    return chain_with_history


def invoke_model(params: LLMQueryRequest, llm: BaseChatModel) -> AsyncGenerator:
    """Chat with the llm

    Parameters
    ----------
    params : LLMQueryRequest
        request body parameters
    llm : BaseChatModel

    Returns
    -------
    AsyncGenerator
    """

    assistant = get_llm_assistant(params.internet_access, llm)
    return consumer_producer(
        assistant.astream_events(
            {"input": params.message}, config={"configurable": {"session_id": "default"}}, version="v1"
        ),
        params.internet_access,
    )
