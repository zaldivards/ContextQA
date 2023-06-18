from typing import BinaryIO

from langchain import OpenAI, VectorDBQA
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone, SKLearnVectorStore

from retriever import models

_VECTORSTORE = {"local": SKLearnVectorStore, "pinecone": Pinecone}


def simple_scan(params: models.LLMQueryTextRequestBody) -> models.VectorScanResult:
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


def document_scan(params: models.LLMQueryDocumentRequestBody, document: BinaryIO) -> models.VectorScanResult:
    """Query the llm providing the best context found in the given document

    Parameters
    ----------
    params : models.LLMQueryDocumentRequestBody
        params from the api request
    document : BinaryIO
        document from the api request

    Returns
    -------
    models.VectorScanResult
        result found by the llm given the best context
    """
    splitter = CharacterTextSplitter(separator=params.separator, chunk_size=params.chunk_size, chunk_overlap=0)
    texts = splitter.split_documents([Document(page_content=document.read())])
    embeddings_util = OpenAIEmbeddings()
    store = _VECTORSTORE[params.similarity_processor].from_documents(texts, embeddings_util)
    finder = VectorDBQA.from_chain_type(OpenAI(), vectorstore=store)
    result = finder({"query": params.query})
    return models.VectorScanResult(**result)
