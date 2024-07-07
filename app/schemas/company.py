from pydantic import BaseModel, EmailStr, ConfigDict, Field, constr

from typing import Dict, Optional




class CompanyCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., max_length=255)
    subdomain: str = Field(..., max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    subscription_status: Optional[str] = Field(None, max_length=50)
    subscription_end_date: Optional[str] = None
    subscription_type: Optional[str] = Field(None, max_length=50)
    paid_services: Optional[str] = None
    company_code: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    services: Optional[str] = None
    additional_contacts: Optional[str] = None
    settings: Optional[Dict] = None


class CompanySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    subdomain: str
    subscription_status: str
    subscription_end_date: str

class CompanyUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = Field(None, max_length=255)
    subdomain: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    subscription_status: Optional[str] = Field(None, max_length=50)
    subscription_end_date: Optional[str] = None
    subscription_type: Optional[str] = Field(None, max_length=50)
    paid_services: Optional[str] = None
    company_code: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    services: Optional[str] = None
    additional_contacts: Optional[str] = None
    settings: Optional[Dict] = None