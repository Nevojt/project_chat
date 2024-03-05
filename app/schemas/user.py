
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from ..models.models import UserRole
        
        
        
class UserOut(BaseModel):
    id: int
    user_name: str
    avatar: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        
        
class UserStatus(BaseModel):
    room_name: str
    user_name: str
    user_id: int
    status: bool = True
   
    
class UserStatusCreate(UserStatus):
    pass


class UserStatusUpdate(BaseModel):
    name_room: str
    status: bool = True


class UserStatusPost(UserStatus):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
     
           
class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    password: str
    avatar: str
    verified: bool = Field(False)
    role: UserRole = UserRole.user
   
    
class UserUpdate(BaseModel):
    user_name: str
    avatar: str
    
    class Config:
        from_attributes = True
        
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str
      
      
class UserInfo(BaseModel):
    id: int
    email: str
    user_name: str
    avatar: str
    created_at: datetime
    
    class Config:
        from_attributes = True