import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter
from pydantic import BaseModel, FilePath
from fastapi.responses import FileResponse, StreamingResponse, Response
from pathlib import Path
from database.s3 import s3_client
from contextlib import AsyncExitStack

photo_router = APIRouter()

@photo_router.get("/", summary="Начальная страница")
async def home():
    return {"message": "Hello World!!"}

@photo_router.get(
    "/photos",
    summary="Получение всех фото"
)
async def fetch_photos():
    result = await s3_client.get_all_objects()
    return result

@photo_router.get(
    "/photos/{photo_id}",
    summary="Получение фото по id"
)
async def get_photo(photo_id: str):
    exit_stack = AsyncExitStack()

    response = await exit_stack.enter_async_context(
        s3_client.get_streaming_object(photo_id)
    )

    return StreamingResponse(
        response["Body"].iter_chunks(),
        media_type=response.get("ContentType", "image/jpeg"),
        background=exit_stack.aclose
    )

@photo_router.post(
    "/upload",
    summary="Добавлине фото"
)
async def upload(file: UploadFile = File(...)):
    print(type(file))
    await s3_client.upload_object(file)
    return {"message": "Success"}
