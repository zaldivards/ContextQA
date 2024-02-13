from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from contextqa import context, get_logger
from contextqa.models.schemas import LLMContextQueryRequest

LOGGER = get_logger()


router = APIRouter()


@router.post("/")
async def qa(params: LLMContextQueryRequest):
    """
    Perform a QA process against the documents you have ingested
    """
    try:
        context_setter = context.get_setter()
        generator = context_setter.load_and_respond(params.question)
        return StreamingResponse(generator, media_type="text/event-stream")
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex
