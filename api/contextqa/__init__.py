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


class AppSettings(BaseSettings):
    """Project settings"""

    config_path: Path | None = None
    tmp_separator: str = ":::sep:::"
    media_home: Path | None = None
    local_vectordb_home: Path | None = None
    sqlite_url: str = f"sqlite:///{contextqa_base_data_dir / 'contextqa'}.sqlite3"
    deployment: Literal["dev", "prod"] = "prod"

    def init_from_cli(self, config_path: Path, media_home: Path, local_vectordb_home: Path):
        """Initialize the configurable if users provide the corresponding CLI arguments"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path = config_path
        media_home.mkdir(parents=True, exist_ok=True)
        self.media_home = media_home
        local_vectordb_home.mkdir(parents=True, exist_ok=True)
        self.local_vectordb_home = local_vectordb_home

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
