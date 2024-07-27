
from datetime import timedelta
from tkinter import CASCADE
from sqlalchemy import JSON, Column, Integer, Interval, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from enum import Enum as PythonEnum
from app.database.database import Base



class UserRoleInRoom(str, PythonEnum):
    admin = "admin"
    owner = "owner"
    moderator = "moderator"
    user = "user"

class Rooms(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True, nullable=False)
    name_room = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    image_room = Column(String, nullable=False)
    owner = Column(Integer, (ForeignKey("users.id", ondelete='SET NULL')), nullable=False)
    secret_room = Column(Boolean, default=False)
    block = Column(Boolean, nullable=False, server_default='false')
    delete_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    invitations = relationship("RoomInvitation", back_populates="room")
    
    
class RoomsManager(Base):
    __tablename__ = 'rooms_manager_secret'
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, (ForeignKey("users.id", ondelete="CASCADE")), nullable=False)
    room_id = Column(Integer, (ForeignKey("rooms.id", ondelete="CASCADE")), nullable=False)
    favorite = Column(Boolean, default=False)

class RoomsManagerMyRooms(Base):
    __tablename__ = 'rooms_manager_my_rooms'
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, (ForeignKey("users.id", ondelete="CASCADE")), nullable=False)
    room_id = Column(Integer, (ForeignKey("rooms.id", ondelete="CASCADE")), nullable=False)
    favorite = Column(Boolean, default=False)


class RoomTabsInfo(Base):
    __tablename__ = 'tabs_info'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    name_tab = Column(String)
    image_tab = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, (ForeignKey("users.id", ondelete="CASCADE")), nullable=False)
    

    
class RoomsTabs(Base):
    __tablename__ = 'tabs'
    
    id = Column(Integer, primary_key=True, nullable=False)
    tab_id = Column(Integer, (ForeignKey("tabs_info.id", ondelete="CASCADE")), nullable=False)
    user_id = Column(Integer, (ForeignKey("users.id", ondelete="CASCADE")), nullable=False)
    room_id = Column(Integer, (ForeignKey("rooms.id", ondelete="CASCADE")), nullable=False)
    tab_name = Column(String)
    favorite = Column(Boolean, default=False)
    
    
    
class RoomInvitation(Base):
    __tablename__ = 'room_invitations'

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    recipient_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum('pending', 'accepted', 'declined', name='invitation_status'), default='pending')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    room = relationship("Rooms", back_populates="invitations")
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    

class RoleInRoom(Base):
    __tablename__ = "role_in_room"
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(UserRoleInRoom,), default='user') 
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    
class Ban(Base):
    __tablename__ = 'bans'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"),  nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    user = relationship("User", back_populates="bans")