
from fastapi import File, UploadFile, APIRouter
from supabase import create_client, Client
from app.config.config_supabase import settings


url: str = settings.supabase_url
key: str = settings.supabase_key
supabase: Client = create_client(url, key)

router = APIRouter(
    prefix="/upload",
    tags=['Upload file'],  
)


def public_url(bucket_name, file_path):
    res = supabase.storage.from_(bucket_name).get_public_url(file_path)
    return res

@router.post("/upload-to-supabase/")
async def upload_to_supabase(file: UploadFile = File(..., limit="5MB"),
                             bucket_name: str = "image_chat"):
    """
    This function is used to upload a file to supabase storage.

    Args:
        file (UploadFile): The file to be uploaded.
        bucket_name (str): The name of the bucket where the file should be uploaded.

    Returns:
        str: The public URL of the uploaded file.

    Raises:
        Exception: If there is an error during the upload process.
    """
    try:
        file_path = file.filename
        file_mime_type = file.content_type
        contents = await file.read()

        upload_response = supabase.storage.from_(bucket_name).upload(file_path, contents, file_options={"contentType": file_mime_type})
        
        return public_url(bucket_name, file_path)

    except Exception as error:
        return {"error": str(error)}





