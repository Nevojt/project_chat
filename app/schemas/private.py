
from pydantic import BaseModel

        
        

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



        
        



