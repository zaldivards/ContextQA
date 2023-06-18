from functools import lru_cache

from pydantic import BaseSettings

from retriever.parsers import models
from retriever.services import social_media, vector


class AppSettings(BaseSettings):
    open_api_key: str
    serpapi_api_key: str
    twitter_api_key: str
    twitter_api_secret: str
    twitter_access_token: str
    twitter_api_secret: str


@lru_cache()
def settings() -> AppSettings:
    return AppSettings()
