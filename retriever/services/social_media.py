from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from retriever.agents.general import get_people_information
from retriever.external.twitter import get_user_tweets
from retriever.parsers.models import Summary
from retriever.parsers.output import summary_parser


def seach_user_info(name: str) -> Summary:
    """Search linkedin and twitter data for a person

    Parameters
    ----------
    name : str
        person name

    Returns
    -------
    Summary
    """
    template = """
    Given the Linkedin information {linkedin_info} and Twitter information {twitter_info} about a person, I want you to create:

    1. A short summary with only 5 words
    2. Two interesting facts about the person
    3. two ice breakers to start a conversation with them
    \n
    {format_instructions}
    """
    linkedin_info = get_people_information(name, "LinkedIn")
    twitter_user = get_people_information(name, "Twitter")
    twitter_info = get_user_tweets(username=twitter_user, num_tweets=10)
    prompt_template = PromptTemplate(
        input_variables=["linkedin_info", "twitter_info"],
        template=template,
        partial_variables={"format_instructions": summary_parser.get_format_instructions()},
    )
    llm = ChatOpenAI(temperature=0)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run(linkedin_info=linkedin_info, twitter_info=twitter_info)
    return summary_parser.parse(response)
