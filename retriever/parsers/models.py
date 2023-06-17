# pylint: disable=E0611
from pydantic import BaseModel, Field


class Summary(BaseModel):
    summary: str = Field(description="Summary of the person")
    facts: list[str] = Field(description="Interesting facts about the person")
    ice_breakers: list[str] = Field(description="Topics of interest of the person")


class VectorScanResult(BaseModel):
    query: str
    result: str
