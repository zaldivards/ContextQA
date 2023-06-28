from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO

import pinecone
from contextqa import models, settings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone, SKLearnVectorStore
from langchain.vectorstores.base import VectorStore

LOCAL_STORE_HOME = Path("/var") / "embeddings"
LOADERS = {"pdf": PyPDFLoader, "txt": TextLoader}


class VectorStoreConnectionError(Exception):
    """This exception is raised when a connection could not be established or credentials are invalid"""


def get_loader(extension: str) -> BaseLoader:
    return LOADERS[extension]


class LLMContextManager(ABC):
    """Base llm manager"""

    envs = settings()

    def load_and_preprocess(self, filename: str, params: models.LLMRequestBodyBase, file_: BinaryIO) -> list[Document]:
        """Load and preprocess the file content

        Parameters
        ----------
        filename : str
            Name of the file to load
        params : models.LLMRequestBodyBase
            api parameters
        file_ : BinaryIO
            file for which to save context

        Returns
        -------
        List[Document]
            splitted document content as documents
        """
        extension = Path(filename).suffix.removeprefix(".")
        with NamedTemporaryFile(mode="wb") as temp:
            temp.write(file_.read())
            loader = get_loader(extension)(temp.name)
            documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=params.chunk_size, chunk_overlap=params.chunk_overlap, separators=["\n\n", "\n", "."]
        )
        texts = splitter.split_documents(documents)
        return texts

    @abstractmethod
    def persist(self, filename: str, params: models.LLMRequestBodyBase, file_: BinaryIO) -> models.LLMResult:
        """Persist the embedded documents

        Parameters
        ----------
        filename : str
            Name of the file to load
        params : models.LLMRequestBodyBase
            api parameters
        file_ : BinaryIO
            file for which to save context

        Returns
        -------
        models.VectorScanResult
            process status
        """
        raise NotImplementedError

    @abstractmethod
    def context_object(self, **kwargs) -> VectorStore:
        """Prepare the processor object. This method needs specific implementations because most of the VectorStores
        are initialized with different parameters

        Returns
        -------
        VectorStore
            An initialized instance of a VectorStore implementation
        """
        raise NotImplementedError

    def load_and_respond(self, question: str, **kwargs) -> models.LLMResult:
        """Load the context and answer the question

        Parameters
        ----------
        question : str
            The question to answer

        Returns
        -------
        models.VectorScanResult
            The final response of the LLM
        """
        context_util = self.context_object(**kwargs)
        llm = ChatOpenAI(verbose=True, temperature=0)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm, retriever=context_util.as_retriever(), return_source_documents=self.envs.debug
        )
        if self.envs.debug:
            result = qa_chain({"query": question})
            print(result["source_documents"])
            return models.LLMResult(response=result["result"])
        result = qa_chain.run(question)
        return models.LLMResult(response=result)


class LocalManager(LLMContextManager):
    """Local manager implementation. It uses `SKLearnVectorStore` as its processor and the context is persisted as a
    parquet file"""

    def persist(self, filename: str, params: models.LLMRequestBodyBase, file_: BinaryIO) -> models.LLMResult:
        documents = self.load_and_preprocess(filename, params, file_)
        db_path = LOCAL_STORE_HOME / filename
        db_path.parent.mkdir(exist_ok=True, parents=True)
        embeddings_util = OpenAIEmbeddings()
        processor = SKLearnVectorStore.from_documents(
            documents, embeddings_util, persist_path=str(db_path.with_suffix(".parquet")), serializer="parquet"
        )
        processor.persist()
        return models.LLMResult(response="success")

    def context_object(self, **kwargs) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = SKLearnVectorStore(
            embedding=embeddings_util,
            persist_path=str((LOCAL_STORE_HOME / kwargs["filename"]).with_suffix(".parquet")),
            serializer="parquet",
        )
        return processor


class PineconeManager(LLMContextManager):
    """Pinecone manager implementation. It uses `Pinecone` as its processor and vector store"""

    def persist(self, filename: str, params: models.LLMRequestBodyBase, file_: BinaryIO) -> models.LLMResult:
        try:
            pinecone.init(api_key=self.envs.pinecone_token, environment=self.envs.pinecone_environment_region)
        except Exception as ex:
            raise VectorStoreConnectionError from ex
        documents = self.load_and_preprocess(filename, params, file_)
        embeddings_util = OpenAIEmbeddings()
        Pinecone.from_documents(documents, embeddings_util, index_name=self.envs.pinecone_index)
        return models.LLMResult(response="success")

    def context_object(self, **kwargs) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = Pinecone.from_existing_index(index_name=self.envs.pinecone_index, embedding=embeddings_util)
        return processor


def get_setter(processor: models.SimilarityProcessor) -> LLMContextManager:
    match processor:
        case models.SimilarityProcessor.LOCAL:
            return LocalManager()
        case models.SimilarityProcessor.PINECONE:
            return PineconeManager()
