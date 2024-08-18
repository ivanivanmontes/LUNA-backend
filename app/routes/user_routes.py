# routes/user_routes.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.schemas.user_schema import UserCreate, UserSchema

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/get_users")
async def get_users(db: Session = Depends(get_db)):
    """
    Retrieve all users in the database

    Args:
        db: database Session

    Returns:
        JSON Object: all users
    """
    users = db.query(User).all()
    return users

@router.post("/create_user", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    #TODO: write code for creating user, although this model / schema is getting kinda annoying
    ...



