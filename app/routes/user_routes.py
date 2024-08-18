# routes/user_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import UserModel
from app.schemas.user_schema import UserSchema

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
    users = db.query(UserModel).all()
    return users

@router.post("/create_user", response_model=UserSchema)
async def create_user(user: UserSchema, db: Session = Depends(get_db)) -> UserSchema :
    #TODO: include a try except for when a field is missing, all fields should be included. 
    does_user_exist = db.query(UserModel).filter(UserModel.email == user.email).first()
    if does_user_exist:
        raise HTTPException(status_code=400, detail="User already exists")
    db_user = UserModel(user)
    print(db_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user



