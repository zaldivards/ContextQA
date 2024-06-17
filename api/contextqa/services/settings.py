from contextqa.models.schemas import ExtraSettings


def db_has_changed(current_settings: ExtraSettings, new_settings: ExtraSettings) -> bool:
    """Check if the database settings have changed

    Parameters
    ----------
    current_settings : ExtraSettings
        The current database settings
    new_settings : ExtraSettings
        The new database settings

    Returns
    -------
    bool
        True if the database settings have changed, False otherwise
    """
    return (
        (current_settings.database.url and current_settings.database.credentials)
        or current_settings.database.url != new_settings.database.url
        or current_settings.database.credentials != new_settings.database.credentials
    )
