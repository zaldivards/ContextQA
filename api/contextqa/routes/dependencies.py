from contextlib import contextmanager
from typing import Generator

from chromadb import PersistentClient
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory
from langchain_community.vectorstores import Chroma
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pinecone import Pinecone
from sqlalchemy.orm import Session

from contextqa import logger
from contextqa.services.db import session_factory
from contextqa.services.context import PineconeManager, LocalManager, LLMContextManager
from contextqa.utils.clients import StoreClient, PineconeClient, ChromaClient
from contextqa.utils.settings import get_or_set
from contextqa.utils.streaming import ChainCompatibleGoogleGenerativeAI


def get_initialized_model() -> BaseChatModel:
    """Initialized model from OpenAI or HuggingFace

    Returns
    -------
    BaseChatModel
    """
    model_settings = get_or_set()

    if model_settings.provider == "openai":
        return ChatOpenAI(
            openai_api_key=model_settings.token,
            temperature=model_settings.temperature,
            model=model_settings.model,
            streaming=True,
        )
    if model_settings.provider == "google":
        return ChainCompatibleGoogleGenerativeAI(
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            },
            convert_system_message_to_human=True,
            google_api_key=model_settings.token,
            temperature=model_settings.temperature,
            model=model_settings.model,
            streaming=True,
        )


def store_client() -> StoreClient | None:
    """Return the client for a specific store chosen using the dynamic store settings

    Returns
    -------
    StoreClient | None
    """
    store_settings = get_or_set(kind="store")
    if store_settings.store == "chroma":
        home = str(store_settings.store_params["home"])
        # chroma_client = PersistentClient(path=home)
        chroma_client = Chroma(
            client=PersistentClient(path=home),
            collection_name=store_settings.store_params["collection"],
            persist_directory=home,
        )
        return ChromaClient(client=chroma_client)
    try:
        pinecone_client = Pinecone(api_key=store_settings.store_params["token"]).Index(
            store_settings.store_params["index"]
        )
    except Exception as ex:
        logger.error(ex)
        return None
    return PineconeClient(client=pinecone_client)


def context_manager() -> LLMContextManager:
    """Return a specific context manager chosen using the dynamic store settings

    Returns
    -------
    LLMContextManager
    """
    store_settings = get_or_set(kind="store")
    if store_settings.store == "chroma":
        manager = LocalManager()
    else:
        manager = PineconeManager()

    return manager


def get_db() -> Generator[Session, None, None]:
    """DB session manager

    Yields
    ------
    Generator
        db session
    """
    try:
        session = session_factory()
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


session_generator = contextmanager(get_db)
