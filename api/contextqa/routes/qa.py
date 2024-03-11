from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse

from contextqa import context
from contextqa.models import PartialModelData
from contextqa.models.schemas import LLMContextQueryRequest
from contextqa.routes.dependencies import get_partial_initialized_model


router = APIRouter()


@router.post("/")
async def qa(
    params: LLMContextQueryRequest,
    partial_model: Annotated[PartialModelData, Depends(get_partial_initialized_model)],
):
    """QA process using the ingested sources"""
    try:
        context_setter = context.get_setter()
        generator = context_setter.load_and_respond(params.question, partial_model)
        return StreamingResponse(generator, media_type="text/event-stream")
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex
