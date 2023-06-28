"""Custom Prompt templates"""

from langchain.chains.conversational_retrieval.prompts import (
    CONDENSE_QUESTION_PROMPT as _CONDENSE_QUESTION_PROMPT,
)
from langchain.prompts import PromptTemplate

# part of this template was taken from langchain.chains.conversational_retrieval.prompts
_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Summary of conversation:
{history}
Current conversation:
{chat_history}
Follow Up Input: {question}
Standalone question:"""


CONTEXTQA_SUMMARY_TEMPLATE = PromptTemplate.from_template(_template)
CONTEXTQA_TEMPLATE = _CONDENSE_QUESTION_PROMPT
