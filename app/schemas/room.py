
from pydantic import BaseModel, ConfigDict      #, HttpUrl
from datetime import datetime
from typing import Optional, List




class RoomBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    owner: int
    name_room: str
    image_room: str
    count_users: int
    count_messages: int
    created_at: datetime
    secret_room: bool
    block: Optional[bool] = None
        
class RoomFavorite(RoomBase):
    favorite: bool
    
    
class RoomCreate(BaseModel):
    name_room: str
    image_room: str
    secret_room: bool = False

class RoomPost(RoomBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

        
class RoomUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name_room: str
    image_room: str
    owner: int
    created_at: datetime
    secret_room: Optional[Optional[bool]]
       
        
class RoomManager(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    room_id: int
    
        
class RoomTabsCreate(BaseModel):
    name_tab: Optional[str] = None
    image_tab: Optional[str] = None
    
class TabUpdate(RoomTabsCreate):
    pass 
    
    
class Tab(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    rooms: List[RoomBase]
    



class CountMessages(BaseModel):
    rooms: str
    count: int
    
class CountUsers(BaseModel):
    rooms: str
    count: int