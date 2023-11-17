# pylint: disable=E0611
from enum import Enum
from typing import Any, Type

from langchain.vectorstores.base import VectorStore
from pydantic import BaseModel, Field


class SimilarityProcessor(str, Enum):
    LOCAL = "local"
    PINECONE = "pinecone"


class Source(BaseModel):
    id_: str = Field(alias="id")
    name: str
    extras: dict[str, Any] = Field(default_factory=dict)


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
    processor: SimilarityProcessor
    identifier: str


class LLMQueryRequest(BaseModel):
    message: str
    internet_access: bool = False


class LLMQueryRequestBody(LLMRequestBodyBase):
    query: str = Field(description="The query we want the llm to respond", min_length=10)


class LLMQueryDocumentRequestBody(LLMQueryRequestBody):
    similarity_processor: SimilarityProcessor = SimilarityProcessor.LOCAL


class LLMQueryTextRequestBody(LLMQueryRequestBody):
    content: str = Field(description="The whole content of the 'context'", min_length=500)


class VectorStoreParams(BaseModel):
    clazz: Type[VectorStore]
    kwargs: dict[str, Any] = Field(default_factory=lambda: {})
