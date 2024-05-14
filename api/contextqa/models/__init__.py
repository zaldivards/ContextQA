from dataclasses import dataclass
from typing import Callable

from langchain_core.language_models.chat_models import BaseChatModel
from langchain.callbacks.streaming_aiter_final_only import AsyncFinalIteratorCallbackHandler
from pydantic import BaseModel

from contextqa import settings
from contextqa.models.schemas import ModelSettingsUpdate, StoreSettings, ExtraSettings, LLMMemory, DBModel


class ModelSettings(ModelSettingsUpdate):
    """Settings related to specific LLMs"""


class VectorStoreSettings(StoreSettings):
    """Settings related to specific vector stores"""

    @classmethod
    def from_defaults(cls) -> "StoreSettings":
        """Get default settings related to the vector store"""
        return cls(
            store="chroma",
            chunk_size=1000,
            overlap=200,
            store_params={"home": settings.local_vectordb_home, "collection": "contextqa-default"},
        )


class Extra(ExtraSettings):
    """Settings related to LLM's memory and database"""

    @classmethod
    def from_defaults(cls) -> "ExtraSettings":
        """Get default settings related to LLM's memory and ingested sources database"""

        return cls(
            media_dir=str(settings.media_home),
            memory=LLMMemory(url=settings.redis_url),
            database=DBModel(url=settings.sqlite_url),
        )


class SettingsSchema(BaseModel):
    """Dict schema returned from the config manager"""

    model: ModelSettings | None = None
    store: VectorStoreSettings | None = VectorStoreSettings.from_defaults()
    extra: Extra | None = Extra.from_defaults()


@dataclass
class PartialModelData:
    """Contains a partial initialized model and an optional callback"""

    partial_model: Callable[..., BaseChatModel]
    callback: AsyncFinalIteratorCallbackHandler | None = None
