import sys

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()
# pylint: disable=C0413
from agents.general import get_people_information
from external.twitter import get_user_tweets


def main(name: str) -> str:
    template = """
    Given the Linkedin information {linkedin_info} and Twitter information {twitter_info} about a person, I want you to create:

    1. A short summary with only 5 words
    2. Two interesting facts about the person
    3. two ice breakers to start a conversation with them
    """
    linkedin_info = get_people_information(name, "LinkedIn")
    twitter_user = get_people_information(name, "Twitter")
    twitter_info = get_user_tweets(username=twitter_user, num_tweets=10)
    prompt_template = PromptTemplate(input_variables=["linkedin_info", "twitter_info"], template=template)
    llm = ChatOpenAI(temperature=0)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run(linkedin_info=linkedin_info, twitter_info=twitter_info)
    return response


if __name__ == "__main__":
    try:
        name_ = sys.argv[1]
        assert len(name_) > 3
    except (IndexError, AssertionError):
        print("Please provide a valid name")
        sys.exit(1)
    main(name_)
