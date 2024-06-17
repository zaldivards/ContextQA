# pylint: disable=E0611
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class SourceFormat(str, Enum):
    """Enum representing the supported file formats"""

    PDF = ".pdf"
    TXT = ".txt"
    CSV = ".csv"


class Status(str, Enum):
    """Enum representing the supported statuses"""

    OK = "ok"
    FAIL = "fail"
    IRRELEVANT = "irrelevant"  # does not matter whether it's OK or FAIL


class BaseSource(BaseModel):
    """Base source model"""

    title: str


class Source(BaseSource):
    """Base source model"""

    id: int
    digest: str


class SourcesList(BaseModel):
    sources: list[Source]
    total: int


class SourceSegment(BaseSource):
    """Source returned as metadata in QA sessions"""

    title: str
    format_: Annotated[SourceFormat, Field(alias="format")]
    content: str | list


class SourceStatus(BaseModel):
    """Response model returning the status of data sources"""

    status: Literal["ready", "empty"]

    @classmethod
    def from_count_status(cls, status_flag: bool) -> "SourceStatus":
        """Get instance given the status flag"""
        status = "ready" if status_flag else "empty"
        return cls(status=status)


class LLMResult(BaseModel):
    """LLM chat response object"""

    response: str


class IngestionResult(BaseModel):
    """Result of the ingestion process"""

    completed: int
    skipped_files: list[str]


class LLMContextQueryRequest(BaseModel):
    """QA session request object"""

    question: str


class LLMQueryRequest(BaseModel):
    """Chat request object"""

    message: str
    internet_access: bool = False


class ModelSettings(BaseModel):
    """Used to show settings"""

    provider: Literal["openai", "huggingface", "google"] | None = None
    model: str | None = None
    temperature: float | None = None
    local: bool = False


class ModelSettingsUpdate(ModelSettings):
    """Used to update settings"""

    token: str | None = None


class ProviderDetail(BaseModel):
    """Represents a provider and its available models"""

    provider: Literal["openai", "huggingface", "google"]
    models: list[str]


class ModelSettingsDetail(ModelSettings):
    """Response object for settings"""

    provider_options: list[ProviderDetail]


class StoreSettings(BaseModel):
    """Used to show store settings"""

    store: Literal["chroma", "pinecone"] | None = None
    chunk_size: int | None = None
    overlap: int | None = None
    store_params: dict | None = None


class StoreSettingsUpdate(StoreSettings):
    """Used to update store settings"""


class LLMMemory(BaseModel):
    """LLM memory settings"""

    kind: Literal["Local", "Redis"] = "Redis"
    url: str | None = None


class _DBData(BaseModel):
    user: str | None = None
    db: str | None = None
    host: str | None = None
    password: str | None = None
    extras: str | None = None


class DBModel(BaseModel):
    """ContextQA database settings

    The database contains information about ingested sources
    """

    kind: Literal["sqlite", "mysql"] = "sqlite"
    url: str | None = None
    credentials: _DBData | None = None


class ExtraSettings(BaseModel):
    """Extra settings related to LLM's memory and ingested sources database"""

    media_dir: str | None = None
    memory: LLMMemory | None = None
    database: DBModel | None = None


class ExtraSettingsUpdate(ExtraSettings):
    """Schema to patch extra settings such as memory and database"""


class ComponentStatus(BaseModel):
    """Component status"""

    name: str
    status: Status
