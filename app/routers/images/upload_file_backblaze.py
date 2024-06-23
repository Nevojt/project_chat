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
    Generate a random string of specified length consisting of letters and digits.

    Parameters:
    length (int): The length of the random string to be generated. Default is 8.

    Returns:
    str: A random string of specified length consisting of letters and digits.

    This function uses the `random.choice` method from the `random` module to select
    characters from the `string.ascii_letters` and `string.digits` constants.
    The selected characters are then joined together using the `join` method to form the final random string.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def generate_unique_filename(filename):
    """
    Generate a unique filename by appending a random suffix to the original filename.

    Parameters:
    filename (str): The original filename.

    Returns:
    str: The unique filename.

    The function splits the original filename into its name and extension parts.
    It then generates a random suffix using the `generate_random_suffix` function.
    Finally, it combines the name, suffix, and extension to form the unique filename.
    """
    file_name, file_extension = os.path.splitext(filename)
    unique_suffix = generate_random_suffix()
    unique_filename = f"{file_name}_{unique_suffix}{file_extension}"
    return unique_filename

@router.post("/chat")
async def upload_to_backblaze(file: UploadFile = File(..., limit="25MB")):
    """
    This function handles file uploads to Backblaze B2 storage.

    Parameters:
    file (UploadFile): The file to be uploaded. The file size limit is set to 25MB.
    bucket_name (str): The name of the bucket where the file will be stored.
                        Default value is "chatall".

    Returns:
    JSONResponse: A JSON response containing the download URL of the uploaded file.
                  If an error occurs during the upload process, a HTTPException is raised.

    Raises:
    HTTPException: If an error occurs during the upload process.
    """
    try:
        # Create a temporary file to store the uploaded file
        with NamedTemporaryFile(delete=False) as temp_file:
            # Copy the uploaded file to the temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        bucket_name = "chatall"
        # Get the bucket by name
        bucket = b2_api.get_bucket_by_name(bucket_name)

        # Generate a unique filename for the uploaded file
        unique_filename = generate_unique_filename(file.filename)

        # Upload the local file to the bucket
        bucket.upload_local_file(
            local_file=temp_file_path,
            file_name=unique_filename
        )

        # Get the download URL for the uploaded file
        download_url = b2_api.get_download_url_for_file_name(bucket_name, unique_filename)
        return JSONResponse(status_code=200, content=download_url)
    except Exception as e:
        # Raise a HTTPException with a 500 status code and the error message
        raise HTTPException(status_code=500, detail=str(e))