from tempfile import NamedTemporaryFile
from typing import BinaryIO

import pinecone
from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone, SKLearnVectorStore

from retriever import models, settings

settings_ = settings()

_VECTORSTORE = {
    "sklearn": models.VectorStoreParams(clazz=SKLearnVectorStore),
    "pinecone": models.VectorStoreParams(clazz=Pinecone, kwargs={"index_name": settings_.pinecone_index}),
}


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
    finder = RetrievalQA.from_chain_type(OpenAI(), retriever=store.as_retriever())
    result = finder.run(params.query)
    return models.VectorScanResult(response=result)


def document_scan(params: models.LLMQueryDocumentRequestBody, document: BinaryIO) -> models.VectorScanResult:
    """Query the llm providing the best context found in the given pdf

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
    processor_params = _VECTORSTORE[params.similarity_processor]
    store = processor_params.clazz.from_documents(texts, embeddings_util, **processor_params.kwargs)
    finder = RetrievalQA.from_chain_type(OpenAI(), retriever=store.as_retriever())
    result = finder.run(params.query)
    return models.VectorScanResult(response=result)


def pdf_scan(params: models.LLMQueryDocumentRequestBody, document: BinaryIO) -> models.VectorScanResult:
    """Query the bot about the pdf content

    Parameters
    ----------
    params : models.LLMQueryDocumentRequestBody
        params from the api request
    document : BinaryIO
        pdf document from the api request

    Returns
    -------
    models.VectorScanResult
        result found by the llm given the best context
    """
    # the temp file is needed to properly load the pdf file using the `PyPDFLoader` class
    if params.similarity_processor == models.SimilarityProcessor.PINECONE:
        pinecone.init(api_key=settings_.pinecone_token, environment=settings_.pinecone_environment_region)
    with NamedTemporaryFile(mode="wb") as temp:
        temp.write(document.read())
        loader = PyPDFLoader(temp.name)
        documents = loader.load()
    splitter = CharacterTextSplitter(separator=params.separator, chunk_size=params.chunk_size, chunk_overlap=0)
    texts = splitter.split_documents(documents)
    embeddings_util = OpenAIEmbeddings()
    processor_params = _VECTORSTORE[params.similarity_processor]
    store = processor_params.clazz.from_documents(texts, embeddings_util, **processor_params.kwargs)
    finder = RetrievalQA.from_chain_type(OpenAI(), retriever=store.as_retriever())
    result = finder.run(params.query)
    return models.VectorScanResult(response=result)
