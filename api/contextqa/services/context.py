from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import AsyncGenerator, BinaryIO, Type, ContextManager, Callable

from chromadb import PersistentClient
from fastapi import UploadFile
from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.base import VectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import CSVLoader, PyMuPDFLoader, TextLoader
from langchain_community.docstore.document import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableSequence
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pydantic import BaseModel, ConfigDict
from pinecone import Pinecone, ServerlessSpec, Index
from sqlalchemy.orm import Session

from contextqa import logger, settings
from contextqa.models import VectorStoreSettings
from contextqa.models.schemas import LLMResult, SourceFormat, IngestionResult
from contextqa.utils import memory, prompts
from contextqa.utils.exceptions import VectorDBConnectionError, DuplicatedSourceError
from contextqa.utils.settings import get_or_set
from contextqa.utils.sources import check_digest, get_not_seen_chunks
from contextqa.utils.streaming import consumer_producer_qa


LOADERS: dict[str, Type[BaseLoader]] = {
    ".pdf": PyMuPDFLoader,
    ".txt": TextLoader,
    ".csv": CSVLoader,
}


class LLMContextManager(ABC):
    """Base llm manager"""

    encoder = HuggingFaceEmbeddings()

    @property
    def _store_settings(self) -> VectorStoreSettings:
        return get_or_set(kind="store")

    def _get_runnable_qa(self, model: BaseChatModel) -> RunnableSequence:
        history_aware_retriever = create_history_aware_retriever(
            model, self.context_object().as_retriever(), prompts.STANDALONE_QUESTION_PROMPT
        )

        question_answer_chain = create_stuff_documents_chain(model, prompts.QA_PROMPT)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            memory.runnable_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        return conversational_rag_chain

    def load_and_preprocess(self, filename: str, file_: BinaryIO, session: Session) -> tuple[list[Document], list[str]]:
        """Load and preprocess the file content

        Parameters
        ----------
        filename : str
            Name of the file to load
        file_ : BinaryIO
            file for which to save context
        session : Session
            connection to the db

        Returns
        -------
        tuple[list[Document], list[str]]
            document chunks and their corresponding IDs

        Raises
        ------
        DuplicatedSourceError
            If the data source already exists and its content has not changed
        """
        extension = Path(filename).suffix
        source_content = file_.read()
        check_digest(filename.strip(), source_content, session)
        try:
            if extension == SourceFormat.PDF:
                path = Path(get_or_set("extra").media_dir) / filename
                file_writer = open(path, mode="wb")
            else:
                file_writer = NamedTemporaryFile(mode="wb", suffix=f"{settings.tmp_separator}{filename}")
                path = file_writer.name
            file_writer.write(source_content)
            loader: BaseLoader = LOADERS[extension](str(path))
            documents = loader.load()
        finally:
            file_writer.close()

        # we do not want to split csv files as they are splitted by rows
        if extension == SourceFormat.CSV:
            return get_not_seen_chunks(documents, extension)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._store_settings.chunk_size,
            chunk_overlap=self._store_settings.overlap,
            separators=["\n\n", "\n", "."],
        )
        chunks = splitter.split_documents(documents)
        return get_not_seen_chunks(chunks, extension)

    @abstractmethod
    def persist(self, filename: str, file_: BinaryIO, session: Session) -> LLMResult:
        """Persist the embedded documents

        Parameters
        ----------
        filename : str
            Name of the file to load
        file_ : BinaryIO
            file for which to save context
        session : Session
            connection to the db

        Returns
        -------
        LLMResult
        """
        raise NotImplementedError

    @abstractmethod
    def context_object(self) -> VectorStore:
        """Prepare the processor object. This method needs specific implementations because most of the VectorStores
        are initialized with different parameters

        Returns
        -------
        VectorStore
            An initialized instance of a VectorStore implementation
        """
        raise NotImplementedError

    def load_and_respond(self, question: str, llm: BaseChatModel) -> AsyncGenerator:
        """Load the context and answer the question

        Parameters
        ----------
        question : str
            The question to answer
        llm : BaseChatModel

        Returns
        -------
        AsyncGenerator
            stream of the final response
        """
        runnable = self._get_runnable_qa(llm)
        return consumer_producer_qa(
            runnable.astream({"input": question}, config={"configurable": {"session_id": "context"}})
        )


