from langchain.output_parsers import PydanticOutputParser

# pylint: disable=E0611
from pydantic import BaseModel, Field


class Summary(BaseModel):
    summary: str = Field(description="Summary of the person")
    facts: list[str] = Field(description="Interesting facts about the person")
    ice_breakers: list[str] = Field(description="Topics of interest of the person")


summary_parser = PydanticOutputParser(pydantic_object=Summary)
