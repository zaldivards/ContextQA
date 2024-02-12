# pylint: disable=E0611
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class SimilarityProcessor(str, Enum):
    LOCAL = "local"
    PINECONE = "pinecone"


class SourceFormat(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    CSV = "csv"


class Source(BaseModel):
    title: str
    format_: Annotated[SourceFormat, Field(alias="format")]
    content: str | list


class LLMResult(BaseModel):
    response: str


class QAResult(LLMResult):
    sources: list[Source]


class LLMRequestBodyBase(BaseModel):
    separator: str = Field(description="Separator to use for the text splitting", default=".")
    chunk_size: int = Field(description="size of each splitted chunk", default=100)
    chunk_overlap: int = 50


class LLMContextQueryRequest(BaseModel):
    question: str


class LLMQueryRequest(BaseModel):
    message: str
    internet_access: bool = False


class LLMQueryRequestBody(LLMRequestBodyBase):
    query: str = Field(description="The query we want the llm to respond", min_length=10)