class LocalManager(LLMContextManager):
    """Local manager implementation. It uses `Chroma` as its processor and the context is persisted as a
    parquet file"""

    def __init__(self, **data):
        super().__init__(**data)
        self.client = PersistentClient(path=str(self._store_settings.store_params["home"]))

    def persist(self, filename: str, file_: BinaryIO, session: Session) -> LLMResult:
        documents, ids = self.load_and_preprocess(filename, file_, session)
        Chroma.from_documents(
            documents,
            self.encoder,
            ids=ids,
            persist_directory=str(self._store_settings.store_params["home"]),
            client=self.client,
            collection_name=self._store_settings.store_params["collection"],
        )
        return LLMResult(response="success")

    def context_object(self) -> VectorStore:
        processor = Chroma(
            client=self.client,
            collection_name=self._store_settings.store_params["collection"],
            embedding_function=self.encoder,
            persist_directory=str(self._store_settings.store_params["home"]),
        )
        return processor


class _CustomPineconeVectorStore(PineconeVectorStore):
    """Custom implementation of `get_pinecone_index` to ensure a raw `api_key` is passed as argument"""

    # pylint: disable=W0221
    @classmethod
    def get_pinecone_index(cls, index_name: str, pool_threads: int = 4, *, _: str | None = None) -> Index:
        token = get_or_set(kind="store").store_params["token"]
        return super().get_pinecone_index(index_name, pool_threads, pinecone_api_key=token)


class PineconeManager(LLMContextManager):
    """Pinecone manager implementation. It uses `Pinecone` as its processor and vector store"""

    def _init(self) -> str:
        index = self._store_settings.store_params["index"]
        pc = Pinecone(api_key=self._store_settings.store_params["token"])

        if index not in pc.list_indexes().names():
            pc.create_index(
                name=index,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=self._store_settings.store_params["environment"]),
            )
        return index

    def persist(self, filename: str, file_: BinaryIO, session: Session) -> LLMResult:
        try:
            logger.info("Initializing Pinecone connection")
            index = self._init()
        except Exception as ex:
            logger.exception("Error connecting to pinecone: %s", ex)
            raise VectorDBConnectionError from ex
        documents, ids = self.load_and_preprocess(filename, file_, session)
        try:
            _CustomPineconeVectorStore.from_documents(documents, self.encoder, index_name=index, ids=ids)
        except Exception as ex:
            logger.exception("Error indexing source: %s", ex)
            session.rollback()
            raise VectorDBConnectionError from ex
        return LLMResult(response="success")

    def context_object(self) -> VectorStore:
        processor = _CustomPineconeVectorStore.from_existing_index(
            index_name=self._store_settings.store_params["index"], embedding=self.encoder
        )
        return processor


class BatchProcessor(BaseModel):
    """QA processor for batch ingestions"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    manager: LLMContextManager
    session_generator: Callable[[], ContextManager[Session]]

    def _wrapper(self, *args) -> None | str:
        try:
            with self.session_generator() as session:
                self.manager.persist(*args, session)
            return None
        except DuplicatedSourceError:
            return args[0]  # filename
        except Exception as ex:
            logger.warning("'%s' ingestion failed. Reason: %s", args[0], ex)
            return f"{args[0]} - Failed to persist"

    def persist(self, sources: list[UploadFile]) -> IngestionResult:
        """Ingest the uploaded sources

        Parameters
        ----------
        sources : list[UploadFile]
            uploaded sources
        session_generator : ContextManager[Session]
            db session manager

        Returns
        -------
        IngestionResult
        """
        func = self._wrapper
        skipped_files = []
        completed = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [executor.submit(func, source.filename, source.file) for source in sources]
            for future in as_completed(tasks):
                result = future.result()
                if result:
                    # skipped because the content had not changed
                    skipped_files.append(result)
                else:
                    # successfully ingested
                    completed += 1
        return IngestionResult(completed=completed, skipped_files=skipped_files)
