# pylint: disable=C0413
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from langchain_core.language_models.chat_models import BaseChatModel

from contextqa.models.schemas import LLMQueryRequest
from contextqa.routes.dependencies import get_initialized_model
from contextqa.services import chat

router = APIRouter()


@router.post("/")
async def get_answer(
    params: LLMQueryRequest,
    model: Annotated[BaseChatModel, Depends(get_initialized_model)],
):
    """
    Provide a message and receive a response from the LLM
    """
    try:
        generator = chat.invoke_model(params, model)
        return StreamingResponse(generator, media_type="text/event-stream")
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY, detail={"message": "Something went wrong", "cause": str(ex)}
        ) from ex
