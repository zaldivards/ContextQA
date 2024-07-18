import logging
import json
from functools import cached_property
from pathlib import Path
from typing import Literal

from pydantic import ValidationError
from pydantic_settings import BaseSettings


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("contextqa")


contextqa_base_data_dir = Path.home() / "contextqa-data"


class Configurables:
    """Settings which can be updated on settings initialization"""

    config_path = contextqa_base_data_dir / "settings.json"
    media_home = contextqa_base_data_dir / "media"
    local_vectordb_home = contextqa_base_data_dir / "vectordb-data"


class AppSettings(BaseSettings):
    """Project settings"""

    config_path: Path = Configurables.config_path
    tmp_separator: str = ":::sep:::"
    media_home: Path = Configurables.media_home
    local_vectordb_home: Path = Configurables.local_vectordb_home
    sqlite_url: str = f"sqlite:///{contextqa_base_data_dir / 'contextqa'}.sqlite3"
    deployment: Literal["dev", "prod"] = "prod"

    def initialize(
        self,
        config_path: Path | None = None,
        media_home: Path | None = None,
        local_vectordb_home: Path | None = None,
    ):
        """Initialize the configurable if users provide the corresponding CLI arguments"""
        if config_path:
            self.config_path = config_path
        if media_home:
            self.media_home = media_home
        if local_vectordb_home:
            self.local_vectordb_home = local_vectordb_home

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.media_home.mkdir(parents=True, exist_ok=True)
        self.local_vectordb_home.mkdir(parents=True, exist_ok=True)

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

        with open(self.config_path, mode="a+", encoding="utf-8") as settings_file:
            try:
                settings_file.seek(0)
                return SettingsSchema.model_validate_json(settings_file.read())
            except ValidationError:  # error is thrown if the user sets a path to an empty json file
                return SettingsSchema()

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
            json.dump(model_settings.model_dump(exclude_none=True, exclude_unset=True), settings_file)

    @cached_property
    def sqlalchemy_url(self) -> str:
        """sqlalchemy url built either from the sqlite url or the credential of a specific mysql server"""
        # pylint: disable=C0415
        from contextqa.models.schemas import ExtraSettings
        from contextqa.utils.settings import get_or_set

        db_settings: ExtraSettings = get_or_set("extra")
        if db_settings.database.url:
            logger.info("Using SQLite")
            return self.sqlite_url
        logger.info("Using MYSQL")
        uri = (
            f"mysql+pymysql://{db_settings.database.credentials.user}:{db_settings.database.credentials.password}"
            f"@{db_settings.database.credentials.host}/{db_settings.database.credentials.db}"
        )
        if extras := db_settings.database.credentials.extras:
            uri += extras
        return uri

    def rebuild_sqlalchemy_url(self):
        """Trigger to rebuild the sqlalchemy URL"""
        del self.__dict__["sqlalchemy_url"]


settings = AppSettings()


if settings.deployment == "dev":
    settings.initialize()
