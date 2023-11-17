from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO, Optional

import pinecone
from chromadb import PersistentClient
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import PyMuPDFLoader, TextLoader
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pinecone import Pinecone
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores.base import VectorStore

from contextqa import get_logger, settings
from contextqa.parsers.models import Source, LLMResult, LLMRequestBodyBase, QAResult, SimilarityProcessor
from contextqa.utils import memory, prompts


LOGGER = get_logger()
LOADERS = {".pdf": PyMuPDFLoader, ".txt": TextLoader}

chroma_client = PersistentClient(path=str(settings.local_vectordb_home))


class VectorStoreConnectionError(Exception):
    """This exception is raised when a connection could not be established or credentials are invalid"""


def get_loader(extension: str) -> BaseLoader:
    return LOADERS[extension]


def prepare_sources(sources: list[Document]) -> list[Source]:
    result = []
    for source in sources:
        name = source.metadata.pop("source")
        extras = {}
        if page := source.metadata.get("page"):
            extras.update(page=page)
        if row := source.metadata.get("row"):
            extras.update(row=row)
        result.append(Source(name=name, extras=extras))
    return result


class LLMContextManager(ABC):
    """Base llm manager"""

    def load_and_preprocess(self, filename: str, params: LLMRequestBodyBase, file_: BinaryIO) -> list[Document]:
        """Load and preprocess the file content

        Parameters
        ----------
        filename : str
            Name of the file to load
        params : LLMRequestBodyBase
            api parameters
        file_ : BinaryIO
            file for which to save context

        Returns
        -------
        List[Document]
            splitted document content as documents
        """
        extension = Path(filename).suffix
        try:
            if extension == ".pdf":
                path = settings.media_home / filename
                file_writer = open(path, mode="wb")
            else:
                file_writer = NamedTemporaryFile(mode="wb", suffix=f":::sep:::{filename}")
                path = file_writer.name
            file_writer.write(file_.read())
            loader: BaseLoader = get_loader(extension)(str(path))
            documents = loader.load()
        finally:
            file_writer.close()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=params.chunk_size, chunk_overlap=params.chunk_overlap, separators=["\n\n", "\n", "."]
        )
        texts = splitter.split_documents(documents)
        return texts

    @abstractmethod
    def persist(self, filename: str, params: LLMRequestBodyBase, file_: BinaryIO) -> LLMResult:
        """Persist the embedded documents

        Parameters
        ----------
        filename : str
            Name of the file to load
        params : LLMRequestBodyBase
            api parameters
        file_ : BinaryIO
            file for which to save context

        Returns
        -------
        VectorScanResult
            process status
        """
        raise NotImplementedError

    @abstractmethod
    def context_object(self, filename: Optional[str]) -> VectorStore:
        """Prepare the processor object. This method needs specific implementations because most of the VectorStores
        are initialized with different parameters

        Parameters
        ----------
        filename : Optional[str]
            Name of the file. If provided, it will be used as the identifier to load the existing context(embeddings).

        Returns
        -------
        VectorStore
            An initialized instance of a VectorStore implementation
        """
        raise NotImplementedError

    def load_and_respond(self, question: str, filename: Optional[str] = None) -> QAResult:
        """Load the context and answer the question

        Parameters
        ----------
        question : str
            The question to answer
        filename : Optional[str], optional
            Name of the file. If provided, it will be used as the identifier to load the existing context(embeddings),
            by default None

        Returns
        -------
        QAResult
            The final response of the LLM
        """
        context_util = self.context_object(filename)
        llm = ChatOpenAI(verbose=True, temperature=0)
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=context_util.as_retriever(),
            memory=memory.Redis(session="context"),
            condense_question_prompt=prompts.CONTEXTQA_RETRIEVAL_PROMPT,
            verbose=settings.debug,
            return_source_documents=True,
        )

        result = qa_chain(question)
        return QAResult(response=result["answer"], sources=prepare_sources(result["source_documents"]))


class LocalManager(LLMContextManager):
    """Local manager implementation. It uses `Chroma` as its processor and the context is persisted as a
    parquet file"""

    def persist(self, filename: str, params: LLMRequestBodyBase, file_: BinaryIO) -> LLMResult:
        documents = self.load_and_preprocess(filename, params, file_)
        embeddings_util = OpenAIEmbeddings()
        processor = Chroma.from_documents(
            documents, embeddings_util, client=chroma_client, collection_name="contextqa-default"
        )
        processor.persist()
        return LLMResult(response="success")

    def context_object(self, filename: Optional[str] = None) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = Chroma(
            client=chroma_client,
            collection_name="contextqa-default",
            embedding_function=embeddings_util,
            persist_directory=str(settings.local_vectordb_home),
        )
        return processor


class PineconeManager(LLMContextManager):
    """Pinecone manager implementation. It uses `Pinecone` as its processor and vector store"""

    def persist(self, filename: str, params: LLMRequestBodyBase, file_: BinaryIO) -> LLMResult:
        try:
            LOGGER.info("Initializing Pinecone connection")
            pinecone.init(api_key=settings.pinecone_token, environment=settings.pinecone_environment_region)
        except Exception as ex:
            raise VectorStoreConnectionError from ex
        documents = self.load_and_preprocess(filename, params, file_)
        embeddings_util = OpenAIEmbeddings()
        try:
            Pinecone.from_documents(
                documents, embeddings_util, index_name=settings.pinecone_index, namespace=Path(filename).stem
            )
        except Exception as ex:
            raise VectorStoreConnectionError from ex
        return LLMResult(response="success")

    def context_object(self, filename: Optional[str] = None) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = Pinecone.from_existing_index(
            index_name=settings.pinecone_index, embedding=embeddings_util, namespace=Path(filename).stem
        )
        return processor


def get_setter(processor: SimilarityProcessor) -> LLMContextManager:
    """LLMContextManager factory function

    Parameters
    ----------
    processor : SimilarityProcessor
        Manager identifier

    Returns
    -------
    LLMContextManager
        Specific LLMContextManager implementation
    """
    match processor:
        case SimilarityProcessor.LOCAL:
            return LocalManager()
        case SimilarityProcessor.PINECONE:
            return PineconeManager()
