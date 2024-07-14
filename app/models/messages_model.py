from datetime import timedelta
from tkinter import CASCADE
from sqlalchemy import JSON, Column, Integer, Interval, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from enum import Enum as PythonEnum
from app.database.database import Base




class Socket(Base):
    __tablename__ = 'socket'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    message = Column(String)
    receiver_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    rooms = Column(String, ForeignKey('rooms.name_room', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_return = Column(Integer)
    fileUrl = Column(String)
    edited = Column(Boolean, server_default='false') 
    
    
    
class PrivateMessage(Base):
    __tablename__ = 'private_messages'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    message = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_read = Column(Boolean, nullable=False, default=True)
    fileUrl = Column(String)
    edited = Column(Boolean, server_default='false')
    id_return = Column(Integer)
    
    
    
class Vote(Base):
    __tablename__ = 'votes'
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    message_id = Column(Integer, ForeignKey("socket.id", ondelete="CASCADE"), primary_key=True)
    dir = Column(Integer)
    
    
class PrivateMessageVote(Base):
    __tablename__ = 'private_message_votes'
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    message_id = Column(Integer, ForeignKey("private_messages.id", ondelete="CASCADE"), primary_key=True)
    dir = Column(Integer) 