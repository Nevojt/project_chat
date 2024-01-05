from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from pydantic.types import conint
        
        



class UserOut(BaseModel):
    id: int
    user_name: str
    avatar: str
    created_at: datetime
    
    class Config:
        from_attributes = True
    
        
class SocketModel(BaseModel):
    created_at: datetime
    receiver_id: int
    message: str
    user_name: str
    avatar: str
    
    class Config:
        from_attributes = True


class PrivateRecipient(BaseModel):
    sender_id: int
    sender_name: str
    sender_avatar: str
    recipient_id: int
    recipient_name: str
    recipient_avatar: str

class PrivateInfoRecipient(BaseModel):
    recipient_id: int
    recipient_name: str
    recipient_avatar: str
    verified: bool
    is_read: bool



class RoomBase(BaseModel):
    id: int
    name_room: str
    image_room: str
    count_users: int
    count_messages: int
    created_at: datetime
    
    
class RoomCreate(BaseModel):
    name_room: str
    image_room: str

class RoomPost(RoomBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        
        
class Images(BaseModel):
    images: str
    image_room: str
    
class ImagesCreate(Images):
    pass
       
class ImagesResponse(Images):
    id: Optional[int]

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
        
class CountMessages(BaseModel):
    rooms: str
    count: int
    
class CountUsers(BaseModel):
    rooms: str
    count: int
    
        
        
        
class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    password: str
    avatar: str
    verified: bool = Field(False)
    
class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(...)
    
class PasswordReset(BaseModel):
    password: str  = Field(...)      


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


class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[int] = None
    
    
class Vote(BaseModel):
    message_id: int
    dir: conint(le=1)
    
    
    
# class MessagePost(MessageBase):
#     id: int
#     created_at: datetime
#     owner_id: int
#     receiver_id: int
    
#     owner: UserOut
#     receiver: UserOut
    
#     class Config:
#         from_attributes = True
        
# class MessageOut(BaseModel):
#     MessagePost: MessagePost
#     votes: int
    
#     class Config:
#         from_attributes = True
        
        
# class MessageBase(BaseModel):
#     message: str
#     is_privat: bool = False
#     receiver_id: int = 1
#     rooms: str
    
    # commit message
# class MessageCreate(MessageBase):
#     pass