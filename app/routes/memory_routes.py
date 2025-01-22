import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pymysql import IntegrityError
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import *
from app.schemas.user_schema import *
from app.s3 import s3
from botocore.exceptions import NoCredentialsError

router = APIRouter()

class MemoryType(Enum):
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def upload_to_s3(file: UploadFile, bucket_name: str = "lovabledog", folder: str = "") -> str:
    try:
        file_name = f"{folder}/{file.filename}"
        s3.upload_fileobj(file.file, bucket_name, file_name)
        return f"https://{bucket_name}.s3.amazonaws.com{file_name}"
    except NoCredentialsError:
        raise HTTPException(status_code=400, detail="Credentials not available for S3")

def create_memory_instance(pin_id: int, db: Session) -> MemoryInstanceModel:
    """
    create a entry in memory_instance and return the newly created instance id
    """
    try:
        new_memory_instance = MemoryInstanceModel(pin_id=pin_id)
        db.add(new_memory_instance)
        db.commit()
        db.refresh(new_memory_instance)
        return new_memory_instance
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"upload failed: {e}")

@router.post("/upload_memory/{pin_id}/{memory_type}")
async def upload_memory(pin_id: int, memory_type: str, file: UploadFile = File(None), text: str = None, db: Session = Depends(get_db)):
    """
    #TODO: write this later.
    """
    if memory_type is None:
        raise HTTPException(status_code=400, detail="File is required for this memory type")
    elif memory_type == MemoryType.TEXT:
        try:
            # upload to database and not s3
            # just store the text and the memory type indicting its only text
            # will trigger an entry in memory_instance to fill in the memory_instance
            new_memory_text = MemoryModel()
            new_memory_text.memory_type = "text"
            new_memory_text.memory_text = text
            new_memory_instance = create_memory_instance(pin_id, db)
            new_memory_text.instance_id = new_memory_instance.instance_id
            db.add(new_memory_text)
            db.commit()
            db.refresh()
            return new_memory_text
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"upload failed: {e}")
    else: # audio , photo , video
        if not file:
            raise HTTPException(status_code=400, detail="File is required for this memory type")
        file_url = upload_to_s3(file)
        new_memory = MemoryModel()
        new_memory.memory_type = memory_type
        new_memory.file_url = file_url
        new_memory_instance = create_memory_instance(pin_id=pin_id, db=db)
        new_memory.instance_id = new_memory_instance.instance_id
        db.add(new_memory)
        db.commit()
        db.refresh(new_memory)
        return new_memory


@router.get("/download_memories_from_instance/{instance_id}/")
async def download_memories_from_instance(instance_id: int, db: Session = Depends(get_db)):
    """
    for a given memory instance, retrieve all the memories as it pertains to that instance
    look up the instance id in the memories table 
    """
    try:
        res = db.query(MemoryModel).filter(MemoryModel.instance_id == instance_id).all()
        return res;
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"upload failed: {e}")
    

