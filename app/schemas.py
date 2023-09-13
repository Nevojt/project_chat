from typing import Optional
from pydantic import BaseModel
from datetime import datetime
        
        
class MessageBase(BaseModel):
    name: str
    message: str
    published: bool = True
    member_id: Optional[int]
    avatar: str
    is_privat: bool = False
    receiver: Optional[int]
    rooms: str
        
        
class MessageCreate(MessageBase):
    pass

class MessagePost(MessageBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
        
        
class RoomBase(BaseModel):
    name_room: str
    
    
class RoomCreate(RoomBase):
    pass

class RoomPost(RoomBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
        
        
        
class UserCreate(BaseModel):
    user_name: str
    password: str
    
    #  response no password
class UserOut(BaseModel):
    id: int
    user_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    user_name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    user_name: Optional[str] = None