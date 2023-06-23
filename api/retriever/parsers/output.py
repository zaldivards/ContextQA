from langchain.output_parsers import PydanticOutputParser

from retriever.parsers.models import Summary

summary_parser = PydanticOutputParser(pydantic_object=Summary)
