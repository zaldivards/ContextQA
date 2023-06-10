from langchain import PromptTemplate
from langchain.agents import initialize_agent, load_tools
from langchain.chat_models import ChatOpenAI


def get_people_information(name: str):
    template = """
    Given the full name {name} I want you to search their linkedin data in google. Do it just once
    """
    llm = ChatOpenAI()
    tools = load_tools(["serpapi"], llm=llm)
    agent = initialize_agent(tools, llm=llm, verbose=True)

    prompt_template = PromptTemplate(template=template, input_variables=["name"])

    return agent.run(prompt_template.format_prompt(name=name))
