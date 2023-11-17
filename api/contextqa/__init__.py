import logging
from pathlib import Path

from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class AppSettings(BaseSettings):
    media_home: Path = Path(".media/")
    local_vectordb_home: Path = Path(".chromadb/")
    openai_api_key: str
    redis_url: str
    serpapi_api_key: str = "no token"
    twitter_api_key: str = "no token"
    twitter_api_secret: str = "no token"
    twitter_access_token: str = "no token"
    twitter_api_secret: str = "no token"
    pinecone_token: str = ""
    pinecone_index: str = ""
    pinecone_environment_region: str = ""
    deployment: str

    @property
    def debug(self) -> bool:
        return self.deployment == "dev"


def get_logger() -> logging.Logger:
    return logging.getLogger("contextqa")


# pylint: disable=C0413
from contextqa.parsers import models
from contextqa.services import chat, context

settings = AppSettings()
