from contextqa import settings as app_settings
from contextqa.models import SettingsSchema


def _config_manager():
    """Config manager closure"""
    settings: SettingsSchema = app_settings.model_settings

    def config_manager(**kwargs) -> SettingsSchema:
        """Manage settings. Note that this utility can be used either to get or set settings.

        Possible use cases are listed below:

        - Read settings: get_or_set()
        - Write settings: get_or_set(**my_settings)

        Both read and write return the latest settings

        Returns
        -------
        SettingsSchema
        """
        nonlocal settings
        if not kwargs:
            return settings
        settings.update(kwargs)
        app_settings.model_settings = settings
        return settings

    return config_manager


get_or_set = _config_manager()
