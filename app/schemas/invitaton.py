from pydantic import BaseModel, ConfigDict
from datetime import datetime

class InvitationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id: int
    sender_id: int
    status: str
    created_at: datetime