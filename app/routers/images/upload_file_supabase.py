from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from fastapi.responses import JSONResponse
from storage3 import create_client
from app.config.config import settings
import re
# https://tygjaceleczftbswxxei.supabase.co/storage/v1/s3
# Налаштування Supabase
url: str = f"{settings.supabase_url}/storage/v1"
key: str = settings.supabase_key

# Створення клієнта для Supabase Storage
headers = {"apiKey": key, "Authorization": f"Bearer {key}"}
storage_client = create_client(url, headers, is_async=False)

# Список бакетів для перевірки з'єднання
storage_client.list_buckets()
# print(buckets)


router = APIRouter(
    prefix="/upload",
    tags=['Upload file'],
)


def generate_new_name(existing_files, original_filename):
    if original_filename not in existing_files:
        return original_filename

    name, extension = re.match(r"(.*?)(\.[^.]*$|$)", original_filename).groups()
    counter = 1
    new_filename = f"{name}_{counter}{extension}"

    while new_filename in existing_files:
        counter += 1
        new_filename = f"{name}_{counter}{extension}"

    return new_filename

def public_url(bucket_name, file_path):
    res = storage_client.from_(bucket_name).get_public_url(file_path)
    return res

@router.post("/upload-to-supabase/")
async def upload_to_supabase(file: UploadFile = File(..., limit="25MB"), bucket_name: str = "image_chat"):
    """
    Upload a file to Supabase storage, ensuring unique file names.

    Args:
        file (UploadFile): The file to be uploaded.
        bucket_name (str): The name of the Supabase storage bucket.

    Returns:
        str: The public URL of the uploaded file, or an error message.
    """
    try:
        # List existing files in the bucket
        existing_files = [f['name'] for f in storage_client.from_(bucket_name).list()]

        # Generate a new name if the file already exists
        # file_path = generate_new_name(existing_files, file.filename)
        file_mime_type = file.content_type
        contents = await file.read()

        # Upload the file
        upload_response = storage_client.from_(bucket_name).upload(file.filename, contents, file_options={"contentType": "image/png"})
        
        return public_url(bucket_name, file.filename)

    except Exception as error:
        return {"error": str(error)}
    
# @router.post("/upload-to-supabase/avatars")
# async def upload_to_supabase_user_avatars(file: UploadFile = File(..., limit="15MB"), bucket_name: str = "user_avatars"):
#     """
#     Upload a file to Supabase storage, ensuring unique file names.

#     Args:
#         file (UploadFile): The file to be uploaded.
#         bucket_name (str): The name of the Supabase storage bucket.

#     Returns:
#         str: The public URL of the uploaded file, or an error message.
#     """
#     try:
#         # List existing files in the bucket
#         existing_files = [f['name'] for f in supabase.storage.from_(bucket_name).list()]

#         # Generate a new name if the file already exists
#         file_path = generate_new_name(existing_files, file.filename)
#         file_mime_type = file.content_type
#         contents = await file.read()

#         # Upload the file
#         upload_response = supabase.storage.from_(bucket_name).upload(file_path, contents, file_options={"contentType": file_mime_type})
        
#         return public_url(bucket_name, file_path)

#     except Exception as error:
#         return {"error": str(error)}