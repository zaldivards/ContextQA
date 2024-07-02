"""Custom Prompt templates"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

_CONTEXTUALIZE_Q_SYSTEM_PROMPT = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
STANDALONE_QUESTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _CONTEXTUALIZE_Q_SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

_QA_SYSTEM_PROMPT = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know.\

Answer using markdown syntax

{context}"""
QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _QA_SYSTEM_PROMPT),
        ("human", "{input}"),
    ]
)
