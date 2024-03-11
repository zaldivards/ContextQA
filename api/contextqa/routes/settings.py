# pylint: disable=C0413
from fastapi import APIRouter, HTTPException, status

from contextqa.models.schemas import (
    ModelSettingsDetail,
    ProviderDetail,
    ModelSettingsUpdate,
    ModelSettings,
    StoreSettings,
)
from contextqa.utils.settings import get_or_set

router = APIRouter()


@router.get("/model", response_model=ModelSettingsDetail)
async def get_model_settings():
    """Get model settings"""
    try:
        return ModelSettingsDetail(
            **get_or_set(),
            provider_options=[
                ProviderDetail(provider="openai", models=["gpt-3.5-turbo", "gpt-4"]),
                ProviderDetail(provider="huggingface", models=["tiiuae/falcon-7b-instruct"]),
                ProviderDetail(provider="google", models=["gemini"]),
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
        return ModelSettings(**get_or_set(**partial_model))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.get("/store", response_model=StoreSettings)
async def get_store_settings():
    """Get store settings"""
    try:
        return StoreSettings(**get_or_set(kind="store"))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.patch("/store", response_model=StoreSettings)
async def update_store_settings(settings: StoreSettings):
    """Update model settings"""
    try:
        partial_model = settings.model_dump(exclude_unset=True, exclude_none=True)
        return StoreSettings(**get_or_set(kind="store", **partial_model))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex
