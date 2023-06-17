from langchain import OpenAI, VectorDBQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SKLearnVectorStore

from retriever.parsers.models import VectorScanResult


def simple_scan(content: str, separator: str, chunk_size: int = 100) -> VectorScanResult:
    """Query the llm providing the best context found by using the KNearestNeighbors model

    Parameters
    ----------
    content : str
        The whole content of the "context"
    separator : str
        Separator to use for the text splitting
    chunk_size : int, optional
        size of each splitted chunk, by default 100

    Returns
    -------
    VectorScanResult
    """
    splitter = CharacterTextSplitter(separator=separator, chunk_size=chunk_size, chunk_overlap=0)
    texts = splitter.split_documents(content)
    embeddings_util = OpenAIEmbeddings()
    store = SKLearnVectorStore.from_documents(texts, embeddings_util)
    finder = VectorDBQA.from_chain_type(OpenAI(), vectorstore=store)
    result = finder({"query": "what is langchain, give me a summary in 10 words"})
    return VectorScanResult(**result)
