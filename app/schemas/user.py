
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
        
        
        
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_name: str
    avatar: str
    created_at: datetime
        
        
class UserStatus(BaseModel):
    room_name: str
    user_name: str
    user_id: int
    status: bool = True
    room_id: int
   
    
class UserStatusCreate(UserStatus):
    pass


class UserStatusUpdate(BaseModel):
    name_room: str
    status: bool = True


class UserStatusPost(UserStatus):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
     
           
class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    password: str
    avatar: str
   
class UserCreateV2(BaseModel):
    email: EmailStr
    user_name: str
    password: str
    
class UserCreateDel(UserCreate):
    verified: bool
    
class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_name: str
    avatar: str
        
class UserUpdateAvatar(BaseModel):
    avatar: str
        
class UserUpdateUsername(BaseModel):
    user_name: str
            
class UserLogin(BaseModel):
    email: EmailStr
    password: str
      
      
class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    user_name: str
    avatar: str
    created_at: datetime
    role: Optional[str]
    verified: bool
    blocked: bool
    token_verify: Optional[str] = None
    
class UserInfoLights(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    user_name: str
    avatar: str
    verified: bool
    active: bool
    
class UserDelete(BaseModel):
    password: str
    
class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str