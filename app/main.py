import time
from dotenv import load_dotenv

load_dotenv()
import os

from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db


url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    name: str
    message: str
    published: bool = True
    
while True:   
    try:
        conn = psycopg2.connect(host=url, database='postgres', user='postgres',
                                password=key, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break

    except Exception as error:
            print('Conection to database failed')
            print("Error:",  error)
            time.sleep(2)
    
my_post = [{"name": "big boss", "message": "content of post 1", "id": 1}, 
           {"name": "litle foot", "message":"favorite Pizza", "id": 2 }]


def find_post(id):
    for p in my_post:
        if p["id"] == id:
            return p
        
def find_index_post(id):
    for i, p in enumerate(my_post):
        if p["id"] == id:
            return i

@app.get("/")
async def root():
    cursor.execute("""SELECT * FROM room_one""")
    
    room_one = cursor.fetchall()
    return {"message": room_one}

@app.get("alchemy")
def test_get(db: Session = Depends(get_db)):
    
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.get("/posts")
async def get_posts():
    return {"data": my_post}



@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def get_posts(post: Post):
    
    return {"data": post}



@app.get("/posts/{id}")
async def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    return {"post_details": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    
    my_post.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
        
    post_dict = post.dict()
    post_dict['id'] = id
    my_post[index] = post_dict
    return {'data': post_dict}
    