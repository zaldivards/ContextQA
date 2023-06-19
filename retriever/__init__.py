from functools import lru_cache

from pydantic import BaseSettings


class AppSettings(BaseSettings):
    openai_api_key: str
    serpapi_api_key: str
    twitter_api_key: str
    twitter_api_secret: str
    twitter_access_token: str
    twitter_api_secret: str
    pinecone_token: str = ""
    pinecone_index: str = ""


@lru_cache()
def settings() -> AppSettings:
    return AppSettings()


# pylint: disable=C0413
from retriever.parsers import models
from retriever.services import social_media, vector
