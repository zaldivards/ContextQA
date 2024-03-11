from typing import Literal

from contextqa import settings as app_settings
from contextqa.models import SettingsSchema, VectorStoreSettings, ModelSettings


def _check_local_store_args(store_settings: VectorStoreSettings | None) -> VectorStoreSettings | None:
    store_settings = store_settings or {"store": "chroma", "chunk_size": 1000, "overlap": 200, "store_params": {}}
    if store_settings["store"] == "chroma":
        if "home" not in store_settings["store_params"]:
            store_settings["store_params"]["home"] = app_settings.local_vectordb_home
        if "collection" not in store_settings["store_params"]:
            store_settings["store_params"]["collection"] = app_settings.default_collection
        return store_settings
    return None


def _config_manager():
    """Config manager closure"""
    settings: SettingsSchema = app_settings.model_settings

    def config_manager(kind: Literal["model", "store"] = "model", **kwargs) -> ModelSettings | VectorStoreSettings:
        """Manage settings. Note that this utility can be used either to get or set settings.

        Possible use cases are listed below:

        - Read settings: get_or_set()
        - Write settings: get_or_set(**my_settings)

        Both read and write return the latest settings

        Returns
        -------
        ModelSettings | VectorStoreSettings
        """
        nonlocal settings
        if not kwargs:
            if kind == "store":
                settings_ = settings.get(kind)
                settings_ = _check_local_store_args(settings_)
                return settings_
            return settings[kind]
        if not settings.get(kind):
            settings[kind] = kwargs
        else:
            settings[kind].update(kwargs)
        app_settings.model_settings = settings
        return settings[kind]

    return config_manager


get_or_set = _config_manager()
