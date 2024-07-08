# pylint: disable=C0413
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from contextqa import settings
from contextqa.routes import api_router
from contextqa.utils.migrations import check_migrations

app = FastAPI(
    title="ContextQA API", openapi_url="/openapi.json", docs_url="/docs", redoc_url="/redoc", lifespan=check_migrations
)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/ping", tags=["Alive?"])
def ping():
    """Test whether the api is up and running"""
    return "Pong!"


app.include_router(api_router, prefix="/api")

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

if settings.deployment == "prod":
    app.mount(
        "/",
        StaticFiles(
            directory=Path(__file__).parent / "ui",
            html=True,
        ),
        name="UI",
    )
