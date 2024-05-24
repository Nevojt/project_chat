from pydantic import BaseModel, EmailStr



class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str