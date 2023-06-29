from langchain import ConversationChain
from langchain.chains.conversation.prompt import DEFAULT_TEMPLATE
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from contextqa import models, settings
from contextqa.utils import memory


_MESSAGES = [
    SystemMessagePromptTemplate.from_template(
        """You are helpful assistant called ContextQA that answer user inputs. You emphasize your name in every greeting.
    
    
    Example: Hello, I am ContextQA, how can I help you?
    """
    ),
    HumanMessagePromptTemplate.from_template("Hi"),
    AIMessagePromptTemplate.from_template("Hello, I am your assitant ContextQA, how may I help you?"),
    SystemMessagePromptTemplate.from_template(DEFAULT_TEMPLATE),
]


def qa_service(message: str) -> models.LLMResult:
    """Chat with the llm

    Parameters
    ----------
    message : str
        User message

    Returns
    -------
    models.LLMResult
        LLM response
    """
    llm = ChatOpenAI(temperature=0)
    prompt = ChatPromptTemplate.from_messages(_MESSAGES)
    chain = ConversationChain(llm=llm, prompt=prompt, memory=memory.Redis("default"), verbose=settings().debug)
    return models.LLMResult(response=chain.run(input=message))
