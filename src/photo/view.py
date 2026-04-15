from fastapi import UploadFile, File, APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.database.s3 import S3Client, get_s3_client
from contextlib import AsyncExitStack


photo_router = APIRouter()

@photo_router.get("/", summary="Начальная страница")
async def home():
    return {"message": "Hello World!!"}

@photo_router.get(
    "/photos",
    summary="Получение всех фото"
)
async def fetch_photos(
        s3: S3Client = Depends(get_s3_client)
):
    result = await s3.get_all_objects()
    print(result)
    return result

@photo_router.get(
    "/photos/{photo_id}",
    summary="Получение фото по id"
)
async def get_photo(photo_id: str):
    exit_stack = AsyncExitStack()

    response = await exit_stack.enter_async_context(
        s3_photo.get_streaming_object(photo_id)
    )

    return StreamingResponse(
        response["Body"].iter_chunks(),
        media_type=response.get("ContentType", "image/jpeg"),
        background=exit_stack.aclose
    )

@photo_router.post(
    "/upload",
    summary="Добавление фото"
)
async def upload_photo(
        file: UploadFile = File(...),
        s3: S3Client = Depends(get_s3_client)
):
    await s3.upload_object(file)
    return {"message": "Success"}

@photo_router.delete(
    "/delete/{photo_id}",
    summary="Удаление фото"
)
async def delete_photo(
        photo_id: str,
        s3: S3Client = Depends(get_s3_client)
):
    await s3.delete_object(photo_id)
    return {"message": "Success"}