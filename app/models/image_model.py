from datetime import timedelta
from tkinter import CASCADE
from sqlalchemy import JSON, Column, Integer, Interval, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from enum import Enum as PythonEnum
from app.database.database import Base

class ImagesAll(Base):
    __tablename__ = 'imagesAll'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    image_room = Column(String, nullable=False)
    images = Column(String, nullable=False)
    
    
class ImagesAvatar(Base):
    __tablename__ = 'imagesAvatar'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    avatar = Column(String, nullable=False)
    images_url = Column(String, nullable=False)
    
class ImagesRooms(Base):
    __tablename__ = 'imagesRooms'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    rooms = Column(String, nullable=False)
    images_url = Column(String, nullable=False)