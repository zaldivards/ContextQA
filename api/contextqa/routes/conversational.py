# pylint: disable=C0413
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse

from contextqa import chat
from contextqa.models import PartialModelData
from contextqa.models.schemas import LLMQueryRequest
from contextqa.routes.dependencies import get_partial_initialized_model

router = APIRouter()


@router.post("/")
async def get_answer(
    params: LLMQueryRequest,
    partial_model_data: Annotated[PartialModelData, Depends(get_partial_initialized_model)],
):
    """
    Provide a message and receive a response from the LLM
    """
    try:
        generator = chat.qa_service(params, partial_model_data)
        return StreamingResponse(generator, media_type="text/event-stream")
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY, detail={"message": "Something went wrong", "cause": str(ex)}
        ) from ex
