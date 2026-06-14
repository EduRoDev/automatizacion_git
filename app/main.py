from fastapi import FastAPI
import logging
from app.api.webhooks import router as webhook_router

def entry_point() -> FastAPI:
    logging.basicConfig(level="INFO")
    api = FastAPI(title="CodeGuard",version="0.1.0")

    @api.get("/")
    async def health_check():
        return {"status": "ok"}

    api.include_router(webhook_router, prefix="/github", tags=["github"])

    return api

app = entry_point()
