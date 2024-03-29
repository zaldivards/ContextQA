# pylint: disable=E0611
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class SimilarityProcessor(str, Enum):
    """Enum representing the supported vector stores

    Note that the LOCAL identifier refers to ChromaDB
    """

    LOCAL = "local"
    PINECONE = "pinecone"


class SourceFormat(str, Enum):
    """Enum representing the supported file formats"""

    PDF = "pdf"
    TXT = "txt"
    CSV = "csv"


class Source(BaseModel):
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
