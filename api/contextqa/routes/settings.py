# pylint: disable=C0413
from shutil import copytree
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from contextqa.models import ModelSettingsUpdate, ModelSettings
from contextqa.models.schemas import (
    ModelSettingsDetail,
    ProviderDetail,
    StoreSettingsUpdate,
    StoreSettings,
    ExtraSettings,
    ExtraSettingsUpdate,
)
from contextqa import settings as app_settings, logger
from contextqa.utils.settings import get_or_set
from contextqa.routes.dependencies import get_db
from contextqa.services.settings import db_has_changed
from contextqa.utils.migrations.settings import migrate_db

router = APIRouter()


@router.get("/model", response_model=ModelSettingsDetail)
async def get_model_settings():
    """Get model settings"""
    try:
        settings = get_or_set()
        return ModelSettingsDetail(
            **settings.model_dump(),
            provider_options=[
                ProviderDetail(provider="openai", models=["gpt-3.5-turbo", "gpt-4"]),
                ProviderDetail(provider="huggingface", models=["tiiuae/falcon-7b-instruct"]),
                ProviderDetail(provider="google", models=["gemini-pro"]),
            ],
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.patch("/model", response_model=ModelSettings)
async def update_model_settings(settings: ModelSettingsUpdate):
    """Update model settings"""
    try:
        partial_model = settings.model_dump(exclude_unset=True, exclude_none=True)
        updated_settings = get_or_set(**partial_model)
        return ModelSettings(
            provider=updated_settings.provider,
            model=updated_settings.model,
            temperature=updated_settings.temperature,
            local=updated_settings.local,
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.get("/store", response_model=StoreSettings)
async def get_store_settings():
    """Get store settings"""
    try:
        settings = get_or_set(kind="store")
        store_params = settings.store_params.copy()
        store_params.pop("token", None)
        return StoreSettings(**(settings.model_dump() | {"store_params": store_params}))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.patch("/store", response_model=StoreSettings)
async def update_store_settings(settings: StoreSettingsUpdate):
    """Update model settings"""
    try:
        current_settings = get_or_set(kind="store")
        # If the token is not in the received settings, do not overwrite the existing one with a None value
        if not settings.store_params.get("token") and settings.store == "pinecone":
            settings.store_params["token"] = current_settings.store_params.get("token")
        partial_model = settings.model_dump(exclude_unset=True, exclude_none=True)
        updated_settings = get_or_set(kind="store", **partial_model)
        store_params = updated_settings.store_params.copy()
        store_params.pop("token", None)
        return StoreSettings(**(updated_settings.model_dump() | {"store_params": store_params}))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.get("/extra", response_model=ExtraSettings)
async def get_extra_settings():
    """Get extra settings"""
    try:
        settings = get_or_set(kind="extra")
        return ExtraSettings(**settings.model_dump())
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.patch("/extra", response_model=ExtraSettings)
async def update_extra_settings(settings: ExtraSettingsUpdate, session: Annotated[Session, Depends(get_db)]):
    """Update extra settings"""
    try:
        current_settings: ExtraSettings = get_or_set(kind="extra")
        partial_model = settings.model_dump(exclude_unset=True, exclude_none=True)
        received_settings = ExtraSettings(**partial_model)
        updated_settings: ExtraSettings = get_or_set(kind="extra", **partial_model)
        if db_has_changed(current_settings, received_settings):
            app_settings.rebuild_sqlalchemy_url()
            migrate_db(session, app_settings.sqlalchemy_url)
        if current_settings.media_dir != received_settings.media_dir:
            logger.info(
                "Media dir changed, copying  content from %s to %s",
                current_settings.media_dir,
                received_settings.media_dir,
            )
            copytree(current_settings.media_dir, received_settings.media_dir, dirs_exist_ok=True)
        return ExtraSettings(**updated_settings.model_dump(exclude_unset=True, exclude_none=True))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.get("/init-status", tags=["Alive?"])
def init_status():
    """Check whether the api has already been initialized"""
    settings = get_or_set()
    return "ok" if settings.provider else "pending"
