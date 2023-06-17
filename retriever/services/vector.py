from langchain import OpenAI, VectorDBQA
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SKLearnVectorStore

from retriever import models


def simple_scan(params: models.LLMQueryRequestBody) -> models.VectorScanResult:
    """Query the llm providing the best context found by using the KNearestNeighbors model

    Parameters
    ----------
    params : models.LLMQueryRequestBody
        params from the api request

    Returns
    -------
    models.VectorScanResult
        result found by the llm given the best context
    """
    splitter = CharacterTextSplitter(separator=params.separator, chunk_size=params.chunk_size, chunk_overlap=0)
    texts = splitter.split_documents([Document(page_content=params.content)])
    embeddings_util = OpenAIEmbeddings()
    store = SKLearnVectorStore.from_documents(texts, embeddings_util)
    finder = VectorDBQA.from_chain_type(OpenAI(), vectorstore=store)
    result = finder({"query": params.query})
    return models.VectorScanResult(**result)
