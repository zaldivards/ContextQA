"""Custom Prompt templates"""

from langchain.agents.conversational.prompt import FORMAT_INSTRUCTIONS
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


_COMMON_TEAMPLATE_SEGMENT = """You are helpful assistant called ContextQA that answer user inputs. You emphasize your
name in every greeting.

Example: 
Human: Hi
Assistant: Hello, I am ContextQA, how can I help you?

"""

CONTEXTQA_RETRIEVAL_PROMPT = PromptTemplate.from_template(_template)
CONTEXTQA_AGENT_TEMPLATE = _COMMON_TEAMPLATE_SEGMENT + FORMAT_INSTRUCTIONS
