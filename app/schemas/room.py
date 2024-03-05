
from pydantic import BaseModel
from datetime import datetime




class RoomBase(BaseModel):
    id: int
    name_room: str
    image_room: str
    count_users: int
    count_messages: int
    created_at: datetime

    class Config:
        from_attributes = True
    
    
class RoomCreate(BaseModel):
    name_room: str
    image_room: str

class RoomPost(RoomBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        
class RoomUpdate(BaseModel):
    id: int
    name_room: str
    image_room: str
    owner: int
    created_at: datetime
    
    class Config:
        from_attributes = True
        

class CountMessages(BaseModel):
    rooms: str
    count: int
    
class CountUsers(BaseModel):
    rooms: str
    count: int