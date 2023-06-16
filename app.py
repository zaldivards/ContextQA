import sys

from dotenv import load_dotenv
from langchain import OpenAI, VectorDBQA
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SKLearnVectorStore

load_dotenv()


# pylint: disable=C0413
from agents.general import get_people_information
from external.twitter import get_user_tweets
from parsers.output import Summary, summary_parser


def query_document(file_: str):
    loader = TextLoader(file_, encoding="utf-8")
    document = loader.load()
    splitter = CharacterTextSplitter(separator=".", chunk_size=100, chunk_overlap=0)
    texts = splitter.split_documents(document)
    embeddings_util = OpenAIEmbeddings()
    store = SKLearnVectorStore.from_documents(texts, embeddings_util)
    finder = VectorDBQA.from_chain_type(OpenAI(), vectorstore=store)
    result = finder({"query": "what is langchain, give me a summary in 5 words"})
    print(result)


def seach_user_info(name: str) -> Summary:
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
    print(response)
    return summary_parser.parse(response)


if __name__ == "__main__":
    try:
        name_ = sys.argv[1]
        assert len(name_) > 3
    except (IndexError, AssertionError):
        print("Please provide a valid name")
        sys.exit(1)
    # seach_user_info(name_)
    query_document(name_)
