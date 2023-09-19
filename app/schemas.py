from typing import Optional
from pydantic import BaseModel
from datetime import datetime
        
        
class MessageBase(BaseModel):
    name: str
    message: str
    avatar: str
    is_privat: bool = False
    receiver: Optional[int]
    rooms: str
    
    
class MessageCreate(MessageBase):
    pass


class UserOut(BaseModel):
    id: int
    user_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        

class MessagePost(MessageBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    
    class Config:
        from_attributes = True
        
        
        
        
        
class RoomBase(BaseModel):
    name_room: str
    image_room: str
    
    
class RoomCreate(RoomBase):
    pass

class RoomPost(RoomBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        



        
class UserStatus(BaseModel):
    id: int
    room_name: str
    user_name: str
    user_id: int
    status: bool = True
    
class UserStatusCreate(UserStatus):
    pass

class UserStatusPost(UserStatus):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
    
        
        
        
class UserCreate(BaseModel):
    user_name: str
    password: str
    
        
class UserLogin(BaseModel):
    user_name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[int] = None