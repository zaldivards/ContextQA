from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from langchain_core.language_models.chat_models import BaseChatModel

from contextqa.models.schemas import LLMContextQueryRequest
from contextqa.routes.dependencies import get_initialized_model, context_manager
from contextqa.services.context import LLMContextManager


router = APIRouter()


@router.post("/")
async def qa(
    params: LLMContextQueryRequest,
    model: Annotated[BaseChatModel, Depends(get_initialized_model)],
    manager: Annotated[LLMContextManager, Depends(context_manager)],
):
    """QA process using the ingested sources"""
    try:
        generator = manager.load_and_respond(params.question, model)
        return StreamingResponse(generator, media_type="text/event-stream")
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex
