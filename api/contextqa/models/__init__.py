from dataclasses import dataclass
from typing import TypedDict, Literal, Callable

from langchain_core.language_models.chat_models import BaseChatModel
from langchain.callbacks.streaming_aiter_final_only import AsyncFinalIteratorCallbackHandler


class SettingsSchema(TypedDict):
    """Dict schema returned from the config manager"""

    platform: Literal["openai", "huggingface", "google"]
    model: str
    temperature: float
    local: bool
    token: str


@dataclass
class PartialModelData:
    """Contains a partial initialized model and an optional callback"""

    partial_model: Callable[..., BaseChatModel]
    callback: AsyncFinalIteratorCallbackHandler | None = None
