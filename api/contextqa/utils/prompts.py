"""Custom Prompt templates"""

from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate

# part of this template was taken from langchain.chains.conversational_retrieval.prompts
TEMPLATE = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

If the final message aka the follow up input is a gratitude or goodbye message, that MUST be your final answer

Example 1:
Assistant: And that is today's wheather
Human: ok thank you
Standalone question: Thank you

Example 2:
Assistant: And that is today's wheather
Human: ok goodbye
Standalone question: Goodbye


Current conversation:
{chat_history}
Follow Up Input: {question}
Standalone question:"""

ANSWER_TEMPLATE = """Answer the question based only on the following context:
{context}

Question: {question}
"""

CONTEXTQA_RETRIEVAL_PROMPT = PromptTemplate.from_template(TEMPLATE)
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")
ANSWER_PROMPT = ChatPromptTemplate.from_template(ANSWER_TEMPLATE)
