
from fastapi import File, UploadFile, APIRouter
from google.cloud import storage
from mimetypes import guess_type
import os
import re

router = APIRouter(
    prefix="/upload_google",
    tags=['Upload file'],
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sinuous-grove-405612-a7d9d516c960.json"
BUCKET_NAME="chatbuscket"


def generate_new_name(bucket, original_blob_name):
    """Генерує нове ім'я файлу, якщо воно вже існує."""
    counter = 1
    blob_name = original_blob_name
    while bucket.blob(blob_name).exists():
        # Розділяємо ім'я файлу та його розширення
        name, extension = re.match(r"(.*?)(\.[^.]*$|$)", original_blob_name).groups()
        # Додаємо лічильник до імені файлу
        blob_name = f"{name}_{counter}{extension}"
        counter += 1
    return blob_name


def upload_to_gcs(bucket_name, file_stream, blob_name):
    """Завантажує файл у Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # Перевіряємо, чи файл вже існує, і змінюємо ім'я, якщо потрібно
    blob_name = generate_new_name(bucket, blob_name)
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