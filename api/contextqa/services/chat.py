from contextqa import models
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

_SYSTEM_MESSAGE = SystemMessagePromptTemplate.from_template(
    """You are helpful assistant called ContextQA that answer user inputs. You emphasize your name in every greeting.
    
    
    Example: Hello, I am ContextQA, how can I help you?
    """
)
_HUMAN_MESSAGE_EXAMPLE = HumanMessagePromptTemplate.from_template("Hi")
_AI_MESSAGE_EXAMPLE = AIMessagePromptTemplate.from_template("Hello, I am your assitant ContextQA, how may I help you?")


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
    human_template = "{input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    prompt = ChatPromptTemplate.from_messages(
        [_SYSTEM_MESSAGE, _HUMAN_MESSAGE_EXAMPLE, _AI_MESSAGE_EXAMPLE, human_message_prompt]
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return models.LLMResult(response=chain.run(input=message))
