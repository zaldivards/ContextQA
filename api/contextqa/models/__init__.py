from dataclasses import dataclass
from typing import Callable

from langchain_core.language_models.chat_models import BaseChatModel
from langchain.callbacks.streaming_aiter_final_only import AsyncFinalIteratorCallbackHandler
from pydantic import BaseModel


from contextqa.models.schemas import (
    ModelSettingsUpdate,
    StoreSettings,
    ExtraSettings,
    ProviderDetail,
    ModelSettingsDetail,
)


class ModelSettings(ModelSettingsUpdate):
    """Settings related to specific LLMs"""


class VectorStoreSettings(StoreSettings):
    """Settings related to specific vector stores"""


class Extra(ExtraSettings):
    """Settings related to LLM's memory and database"""


class SettingsSchema(BaseModel):
    """Dict schema returned from the config manager"""

    model: ModelSettings | None = None
    store: VectorStoreSettings | None = None
    extra: Extra | None = Extra.from_defaults()


@dataclass
class PartialModelData:
    """Contains a partial initialized model and an optional callback"""

    partial_model: Callable[..., BaseChatModel]
    callback: AsyncFinalIteratorCallbackHandler | None = None
