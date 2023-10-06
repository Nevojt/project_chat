
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings


SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_name}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_username}'



engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=30)
connection = engine.connect()
connection.close() 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
        
while True:   
    try:
        conn = psycopg2.connect(host=settings.database_hostname, database=settings.database_name, user=settings.database_username,
                                password=settings.database_password, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break

    except Exception as error:
            print('Conection to database failed')
            print("Error:",  error)
            time.sleep(2)