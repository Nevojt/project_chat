from fastapi import File, UploadFile, APIRouter
from supabase import create_client, Client
from app.config.config_supabase import settings

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import models
from app.schemas import image



url: str = settings.supabase_url
key: str = settings.supabase_key
supabase: Client = create_client(url, key)

router = APIRouter(
    prefix="/upload",
    tags=['Upload file'],  
)

# Upload to server and database images for avatars
def public_url(bucket_name, file_path):
    res = supabase.storage.from_(bucket_name).get_public_url(file_path)
    return res

async def create_image_avatars(images: image.UploadAvatar, db: Session = Depends(get_db)):
 
    images = models.ImagesAvatar(**images.model_dump())
    db.add(images)
    db.commit()
    db.refresh(images)    
    return images


@router.post("/upload-avatar")
async def upload_to_avatars(name: str, 
                            file: UploadFile = File(...), 
                            db: Session = Depends(get_db), 
                            bucket_name: str = "image_avatars"):
    """
    Upload a file to supabase storage and add its URL to the database.
    """
    try:
        # download the image
        file_path = file.filename
        file_mime_type = file.content_type
        contents = await file.read()

        upload_response = supabase.storage.from_(bucket_name).upload(file_path, contents, file_options={"contentType": file_mime_type})
        
        # get published url
        public_url_response = public_url(bucket_name, file_path)

        # created object and upload to database
        image_data = {"images_url": public_url_response, "avatar": name}
        saved_image = await create_image_avatars(image.UploadAvatar(**image_data), db)

        # return list of images
        return saved_image

    except Exception as error:
        return {"error": str(error)}
    
    
    
# Upload to server and database images for rooms
async def create_image_rooms(images: image.UploadRooms, db: Session = Depends(get_db)):
 
    images = models.ImagesRooms(**images.model_dump())
    db.add(images)
    db.commit()
    db.refresh(images)    
    return images

    
@router.post("/upload-rooms")
async def upload_to_rooms(name: str,
                        file: UploadFile = File(...),
                        db: Session = Depends(get_db),
                        bucket_name: str = "image_rooms"):

    try:
        # download the image
        file_path = file.filename
        file_mime_type = file.content_type
        contents = await file.read()

        upload_response = supabase.storage.from_(bucket_name).upload(file_path, contents, file_options={"contentType": file_mime_type})
        
        # get published url
        public_url_response = public_url(bucket_name, file_path)

        # created object and upload to database
        image_data = {"images_url": public_url_response, "rooms": name}
        saved_image = await create_image_rooms(image.UploadRooms(**image_data), db)

        # return list of images
        return saved_image

    except Exception as error:
        return {"error": str(error)}