
from pydantic import BaseModel, EmailStr, Field



class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(...)
    
class PasswordReset(BaseModel):
    password: str  = Field(...)
    
    
class PasswordResetMobile(BaseModel):
    email: EmailStr = Field(...)
    code: str = Field(...)
    password: str  = Field(...)

class PasswordResetV2(PasswordResetRequest):
    code: str = Field(...)