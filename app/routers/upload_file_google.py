
from fastapi import File, UploadFile, APIRouter
from google.cloud import storage
from mimetypes import guess_type
import os

router = APIRouter(
    prefix="/upload_google",
    tags=['Upload file'],
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sinuous-grove-405612-a7d9d516c960.json"
BUCKET_NAME="chatbuscket"

from mimetypes import guess_type
from google.cloud import storage

def upload_to_gcs(bucket_name, file_stream, blob_name):
    """Завантажує файл у Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Визначення MIME-типу файлу
    content_type, _ = guess_type(blob_name)
    if content_type:
        blob.upload_from_file(file_stream, content_type=content_type)
    else:
        blob.upload_from_file(file_stream)

    # Формування постійного публічного URL
    public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"

    return public_url



@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    file_stream = file.file
    blob_name = file.filename
    public_url = upload_to_gcs(BUCKET_NAME, file_stream, blob_name)
    return {"filename": file.filename, "public_url": public_url}










"m8tGPO8NcCj0PZYgEz/7yFS9bxtnbuHvh0FB+y/w"