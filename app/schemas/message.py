from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from typing_extensions import Annotated



class SocketModel(BaseModel):
    created_at: datetime
    receiver_id: int
    id: int
    message: str
    user_name: str
    avatar: str
    verified: bool
    vote: int
    id_return: Optional[int] = None 
    
    class Config:
        from_attributes = True
        
class SocketUpdate(BaseModel):
    message: str
    
class Vote(BaseModel):
    message_id: int
    dir: Annotated[int, Field(strict=True, le=1)]