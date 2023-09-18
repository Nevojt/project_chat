from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base



    
class Rooms(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True, nullable=False)
    name_room = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    image_room = Column(String, nullable=False, server_default='https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/Content%20Home%20page/Desktop/weight-lifting-1284616_640.jpg')
    
    
class Message(Base):
    __tablename__ ='messagesDev' # 'messagesDev'
    
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    avatar = Column(String, nullable=False)
    is_privat = Column(Boolean, server_default='False', nullable=False)
    receiver = Column(Integer, nullable=False)
    rooms = Column(String, ForeignKey('rooms.name_room'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    user_name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
class User_Status(Base):
    __tablename__ = 'user_status' 
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    room_name = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, nullable=False, unique=True)
    user_name = Column(String, nullable=False)
    status = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    
    
    