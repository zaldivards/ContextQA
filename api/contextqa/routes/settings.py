# pylint: disable=C0413
from fastapi import APIRouter, HTTPException, status

from contextqa.models.schemas import SettingsDetail, ProviderDetail, SettingsUpdate, Settings
from contextqa.utils.settings import get_or_set

router = APIRouter()


@router.get("/", response_model=SettingsDetail)
async def get_settings():
    """Get model settings"""
    try:
        return SettingsDetail(
            **get_or_set(),
            provider_options=[
                ProviderDetail(provider="openai", models=["gpt-3.5-turbo", "gpt-4"]),
                ProviderDetail(provider="huggingface", models=["tiiuae/falcon-7b-instruct"]),
                ProviderDetail(provider="google", models=["gemini"]),
            ]
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.patch("/", response_model=Settings)
async def update_settings(settings: SettingsUpdate):
    """Update model settings"""
    try:
        partial_model = settings.model_dump(exclude_unset=True, exclude_none=True)
        return Settings(**get_or_set(**partial_model))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex
