from pydantic import BaseModel

from contextqa import settings
from contextqa.models.schemas import ModelSettingsUpdate, StoreSettings, ExtraSettings, LLMMemory, DBModel


class ModelSettings(ModelSettingsUpdate):
    """Settings related to specific LLMs"""

    @classmethod
    def from_defaults(cls) -> "StoreSettings":
        """Get default settings related to the vector store"""
        return cls(
            temperature=1,
        )


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
            memory=LLMMemory(kind="Local"),
            database=DBModel(url=settings.sqlite_url),
        )


class SettingsSchema(BaseModel):
    """Dict schema returned from the config manager"""

    model: ModelSettings | None = ModelSettings.from_defaults()
    store: VectorStoreSettings | None = VectorStoreSettings.from_defaults()
    extra: Extra | None = Extra.from_defaults()
