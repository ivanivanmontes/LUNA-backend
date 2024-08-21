from pydantic import BaseModel
from typing import Optional

# Pydantic schemas 
# base user schema 
class UserSchema(BaseModel):
    # id: gets created in the user model
    username: str
    email: str
    first_name: str
    last_name: str
    password: str

    class Config:
        from_attributes = True

# parameters for updating basic user information
class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True
