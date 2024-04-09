from fastapi import APIRouter, File, UploadFile
from supabase import create_client, Client
from app.config.config_supabase import settings
import re

# Налаштування Supabase
url: str = settings.supabase_url
key: str = settings.supabase_key
supabase: Client = create_client(url, key)

router = APIRouter(
    prefix="/upload",
    tags=['Upload file'],
)

def generate_new_name(existing_files, original_filename):
    """
    Generate a new file name if the given name already exists in the list of existing files.

    Args:
        existing_files (list): A list of existing file names in the storage.
        original_filename (str): The original file name.

    Returns:
        str: The new file name if the original exists, otherwise the original filename.
    """
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
    res = supabase.storage.from_(bucket_name).get_public_url(file_path)
    return res

@router.post("/upload-to-supabase/")
async def upload_to_supabase(file: UploadFile = File(..., limit="10MB"), bucket_name: str = "image_chat"):
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
        existing_files = [f['name'] for f in supabase.storage.from_(bucket_name).list()]

        # Generate a new name if the file already exists
        file_path = generate_new_name(existing_files, file.filename)
        file_mime_type = file.content_type
        contents = await file.read()

        # Upload the file
        upload_response = supabase.storage.from_(bucket_name).upload(file_path, contents, file_options={"contentType": file_mime_type})
        
        return public_url(bucket_name, file_path)

    except Exception as error:
        return {"error": str(error)}