from typing import AsyncGenerator

from langchain.agents import initialize_agent, AgentType, Agent
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.callbacks.streaming_aiter_final_only import AsyncFinalIteratorCallbackHandler
from langchain.chains import ConversationChain
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder

from contextqa import settings
from contextqa.agents.tools import searcher
from contextqa.models import PartialModelData
from contextqa.models.schemas import LLMQueryRequest
from contextqa.utils import memory, prompts
from contextqa.utils.streaming import consumer_producer


from langchain_core.runnables.history import RunnableWithMessageHistory

_MESSAGES = [
    SystemMessagePromptTemplate.from_template(
        "You are a helpful assistant called ContextQA that answers user inputs and questions"
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
]


def get_llm_assistant(
    internet_access: bool, partial_model_data: PartialModelData
) -> tuple[ConversationChain | Agent, AsyncCallbackHandler]:
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
        callback = partial_model_data.callback or AsyncFinalIteratorCallbackHandler(
            answer_prefix_tokens=["Final", "Answer", '",', "", '"', "action", "_input", '":', '"']
        )
        llm = partial_model_data.partial_model(streaming=True, callbacks=[callback])
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
    llm = partial_model_data.partial_model(streaming=True)
    prompt = ChatPromptTemplate.from_messages(_MESSAGES)

    chain = prompt | llm
    chain_with_history = RunnableWithMessageHistory(
        chain, memory.Redis, input_messages_key="input", history_messages_key="history"
    )
    return chain_with_history


def qa_service(params: LLMQueryRequest, partial_model: PartialModelData) -> AsyncGenerator:
    """Chat with the llm

    Parameters
    ----------
    params : LLMQueryRequest
        request body parameters

    Returns
    -------
    AsyncGenerator
    """

    assistant = get_llm_assistant(params.internet_access, partial_model)
    return consumer_producer(
        assistant.astream({"input": params.message}, config={"configurable": {"session_id": "default"}})
    )
