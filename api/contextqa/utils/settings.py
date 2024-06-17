from typing import Literal

from contextqa import settings as app_settings
from contextqa.models import VectorStoreSettings, ModelSettings, Extra


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
            return getattr(settings, kind)
        if not getattr(settings, kind):
            setattr(settings, kind, kwargs)
        else:
            specific_settings: VectorStoreSettings | ModelSettings | Extra = getattr(settings, kind)
            new_settings = specific_settings.__class__.model_validate(specific_settings.model_dump() | kwargs)
            setattr(settings, kind, new_settings)
        app_settings.model_settings = settings
        return getattr(settings, kind)

    return config_manager


get_or_set = _config_manager()
