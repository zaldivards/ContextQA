# pylint: disable=E0611
from enum import Enum

from pydantic import BaseModel, Field


class SimilarityProcessor(str, Enum):
    LOCAL = "local"
    PINECONE = "pinecone"


class Summary(BaseModel):
    summary: str = Field(description="Summary of the person")
    facts: list[str] = Field(description="Interesting facts about the person")
    ice_breakers: list[str] = Field(description="Topics of interest of the person")


class VectorScanResult(BaseModel):
    query: str
    result: str


class LLMQueryRequestBodyBase(BaseModel):
    query: str = Field(description="The query we want the llm to respond", min_length=10)
    separator: str = Field(description="Separator to use for the text splitting", default=".")
    chunk_size: int = Field(description="size of each splitted chunk", default=100)


class LLMQueryDocumentRequestBody(LLMQueryRequestBodyBase):
    similarity_processor: SimilarityProcessor


class LLMQueryTextRequestBody(LLMQueryRequestBodyBase):
    content: str = Field(description="The whole content of the 'context'", min_length=500)
