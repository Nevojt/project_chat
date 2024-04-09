from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from enum import Enum as PythonEnum
from app.database.database import Base


class UserRole(str, PythonEnum):
	user = "user"
	admin = "admin"

class Socket(Base):
    __tablename__ = 'socket'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    message = Column(String)
    receiver_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    rooms = Column(String, ForeignKey('rooms.name_room', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_return = Column(Integer)
    fileUrl = Column(String)
    

    
class PrivateMessage(Base):
    __tablename__ = 'private_messages'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    messages = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_read = Column(Boolean, nullable=False, default=True)
    
class Rooms(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True, nullable=False)
    name_room = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    image_room = Column(String, nullable=False)
    owner = Column(Integer, (ForeignKey("users.id", ondelete='SET NULL')), nullable=False)
    secret_room = Column(Boolean, default=False)
    block = Column(Boolean, default=False)
    
    
    
class RoomsManager(Base):
    __tablename__ = 'rooms_manager'
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, (ForeignKey("users.id", ondelete="CASCADE")), nullable=False)
    room_id = Column(Integer, (ForeignKey("rooms.id", ondelete="CASCADE")), nullable=False)
    favorite = Column(Boolean, default=False)
    
class RoomsTabs(Base):
    __tablename__ = 'tabs'
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, (ForeignKey("users.id", ondelete="CASCADE")), nullable=False)
    room_id = Column(Integer, (ForeignKey("rooms.id", ondelete="CASCADE")), nullable=False)
    tab_name = Column(String)
    favorite = Column(Boolean, default=False)


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    user_name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    verified = Column(Boolean, nullable=False, server_default='false')
    token_verify = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    
class User_Status(Base):
    __tablename__ = 'user_status' 
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    name_room = Column(String, ForeignKey("rooms.name_room", ondelete="CASCADE", onupdate='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),unique=True, nullable=False)
    user_name = Column(String, nullable=False)
    status = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    
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