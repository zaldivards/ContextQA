"""Custom Prompt templates"""

from langchain.prompts import PromptTemplate

# part of this template was taken from langchain.chains.conversational_retrieval.prompts
_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

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


CONTEXTQA_RETRIEVAL_PROMPT = PromptTemplate.from_template(_template)
