from pydantic import BaseModel
from typing import Optional

# Pydantic schemas 
class UserSchema(BaseModel):
    # id: gets created in the user model
    username: str
    email: str
    first_name: str
    last_name: str
    password: str

    class Config:
        from_attributes = True