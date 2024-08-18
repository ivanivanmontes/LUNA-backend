# routes/user_routes.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/get_users")
async def getUsers(db: Session = Depends(get_db)):
    """
    Retrieve all users in the database

    Returns:
        JSON Object: all users
    """
    users = db.query(User).all()
    return users




