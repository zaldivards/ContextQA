import os

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from agents.general import get_people_information

# from external.linkedin import get_linkedin_profile

os.environ["OPENAI_API_KEY"] = "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"

template = """
Given the following information about a person:

{information}

I want you to create:

1. A short summary with only 5 words
2. Two interesting facts about the person
"""

prompt_template = PromptTemplate(input_variables=["information"], template=template)
llm = ChatOpenAI(temperature=0)
chain = LLMChain(llm=llm, prompt=prompt_template)

# information = input("\n\nPaste the person's information\n\n")

print(chain.run(information=get_people_information("Christian Zaldivar Azumo")))
print("\n\n")
