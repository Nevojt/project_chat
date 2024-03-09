
from pydantic import BaseModel
from datetime import datetime
from typing import Optional




class RoomBase(BaseModel):
    id: int
    owner: int
    name_room: str
    image_room: str
    count_users: int
    count_messages: int
    created_at: datetime
    private: bool

    class Config:
        from_attributes = True
        
class RoomFavorite(RoomBase):
    favorite: bool
    
    
class RoomCreate(BaseModel):
    name_room: str
    image_room: str
    private: bool = False

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
    private: Optional[Optional[bool]]
    
    class Config:
        from_attributes = True
        
        
class RoomManager(BaseModel):
    room_id: int
    
    class Config:
        from_attributes = True
        

class CountMessages(BaseModel):
    rooms: str
    count: int
    
class CountUsers(BaseModel):
    rooms: str
    count: int