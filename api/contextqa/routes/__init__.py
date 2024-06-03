from fastapi import APIRouter

from contextqa.routes import conversational, qa, sources, settings, status

api_router = APIRouter(prefix="/v2")


api_router.include_router(conversational.router, prefix="/bot", tags=["Conversational"])
api_router.include_router(qa.router, prefix="/qa", tags=["QA"])
api_router.include_router(sources.router, prefix="/sources", tags=["Sources"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(status.router, prefix="/status", tags=["Status"])
