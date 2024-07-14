from datetime import timedelta
from tkinter import CASCADE
from sqlalchemy import JSON, Column, Integer, Interval, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from enum import Enum as PythonEnum
from app.database.database import Base




class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(255), unique=True, nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50))
    address = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    subscription_status = Column(String(50))
    subscription_end_date = Column(String)
    subscription_type = Column(String(50))
    paid_services = Column(String)
    company_code = Column(String(50))
    logo_url = Column(String(255))
    description = Column(String)
    services = Column(String)
    additional_contacts = Column(String)
    settings = Column(JSON)
    
    users = relationship("User", back_populates="company", cascade="all, delete")
    rooms = relationship("Rooms", back_populates="company", cascade="all, delete")