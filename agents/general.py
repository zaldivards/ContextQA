from typing import Literal

from langchain import PromptTemplate
from langchain.agents import initialize_agent, load_tools
from langchain.chat_models import ChatOpenAI


def get_people_information(name: str, social_media: Literal["LinkedIn", "Twitter"]):
    if social_media == "LinkedIn":
        template = """
        Given the name {name} I want you to search their linkedin data
        """
    elif social_media == "Twitter":
        template = """
        Given the name {name} I want you to find a link to their Twitter profile page and extract from it their username.
        Do it just once and only once!
        
        Your final answer will be only the person's username. 
        As an example, @username is a well-formatted answer. The answer "My final answer is @username" is not well-formatted. 
        """
    llm = ChatOpenAI()
    tools = load_tools(["serpapi"], llm=llm)
    agent = initialize_agent(tools, llm=llm, verbose=True)

    prompt_template = PromptTemplate(template=template, input_variables=["name"])

    return agent.run(prompt_template.format_prompt(name=name))
