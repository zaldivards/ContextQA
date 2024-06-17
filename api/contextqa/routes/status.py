from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from langchain_core.language_models.chat_models import BaseChatModel
from sqlalchemy.orm import Session

from contextqa.routes.dependencies import get_db, get_initialized_model, store_client
from contextqa.models.schemas import ComponentStatus
from contextqa.services.status import get_status
from contextqa.utils.clients import StoreClient

router = APIRouter()


@router.get("/", response_model=list[ComponentStatus])
async def status_(
    session: Annotated[Session, Depends(get_db)],
    model: Annotated[BaseChatModel, Depends(get_initialized_model)],
    client: Annotated[StoreClient | None, Depends(store_client)],
):
    """# ContextQA's components status"""
    try:
        return get_status(session, model, client)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex
