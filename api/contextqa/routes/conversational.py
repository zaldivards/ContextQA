# pylint: disable=C0413
from fastapi import APIRouter, HTTPException, status

from contextqa import chat
from contextqa.models.schemas import (
    LLMResult,
    LLMQueryRequest,
)

router = APIRouter()


@router.post("/", response_model=LLMResult)
def get_answer(params: LLMQueryRequest):
    """
    Provide a message and receive a response from the LLM
    """
    try:
        return chat.qa_service(params)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY, detail={"message": "Something went wrong", "cause": str(ex)}
        ) from ex
