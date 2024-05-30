from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from enum import Enum as PythonEnum
from app.database.database import Base


class UserRole(str, PythonEnum):
	user = "user"
	admin = "admin"
 
class UserRoleInRoom(str, PythonEnum):
    admin = "admin"
    owner = "owner"
    moderator = "moderator"
    user = "user"

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
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    messages = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_read = Column(Boolean, nullable=False, default=True)
    fileUrl = Column(String)
    edited = Column(Boolean, server_default='false')
    id_return = Column(Integer)
    
class Rooms(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True, nullable=False)
    name_room = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    image_room = Column(String, nullable=False)
    owner = Column(Integer, (ForeignKey("users.id", ondelete='SET NULL')), nullable=False)
    secret_room = Column(Boolean, default=False)
    block = Column(Boolean, nullable=False, server_default='false')
    
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
    blocked = Column(Boolean, nullable=False, server_default='false')
    
    bans = relationship("Ban", back_populates="user")
    
class RoleInRoom(Base):
    __tablename__ = "role_in_room"
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(UserRoleInRoom,), default='user') 
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    
class User_Status(Base):
    __tablename__ = 'user_status' 
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    name_room = Column(String, ForeignKey("rooms.name_room", ondelete="CASCADE", onupdate='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),unique=True, nullable=False)
    user_name = Column(String, nullable=False)
    status = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    
class Ban(Base):
    __tablename__ = 'bans'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"),  nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    user = relationship("User", back_populates="bans")    
    
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
    
    
class PasswordReset(Base):
    __tablename__ = 'password_reset'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    email = Column(String, index=True)
    reset_code = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_active = Column(Boolean, default=True)
    
    
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