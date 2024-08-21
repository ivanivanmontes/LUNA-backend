import logging

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from pymysql import IntegrityError
from sqlalchemy import or_
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

#TODO: can we write the return types for clarity?

@router.get("/get_all_users")
async def get_all_users(db: Session = Depends(get_db)):
    """
    Retrieve all users in the database

    Args:
        db: database session

    Returns:
        JSON Object: all users
    """
    users = db.query(UserModel).all()
    return users

@router.get("/get_user/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Return a user model given their user_id

    Args:
        user_id: unique integer representing a user
        db: database session
    
    Returns:
        UserModel: user data 
    
    Raises:
        HTTPException: if user_id does not exist
    """
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail=f"user not found for user_id: {user_id}")

    return user

#TODO: can we think of other read routes for the user?

@router.post("/create_user", response_model=UserSchema)
async def create_user(user: UserSchema, db: Session = Depends(get_db)) -> UserSchema:
    #TODO: there is no distinction when a 400 gets returned for email / username
    #      user_id duplicate check is horrible code. please refactor 
    #      by introducing auto incrementing user_ids and UUIDs.
    """
    Create a user in the database

    Args:
        user: JSON object that contains new user information
        db: database session

    Returns:
        Response: Letting us know if a user was successfully created
    
    Raises:
        HTTPException: if an email is already used

    """
    db_user = UserModel(user) 
    is_user_not_unique = db.query(UserModel).filter(
        or_(UserModel.email == user.email, UserModel.username == user.username)
    ).first()
    does_user_id_duplicate = db.query(UserModel).filter(UserModel.user_id == db_user.user_id).first()
    if is_user_not_unique:
        # if email / username is already used
        raise HTTPException(status_code=400, detail="Email / username already used")
    
    while does_user_id_duplicate:
        # generate a new user if user id is duplicated
        db_user = UserModel(user)
        does_user_id_duplicate = db.query(UserModel).filter(UserModel.user_id == db_user.user_id).first()

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logging.info(f"Created user: {db_user}")
        return user
    except IntegrityError as e:
        # make sure to return the response given from the frontend!
        db.rollback()
        logging.error(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating user: {e}")
    
@router.delete("/delete_user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    """
    deletes a user off of the database. 
    no need to delete from user_pins or user_partnerships

    Args:
        user_id: the user id to delete 
        db: Database session
    
    Returns:
        Response: Letting us know if a user was successfully created
    
    Raises:
        HTTPException: if user id cannot be deleted 
    """

    did_delete = db.query(UserModel).filter(UserModel.user_id == user_id).delete()
    if did_delete:
        db.commit()
        logging.info(f"deleted user {user_id}")
        return JSONResponse(status_code=200, content={"success": f"deleted user: {user_id}"})
    else:
        db.rollback()
        logging.error(f"Error deleting user: {user_id}")
        raise HTTPException(status_code=400, detail=f"Error deleting user: {user_id}")

