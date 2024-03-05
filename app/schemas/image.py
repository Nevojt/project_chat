
from typing import Optional
from pydantic import BaseModel



class Images(BaseModel):
    images: str
    image_room: str
    
class ImagesCreate(Images):
    pass
       
class ImagesResponse(Images):
    id: Optional[int]

    class Config:
        from_attributes = True