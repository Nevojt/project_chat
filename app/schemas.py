from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class PostBase(BaseModel):
    name: str
    message: str
    published: bool = True
    member_id: Optional[int]
    avatar: str
    is_privat: bool = False
    receiver: Optional[int]
    
    
class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
        
class UserCreate(BaseModel):
    user_name: str
    token: int
    
    #  response no password
class UserOut(BaseModel):
    id: int
    user_name: str
    created_at: datetime
    token: int
    class Config:
        from_attributes = True

