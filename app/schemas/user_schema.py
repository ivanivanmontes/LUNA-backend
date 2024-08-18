from pydantic import BaseModel
from typing import Optional

# Pydantic schemas 
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class UserSchema(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True