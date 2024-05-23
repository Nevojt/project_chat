from b2sdk.v2 import InMemoryAccountInfo, B2Api
from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from fastapi.responses import JSONResponse
from storage3 import create_client
from app.config.config import settings
import re



info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", "003272b811b571d0000000001", "K003+fdiPfTf46F43X456LPkKadlPtI")

router = APIRouter(
    prefix="/upload-to-backblaze",
    tags=['Upload file'],
)

@router.post("/upload")
async def upload_to_backblaze(file: UploadFile = File(..., limit="25MB"), bucket_name: str = "chatall"):
    
    bucket = b2_api.get_bucket_by_name(bucket_name)
    file_path = file.filepath
    file_name = 'example_file.txt'
    bucket.upload_local_file(
        local_file=file_path,
        file_name=file_name
    )
    print("File uploaded successfully.")
