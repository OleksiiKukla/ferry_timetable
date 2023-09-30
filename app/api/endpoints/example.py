from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.core.config import settings

api = APIRouter()


@api.get("/")
async def get_example_response() -> JSONResponse:
    print(settings.REDIS_URI)
    return JSONResponse({"example": "Hi, teammates!"})


# @api.get("/celery")
# async def get_example_celery() -> dict:
#     result = print_hello.delay()
#     return {"task_id": result.id}
