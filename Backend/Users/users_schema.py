from pydantic import BaseModel
from typing import List

class User_info(BaseModel):
    uid: int
    name: str
    password: str
    status: str

class User(BaseModel):
    name: str
    password: str

class User_Status(BaseModel):
    user_id: int
    status_id: int