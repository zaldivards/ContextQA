from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO, Optional

from contextqa import models, settings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import SKLearnVectorStore
from langchain.vectorstores.base import VectorStore

LOCAL_STORE_HOME = Path("/var") / "embeddings"
LOADERS = {"pdf": PyPDFLoader, "txt": TextLoader}


def get_loader(extension: str) -> BaseLoader:
    return LOADERS[extension]


class LLMContextManager(ABC):
    """Base llm manager"""

    def load_and_preprocess(
        self, filename: str, params: models.LLMRequestBodyBase, file_: BinaryIO
    ) -> models.LLMResult:
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

    def load_and_respond(self, question: str, filename: Optional[str] = None) -> models.LLMResult:
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
        envs = settings()
        context_util = self.context_object(filename)
        llm = ChatOpenAI(verbose=True, temperature=0)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm, retriever=context_util.as_retriever(), return_source_documents=envs.debug
        )
        if envs.debug:
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

    def context_object(self, filename: Optional[str] = None) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = SKLearnVectorStore(
            embedding=embeddings_util,
            persist_path=str((LOCAL_STORE_HOME / filename).with_suffix(".parquet")),
            serializer="parquet",
        )
        return processor


def get_setter(processor: models.SimilarityProcessor) -> LLMContextManager:
    match processor:
        case models.SimilarityProcessor.LOCAL:
            return LocalManager()