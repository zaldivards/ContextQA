from functools import partial
from typing import Generator

from chromadb import PersistentClient
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory
from langchain.vectorstores.chroma import Chroma
from langchain_openai import ChatOpenAI
from pinecone import Pinecone

from contextqa.models import PartialModelData
from contextqa.services.db import session_factory
from contextqa.services.context import PineconeManager, LocalManager, LLMContextManager
from contextqa.utils.clients import StoreClient, PineconeClient, ChromaClient
from contextqa.utils.settings import get_or_set
from contextqa.utils.streaming import ChainCompatibleGoogleGenerativeAI


def get_partial_initialized_model() -> PartialModelData:
    """Partial initialized model from OpenAI or HuggingFace

    Returns
    -------
    PartialModelData
    """
    model_settings = get_or_set()

    if model_settings.provider == "openai":
        return PartialModelData(
            partial_model=partial(
                ChatOpenAI,
                openai_api_key=model_settings.token,
                temperature=model_settings.temperature,
                model=model_settings.model,
            ),
            callback=None,
        )
    if model_settings.provider == "google":
        return PartialModelData(
            partial_model=partial(
                ChainCompatibleGoogleGenerativeAI,
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
            ),
            callback=None,
        )


def store_client() -> StoreClient:
    """Return the client for a specific store chosen using the dynamic store settings

    Returns
    -------
    StoreClient
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
    pinecone_client = Pinecone(api_key=store_settings.store_params["token"]).Index(store_settings.store_params["index"])
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


def get_db() -> Generator:
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
