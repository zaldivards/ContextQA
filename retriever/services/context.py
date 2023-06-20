from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO, Optional

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import SKLearnVectorStore
from langchain.vectorstores.base import VectorStore

from retriever import models

LOCAL_STORE_HOME = Path.home() / "embeddings"
LOADERS = {"pdf": PyPDFLoader, "txt": TextLoader}


def get_loader(extension: str) -> BaseLoader:
    return LOADERS[extension]


class LLMContextManager(ABC):
    """Base llm manager"""

    def load_and_preprocess(
        self, filename: str, params: models.LLMRequestBodyBase, file_: BinaryIO
    ) -> models.VectorScanResult:
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
        models.VectorScanResult
            process status
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
        return self.persist(texts, filename)

    @abstractmethod
    def persist(self, documents: list[Document], filename: str) -> models.VectorScanResult:
        """Persist the embedded documents

        Parameters
        ----------
        documents : list[Document]
            the preprocessed file content
        filename : str
            name of the file. It will be used as identifier

        Returns
        -------
        models.VectorScanResult
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

    def load_and_respond(self, question: str, filename: Optional[str] = None) -> models.VectorScanResult:
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
        models.VectorScanResult
            The final response of the LLM
        """
        context_util = self.context_object(filename)
        qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(), retriever=context_util.as_retriever())
        result = qa_chain.run(question)
        return models.VectorScanResult(response=result)


class LocalManager(LLMContextManager):
    """Local manager implementation. It uses `SKLearnVectorStore` as its processor and the context is persisted as a
    parquet file"""

    def persist(self, documents: list[Document], filename: str) -> models.VectorScanResult:
        embeddings_util = OpenAIEmbeddings()
        processor = SKLearnVectorStore.from_documents(
            documents, embeddings_util, persist_path=str(LOCAL_STORE_HOME / filename), serializer="parquet"
        )
        processor.persist()
        return models.VectorScanResult(response="success")

    def context_object(self, filename: Optional[str] = None) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = SKLearnVectorStore(
            embedding=embeddings_util, persist_path=str(LOCAL_STORE_HOME / filename), serializer="parquet"
        )
        return processor


def get_setter(processor: models.SimilarityProcessor) -> LLMContextManager:
    match processor:
        case models.SimilarityProcessor.LOCAL:
            return LocalManager()
