# pylint: disable=C0413
from fastapi import APIRouter, HTTPException, status

from contextqa.models import (
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
        settings = get_or_set()
        return ModelSettingsDetail(
            **settings.model_dump(),
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
async def update_store_settings(settings: StoreSettings):
    """Update model settings"""
    try:
        current_settings = get_or_set(kind="store")
        # If the token is not in the received settings, do not overwrite the existing one with a None value
        if not settings.store_params.get("token") and settings.store == "pinecone":
            settings.store_params["token"] = current_settings.store_params.get("token")
        partial_model = settings.model_dump(exclude_unset=True, exclude_none=True)
        updated_settings = get_or_set(kind="store", **partial_model)
        store_params = updated_settings.store_params.copy()
        store_params.pop("token")
        return StoreSettings(**(updated_settings.model_dump() | {"store_params": store_params}))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex
