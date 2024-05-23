import shutil
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from fastapi.responses import JSONResponse
from app.config.config import settings




info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", settings.backblaze_id, settings.backblaze_key)

router = APIRouter(
    prefix="/upload-to-backblaze",
    tags=['Upload file'],
)
bucket = ["chatall", "usravatar"]
@router.post("/chat")
async def upload_to_backblaze(file: UploadFile = File(..., limit="25MB"), bucket_name: str = Query("chatall", inclusion=bucket)):
    """
    This function is responsible for uploading a file to a specified Backblaze B2 bucket.

    Parameters:
    file (UploadFile): The file to be uploaded. The file size limit is set to 25MB.
    bucket_name (str): The name of the Backblaze B2 bucket to upload the file to. The default value is "chatall".
                        Download avatars: bucket -> "usravatar"
                        The bucket_name must be one of the values in the 'bucket' list.

    Returns:
    JSONResponse: A JSON response containing the public URL of the uploaded file.
                  If an error occurs during the upload process, a HTTPException is raised with a 500 status code.

    Raises:
    HTTPException: If an error occurs during the upload process.
    """
    try:
        # Створення тимчасового файлу
        with NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # get backed
        bucket = b2_api.get_bucket_by_name(bucket_name)
        
        # Download file Backblaze B2
        bucket.upload_local_file(
            local_file=temp_file_path,
            file_name=file.filename
        )
        # Generate public URL
        download_url = b2_api.get_download_url_for_file_name(bucket_name, file.filename)
        return JSONResponse(status_code=200, content={"url": download_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))