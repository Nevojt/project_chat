from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base



    
class Rooms(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True, nullable=False)
    name_room = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    
class Message(Base):
    __tablename__ ='messagesDev'
    
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    member_id = Column(Integer,  nullable=False)
    avatar = Column(String, nullable=False)
    is_privat = Column(Boolean, server_default='False', nullable=False)
    receiver = Column(Integer, nullable=False)
    rooms = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    user_name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))