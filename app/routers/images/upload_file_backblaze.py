import shutil
import random
import string
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from fastapi.responses import JSONResponse
from app.config.config import settings
import os



info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", settings.backblaze_id, settings.backblaze_key)

router = APIRouter(
    prefix="/upload-to-backblaze",
    tags=['Upload file'],
)

def generate_random_suffix(length=8):
    """
    Генерує випадковий суфікс з букв і цифр.

    Parameters:
    length (int): Довжина суфіксу. Значення за замовчуванням - 8.

    Returns:
    str: Випадковий суфікс.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def generate_unique_filename(filename):
    """
    Генерує унікальну назву файлу, додаючи випадковий суфікс.

    Parameters:
    filename (str): Назва файлу.

    Returns:
    str: Унікальна назва файлу.
    """
    file_name, file_extension = os.path.splitext(filename)
    unique_suffix = generate_random_suffix()
    unique_filename = f"{file_name}_{unique_suffix}{file_extension}"
    return unique_filename

@router.post("/chat")
async def upload_to_backblaze(file: UploadFile = File(..., limit="25MB"),
                              bucket_name: str = Query("chatall")):

    try:
   
        with NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        

        bucket = b2_api.get_bucket_by_name(bucket_name)
        

        unique_filename = generate_unique_filename(file.filename)
        
 
        bucket.upload_local_file(
            local_file=temp_file_path,
            file_name=unique_filename
        )
 
        download_url = b2_api.get_download_url_for_file_name(bucket_name, unique_filename)
        return JSONResponse(status_code=200, content={"url": download_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))