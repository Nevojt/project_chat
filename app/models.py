from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base



class RoomOne(Base):
    __tablename__ = 'room_one'
    
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    member_id = Column(Integer,  nullable=False)
    avatar = Column(String, nullable=False)
    is_privat = Column(Boolean, server_default='False', nullable=False)
    receiver = Column(Integer, nullable=False)
    
class RoomTwo(Base):
    __tablename__ = 'room_two'
    
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    member_id = Column(Integer,  nullable=False)
    avatar = Column(String, nullable=False)
    is_privat = Column(Boolean, server_default='False', nullable=False)
    receiver = Column(Integer, nullable=False)
    
class RoomThree(Base):
    __tablename__ = 'room_three'
    
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    member_id = Column(Integer,  nullable=False)
    avatar = Column(String, nullable=False)
    is_privat = Column(Boolean, server_default='False', nullable=False)
    receiver = Column(Integer, nullable=False)
    
class RoomFour(Base):
    __tablename__ = 'room_four'
    
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    member_id = Column(Integer,  nullable=False)
    avatar = Column(String, nullable=False)
    is_privat = Column(Boolean, server_default='False', nullable=False)
    receiver = Column(Integer, nullable=False)
    
class RoomFive(Base):
    __tablename__ = 'room_five'
    
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    member_id = Column(Integer,  nullable=False)
    avatar = Column(String, nullable=False)
    is_privat = Column(Boolean, server_default='False', nullable=False)
    receiver = Column(Integer, nullable=False)
    
    
    
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    user_name = Column(String, nullable=False)   
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    token = Column(String, nullable=False)