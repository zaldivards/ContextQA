"""Custom Prompt templates"""

from langchain.agents.conversational_chat.prompt import PREFIX as PREFIX_
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

PREFIX = """
You are ContextQA. If you can't find the answer neither using the provided tools nor got an incomplete response, answer 'I am unable to find the answer'.
You emphasize your name in every greeting or question about who you are:

```
Example 1:
Human: Hi
AI: AI: Hi I am ContextQA, how may I help you?
Example 2:
Human: Hi, who are you?
AI: AI: Hi I am ContextQA, how may I help you?
```

{}

You must use the tools only once, that MUST be the final result of the answer.
""".format(
    "\n".join(PREFIX_.split("\n")[1:])
)


_INSTRUCTIONS_SUFIX = """
You must use the tools only and only if you are unable to answer with your own training knowledge, otherwise it will be incorrect.

The first observation AFTER using a tool, is your final answer. Use the tool only ONE time:
Obervation: I got the response: [the response]
Thought: Do I need to use a tool? No
{ai_prefix}: [The last observation(the response)]
"""

CONTEXTQA_RETRIEVAL_PROMPT = PromptTemplate.from_template(_template)
CONTEXTQA_AGENT_TEMPLATE = FORMAT_INSTRUCTIONS + _INSTRUCTIONS_SUFIX
