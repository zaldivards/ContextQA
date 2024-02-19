from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from operator import itemgetter
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import AsyncGenerator, BinaryIO, Type

import pinecone
from chromadb import PersistentClient
from fastapi import UploadFile
from langchain.schema import format_document, BasePromptTemplate
from langchain.memory.chat_memory import BaseChatMemory
from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores.pinecone import Pinecone
from langchain_community.document_loaders import CSVLoader, PyMuPDFLoader, TextLoader
from langchain_community.docstore.document import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableSequence
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel
from sqlalchemy.orm import Session

from contextqa import get_logger, settings
from contextqa.models import PartialModelData
from contextqa.models.schemas import LLMResult, SimilarityProcessor, SourceFormat, IngestionResult
from contextqa.utils import memory, prompts
from contextqa.utils.exceptions import VectorDBConnectionError, DuplicatedSourceError
from contextqa.utils.sources import check_digest, get_not_seen_chunks
from contextqa.utils.streaming import consumer_producer_qa


LOGGER = get_logger()
LOADERS: dict[str, Type[BaseLoader]] = {".pdf": PyMuPDFLoader, ".txt": TextLoader, ".csv": CSVLoader}

chroma_client = PersistentClient(path=str(settings.local_vectordb_home))


def _combine_documents(
    docs: list[Document],
    document_prompt: BasePromptTemplate = prompts.DEFAULT_DOCUMENT_PROMPT,
    document_separator: str = "\n\n",
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


class LLMContextManager(BaseModel, ABC):
    """Base llm manager"""

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
            if extension == "." + SourceFormat.PDF:
                path = settings.media_home / filename
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
        if extension == "." + SourceFormat.CSV:
            return get_not_seen_chunks(documents, extension)

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", "."])
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

    def persist(self, filename: str, file_: BinaryIO, session: Session) -> LLMResult:
        documents, ids = self.load_and_preprocess(filename, file_, session)
        embeddings_util = OpenAIEmbeddings()
        processor = Chroma.from_documents(
            documents,
            embeddings_util,
            ids=ids,
            persist_directory=str(settings.local_vectordb_home),
            client=chroma_client,
            collection_name=settings.default_collection,
        )
        processor.persist()
        return LLMResult(response="success")

    def context_object(self) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = Chroma(
            client=chroma_client,
            collection_name=settings.default_collection,
            embedding_function=embeddings_util,
            persist_directory=str(settings.local_vectordb_home),
        )
        return processor


class PineconeManager(LLMContextManager):
    """Pinecone manager implementation. It uses `Pinecone` as its processor and vector store"""

    def persist(self, filename: str, file_: BinaryIO, session: Session) -> LLMResult:
        try:
            LOGGER.info("Initializing Pinecone connection")
            pinecone.init(api_key=settings.pinecone_token, environment=settings.pinecone_environment_region)
        except Exception as ex:
            raise VectorDBConnectionError from ex
        documents = self.load_and_preprocess(filename, file_, session)
        embeddings_util = OpenAIEmbeddings()
        try:
            Pinecone.from_documents(documents, embeddings_util, index_name=settings.pinecone_index)
        except Exception as ex:
            raise VectorDBConnectionError from ex
        return LLMResult(response="success")

    def context_object(self) -> VectorStore:
        embeddings_util = OpenAIEmbeddings()
        processor = Pinecone.from_existing_index(index_name=settings.pinecone_index, embedding=embeddings_util)
        return processor


class BatchProcessor(BaseModel):
    """QA processor for batch ingestions"""

    manager: LLMContextManager

    def _wrapper(self, *args) -> None | str:
        try:
            self.manager.persist(*args)
            return None
        except DuplicatedSourceError:
            return args[0]  # filename

    def persist(self, sources: list[UploadFile], session: Session) -> IngestionResult:
        """Ingest the uploaded sources

        Parameters
        ----------
        sources : list[UploadFile]
            uploaded sources
        session : Session
            db session

        Returns
        -------
        IngestionResult
        """
        func = self._wrapper
        skipped_files = []
        completed = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [executor.submit(func, source.filename, source.file, session) for source in sources]
            for future in as_completed(tasks):
                result = future.result()
                if result:
                    # skipped because the content had not changed
                    skipped_files.append(result)
                else:
                    # successfully ingested
                    completed += 1
        return IngestionResult(completed=completed, skipped_files=skipped_files)


def get_setter(processor: SimilarityProcessor | None = None) -> LLMContextManager:
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
    processor = processor or SimilarityProcessor.LOCAL
    match processor:
        case SimilarityProcessor.LOCAL:
            return LocalManager()
        case SimilarityProcessor.PINECONE:
            return PineconeManager()
