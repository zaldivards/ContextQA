import logging
import json
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("contextqa")


class AppSettings(BaseSettings):
    """Project settings"""

    config_path: Path = Path("settings.json")
    default_collection: str = "contextqa-default"
    tmp_separator: str = ":::sep:::"
    media_home: Path = Path(".media/")
    local_vectordb_home: Path = Path(".chromadb/")
    sqlite_url: str = "sqlite:///contextqa.sqlite3"
    openai_api_key: str | None = None
    redis_url: str | None = None
    deployment: str = "dev"
    mysql_user: str | None = None
    mysql_password: str | None = None
    mysql_host: str | None = None
    mysql_dbname: str | None = None
    mysql_extra_args: str | None = None

    @property
    def debug(self) -> bool:
        """lazy attr based on the deployment attr"""
        return self.deployment == "dev"

    @property
    def model_settings(self):
        """Get the initial settings

        Returns
        -------
        SettingsSchema
        """
        #  pylint: disable=C0415
        from contextqa.models import SettingsSchema

        with open(self.config_path, mode="r", encoding="utf-8") as settings_file:
            return SettingsSchema.model_validate_json(settings_file.read())

    @model_settings.setter
    def model_settings(self, model_settings):
        """
        Parameters
        ----------
        model_settings : SettingsSchema

        Returns
        -------
        SettingsSchema
        """
        with open(self.config_path, mode="w", encoding="utf-8") as settings_file:
            return json.dump(model_settings.model_dump(), settings_file)

    @field_validator("media_home")
    @classmethod
    def validate_media_path(cls, value: Path) -> Path:
        """validator for media path"""
        value.mkdir(parents=True, exist_ok=True)
        return value

    @property
    def sqlalchemy_url(self) -> str:
        """sqlalchemy url built either from the sqlite url or the credential of a specific mysql server"""
        mysql_requirements = [self.mysql_user, self.mysql_password, self.mysql_host, self.mysql_dbname]
        if not all(mysql_requirements):
            logger.info("Using sqlite")
            return self.sqlite_url
        uri = "mysql+pymysql://{}:{}@{}/{}".format(*mysql_requirements)
        if extras := self.mysql_extra_args:
            uri += extras
        return uri


settings = AppSettings()

# pylint: disable=C0413
from contextqa.services import chat, context
