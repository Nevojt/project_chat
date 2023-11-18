from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
# from sqlalchemy.orm import relationship
from .database import Base


class Socket(Base):
    __tablename__ = 'socket'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    message = Column(String, nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rooms = Column(String, ForeignKey('rooms.name_room', ondelete='CASCADE'), nullable=False)

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
    
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    user_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=False, server_default='https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/content%20common%20chat/Avatar%20Desktop/avatar_default.jpg')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
class User_Status(Base):
    __tablename__ = 'user_status' 
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    name_room = Column(String, ForeignKey("rooms.name_room", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),unique=True, nullable=False)
    user_name = Column(String, nullable=False)
    status = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    
class Vote(Base):
    __tablename__ = 'votes'
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    message_id = Column(Integer, ForeignKey("messagesDev.id", ondelete="CASCADE"), primary_key=True)
    
    
class ImagesAll(Base):
    __tablename__ = 'imagesAll'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    image_room = Column(String, nullable=False)
    images = Column(String, nullable=False)
    



# class Message(Base):
#     __tablename__ ='messagesDev'
    
#     id = Column(Integer, primary_key=True, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
#     message = Column(String, nullable=False)
#     is_privat = Column(Boolean, server_default='False', nullable=False)
#     receiver_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
#     rooms = Column(String, ForeignKey('rooms.name_room', ondelete='CASCADE'), nullable=False)
#     owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
#     owner = relationship('User', foreign_keys=[owner_id])
#     receiver = relationship('User', foreign_keys=[receiver_id])