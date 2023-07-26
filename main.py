'''It's a startup file, the code doen't matter'''
    

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name:str
    price:float
    is_offer: Union[bool, None] = None

@app.get("/")
async def read_root():
    return {"Hello": "world"}


