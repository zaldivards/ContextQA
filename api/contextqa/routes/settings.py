# pylint: disable=C0413
from fastapi import APIRouter, HTTPException, status

from contextqa.models.schemas import SettingsDetail, PlatformDetail, SettingsUpdate, Settings
from contextqa.utils.settings import get_or_set

router = APIRouter()


@router.get("/", response_model=SettingsDetail)
async def get_settings():
    """
    Provide a message and receive a response from the LLM
    """
    try:
        return SettingsDetail(
            **get_or_set(),
            platforms_options=[
                PlatformDetail(platform="openai", models=["gpt-3.5-turbo", "gpt-4"]),
                PlatformDetail(platform="huggingface", models=["tiiuae/falcon-7b-instruct"]),
                PlatformDetail(platform="google", models=["gemini"]),
            ]
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex


@router.put("/", response_model=Settings)
async def update_settings(settings: SettingsUpdate):
    """
    Provide a message and receive a response from the LLM
    """
    try:
        return Settings(**get_or_set(**settings.model_dump()))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Something went wrong", "cause": str(ex)},
        ) from ex
