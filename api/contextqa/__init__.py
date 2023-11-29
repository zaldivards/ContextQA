import logging
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_logger() -> logging.Logger:
    return logging.getLogger("contextqa")

class AppSettings(BaseSettings):
    default_collection: str = "contextqa-default"
    tmp_separator: str = ":::sep:::"
    media_home: Path = Path(".media/")
    local_vectordb_home: Path = Path(".chromadb/")
    sqlite_url: str = "sqlite:///contextqa.sqlite"
    openai_api_key: str | None = None
    redis_url: str | None = None
    serpapi_api_key: str | None = None
    twitter_api_key: str | None = None
    twitter_api_secret:str | None = None
    twitter_access_token: str | None = None
    twitter_api_secret: str | None = None
    pinecone_token: str | None = None
    pinecone_index: str | None = None
    pinecone_environment_region: str | None = None
    deployment: str = "dev"
    mysql_user: str | None = None
    mysql_password: str | None = None
    mysql_host: str | None = None
    mysql_dbname: str | None = None
    mysql_extra_args: str | None = None

    @property
    def debug(self) -> bool:
        return self.deployment == "dev"

    @field_validator("media_home")
    @classmethod
    def validate_media_path(cls, value: Path) -> Path:
        value.mkdir(parents=True, exist_ok=True)
        return value
    
    @property
    def sqlalchemy_url(self) -> str:
        mysql_requirements = [self.mysql_user, self.mysql_password, self.mysql_host, self.mysql_dbname]
        if not all(mysql_requirements):
            get_logger().info("Using sqlite")
            return self.sqlite_url
        uri = "mysql+pymysql://{}:{}@{}/{}".format(*mysql_requirements)
        if extras := self.mysql_extra_args:
            uri += extras
        return uri
    




settings = AppSettings()

# pylint: disable=C0413
from contextqa.services import chat, context
