from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class PostBase(BaseModel):
    name: str
    message: str
    published: bool = True
    
    
class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True
        
class UserCreate(BaseModel):
    user_name: EmailStr  # Email address
    password: str
    
    #  response no password
class UserOut(BaseModel):
    id: int
    user_name: EmailStr # Email address
    created_at: datetime
    class Config:
        orm_mode = True
    
    
class UserLogin(BaseModel):
    user_name: EmailStr # Email address
    password: str
    
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[str] = None