from typing import Annotated

from fastapi import File, UploadFile, APIRouter

router = APIRouter(
    prefix="/upload",
    tags=['Upload file'],
    
)


@router.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.size}