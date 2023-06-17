from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

load_dotenv()

# pylint: disable=C0413
from retriever import models, social_media, vector

app = FastAPI(title="LLM Retriever", openapi_url="/openapi.json", docs_url="/docs", redoc_url="/redoc")


@app.get("/social-media", response_model=models.Summary)
def get_user_info(name: str = Query(min_length=4)):
    try:
        return social_media.seach_user_info(name)
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


@app.post("/context-query", response_model=models.VectorScanResult)
def query_llm(params: models.LLMQueryRequestBody):
    try:
        return vector.simple_scan(params)
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex
