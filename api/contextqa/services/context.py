from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from operator import itemgetter
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import AsyncGenerator, BinaryIO, Type, ContextManager, Callable

from chromadb import PersistentClient
from fastapi import UploadFile
from langchain.schema import format_document, BasePromptTemplate
from langchain.memory.chat_memory import BaseChatMemory
from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.base import VectorStore
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import CSVLoader, PyMuPDFLoader, TextLoader
from langchain_community.docstore.document import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableSequence
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pydantic import BaseModel, ConfigDict
from pinecone import Pinecone, ServerlessSpec, Index
from sqlalchemy.orm import Session

from contextqa import logger, settings
from contextqa.models import PartialModelData, VectorStoreSettings
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


def _combine_documents(
    docs: list[Document],
    document_prompt: BasePromptTemplate = prompts.DEFAULT_DOCUMENT_PROMPT,
    document_separator: str = "\n\n",
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


class LLMContextManager(ABC):
    """Base llm manager"""

    @property
    def _store_settings(self) -> VectorStoreSettings:
        return get_or_set(kind="store")

    def _get_runnable_qa(self, model: BaseChatModel, memory_obj: BaseChatMemory) -> RunnableSequence:
        loaded_memory = RunnablePassthrough.assign(
            chat_history=RunnableLambda(memory_obj.load_memory_variables) | itemgetter("chat_history"),
        )
        standalone_question = {
            "standalone_question": {
                "question": lambda x: x["question"],
                "chat_history": lambda x: get_buffer_string(x["chat_history"]),
            }
            | prompts.CONTEXTQA_RETRIEVAL_PROMPT
            | model
            | StrOutputParser()
        }
        # Now we retrieve the documents
        retrieved_documents = {
            "docs": itemgetter("standalone_question") | self.context_object().as_retriever(),
            "question": lambda x: x["standalone_question"],
        }
        # Now we construct the inputs for the final prompt
        final_inputs = {
            "context": lambda x: _combine_documents(x["docs"]),
            "question": itemgetter("question"),
        }
        # And finally, we do the part that returns the answers
        answer = {
            "answer": final_inputs | prompts.ANSWER_PROMPT | model,
            "docs": itemgetter("docs"),
        }
        # And now we put it all together!
        final_chain = loaded_memory | standalone_question | retrieved_documents | answer

        return final_chain

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

    def load_and_respond(self, question: str, partial_model_data: PartialModelData) -> AsyncGenerator:
        """Load the context and answer the question

        Parameters
        ----------
        question : str
            The question to answer

        Returns
        -------
        AsyncGenerator
            stream of the final response
        """
        llm = partial_model_data.partial_model(streaming=True)
        runnable = self._get_runnable_qa(llm, memory.Redis(session="context", buffer=True))
        return consumer_producer_qa(runnable.astream({"question": question}))


class LocalManager(LLMContextManager):
    """Local manager implementation. It uses `Chroma` as its processor and the context is persisted as a
    parquet file"""

    def __init__(self, **data):
        super().__init__(**data)
        self.client = PersistentClient(path=str(self._store_settings.store_params["home"]))

    def persist(self, filename: str, file_: BinaryIO, session: Session) -> LLMResult:
        documents, ids = self.load_and_preprocess(filename, file_, session)
        embeddings_util = OpenAIEmbeddings()
        Chroma.from_documents(
            documents,
            embeddings_util,
            ids=ids,
            persist_directory=str(self._store_settings.store_params["home"]),
            client=self.client,
            collection_name=self._store_settings.store_params["collection"],
        )
        return LLMResult(response="success")

    def context_object(self) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = Chroma(
            client=self.client,
            collection_name=self._store_settings.store_params["collection"],
            embedding_function=embeddings_util,
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
        embeddings_util = OpenAIEmbeddings()
        try:
            _CustomPineconeVectorStore.from_documents(documents, embeddings_util, index_name=index, ids=ids)
        except Exception as ex:
            logger.exception("Error indexing source: %s", ex)
            session.rollback()
            raise VectorDBConnectionError from ex
        return LLMResult(response="success")

    def context_object(self) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = _CustomPineconeVectorStore.from_existing_index(
            index_name=self._store_settings.store_params["index"], embedding=embeddings_util
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
