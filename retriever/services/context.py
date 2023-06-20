from functools import wraps
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO, Callable

from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import SKLearnVectorStore

from retriever import models

LOCAL_STORE_HOME = Path.home() / "embeddings"
LOADERS = {"pdf": PyPDFLoader, "txt": TextLoader}


def get_loader(extension: str) -> BaseLoader:
    return LOADERS[extension]


def context_setter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        params: models.LLMRequestBodyBase = args[1]
        extension = Path(args[0]).suffix.removeprefix(".")
        with NamedTemporaryFile(mode="wb") as temp:
            temp.write(args[2].read())
            loader = get_loader(extension)(temp.name)
            documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=params.chunk_size, chunk_overlap=params.chunk_overlap, separators=["\n\n", "\n", "."]
        )
        texts = splitter.split_documents(documents)
        kwargs["documents"] = texts
        func(*args, **kwargs)

    return wrapper


# pylint: disable=W0613
@context_setter
def local_context(filename: str, params: models.LLMRequestBodyBase, document: BinaryIO, **kwargs):
    embeddings_util = OpenAIEmbeddings()
    store = SKLearnVectorStore.from_documents(
        kwargs["documents"], embeddings_util, persist_path=str(LOCAL_STORE_HOME / filename), serializer="parquet"
    )
    store.persist()


def get_setter(processor: models.SimilarityProcessor) -> Callable[[str, models.LLMRequestBodyBase, BinaryIO], None]:
    match processor:
        case models.SimilarityProcessor.LOCAL:
            return local_context
