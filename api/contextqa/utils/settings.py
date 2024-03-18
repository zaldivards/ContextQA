from typing import Literal

from contextqa import settings as app_settings
from contextqa.models import VectorStoreSettings, ModelSettings, Extra


def _check_local_store_args(store_settings: VectorStoreSettings | None) -> VectorStoreSettings:
    store_settings = store_settings or VectorStoreSettings(
        store="chroma", chunk_size=1000, overlap=200, store_params={}
    )
    if store_settings.store == "chroma":
        if "home" not in store_settings.store_params:
            store_settings.store_params["home"] = app_settings.local_vectordb_home
        if "collection" not in store_settings.store_params:
            store_settings.store_params["collection"] = app_settings.default_collection
        return store_settings
    return store_settings


def _config_manager():
    """Config manager closure"""
    settings = app_settings.model_settings

    def config_manager(
        kind: Literal["model", "store", "extra"] = "model", **kwargs
    ) -> ModelSettings | VectorStoreSettings | Extra:
        """Manage settings. Note that this utility can be used either to get or set settings.

        Possible use cases are listed below:

        - Read settings: get_or_set()
        - Write settings: get_or_set(**my_settings)

        Both read and write return the latest settings

        Returns
        -------
        ModelSettings | VectorStoreSettings | Extra
        """
        nonlocal settings
        if not kwargs:
            if kind == "store":
                settings_ = _check_local_store_args(settings.store)
                return settings_
            return getattr(settings, kind)
        if not getattr(settings, kind):
            setattr(settings, kind, kwargs)
        else:
            specific_settings: VectorStoreSettings | ModelSettings = getattr(settings, kind)
            new_settings = specific_settings.__class__.model_validate(specific_settings.model_dump() | kwargs)
            setattr(settings, kind, new_settings)
        app_settings.model_settings = settings
        return getattr(settings, kind)

    return config_manager


get_or_set = _config_manager()
