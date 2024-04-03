
from typing import Optional
from pydantic import BaseModel



class Images(BaseModel):
    images: str
    image_room: str
    
class ImagesCreate(Images):
    pass
      
class UploadAvatar(BaseModel):
    avatar: str
    images_url: str 

class UploadRooms(BaseModel):
    rooms: str
    images_url: str    
       
class ImagesResponse(Images):
    id: Optional[int]

    class Config:
        from_attributes = True