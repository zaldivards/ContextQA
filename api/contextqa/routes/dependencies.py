from functools import partial
from typing import Generator

from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory
from langchain_openai import ChatOpenAI

from contextqa.models import PartialModelData
from contextqa.services.db import session_factory
from contextqa.utils.settings import get_or_set
from contextqa.utils.streaming import ChainCompatibleGoogleGenerativeAI


def get_partial_initialized_model() -> PartialModelData:
    """Partial initialized model from OpenAI or HuggingFace

    Returns
    -------
    PartialModelData
    """
    model_settings = get_or_set()

    if model_settings["provider"] == "openai":
        return PartialModelData(
            partial_model=partial(
                ChatOpenAI,
                openai_api_key=model_settings["token"],
                temperature=model_settings["temperature"],
                model=model_settings["model"],
            ),
            callback=None,
        )
    if model_settings["provider"] == "google":
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
                google_api_key=model_settings["token"],
                temperature=model_settings["temperature"],
                model=model_settings["model"],
            ),
            callback=None,
        )


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
