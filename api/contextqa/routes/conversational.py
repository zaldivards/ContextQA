# pylint: disable=C0413
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from contextqa import chat
from contextqa.models.schemas import LLMQueryRequest

router = APIRouter()


@router.post("/")
async def get_answer(params: LLMQueryRequest):
    """
    Provide a message and receive a response from the LLM
    """
    try:
        generator = chat.qa_service(params)
        return StreamingResponse(generator, media_type="text/event-stream")
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY, detail={"message": "Something went wrong", "cause": str(ex)}
        ) from ex
