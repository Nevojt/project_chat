
from pydantic import BaseModel

        
        

class PrivateRecipient(BaseModel):
    sender_id: int
    sender_name: str
    sender_avatar: str
    receiver_id: int
    receiver_name: str
    receiver_avatar: str

class PrivateInfoRecipient(BaseModel):
    receiver_id: int
    receiver_name: str
    receiver_avatar: str
    verified: bool
    is_read: bool



        
        



