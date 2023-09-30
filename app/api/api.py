from fastapi import APIRouter

from app.api.endpoints import example

api = APIRouter()

api.include_router(example.api, tags=["example"], prefix="/example")
