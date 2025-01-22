from typing import Optional
from fastapi import File, UploadFile
from pydantic import BaseModel

# Pydantic schemas 
class MemorySchema(BaseModel):
    # user_id : int
    # pin_id : int
    # file_name: str
    file: Optional[UploadFile] = File(None)  # Allows optional file upload
    text: Optional[str] = None  # Allows optional text