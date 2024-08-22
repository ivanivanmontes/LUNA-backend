import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pymysql import IntegrityError
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import *
from app.schemas.user_schema import *

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#TODO: can we write the return types for clarity?
#TODO: can we think of other read routes for the user?
#TODO: in create_user:
#    - there is no distinction when a 400 gets returned for email / username
#    - user_id duplicate check is horrible code. please refactor 
#    - by introducing auto incrementing user_ids and UUIDs.
#    - should user's have a field for partnership_id???
#TODO: in update_user_basic:
#    - update this route to return past info and new info. Will need to change the return type
#TODO: in create_partnership:
#    - update docstring
#    - There's a check to make sure the users are single / in a 1:1 relationship, this could be updated later...
#    - partnership -> relationship?
#    - overall this route could use the most refactoring


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

@router.post("/create_user", response_model=UserSchema)
async def create_user(user: UserSchema, db: Session = Depends(get_db)) -> UserSchema:
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

@router.put("/update_user/{user_id}", response_model=UserUpdateSchema)
async def update_user_basic(user_id: int, user_update: UserUpdateSchema, db: Session = Depends(get_db)) -> UserUpdateSchema:
    """
    update a user's basic credentials (last/first/user name)

    Args:
        user_id: user's id 
        user_update: schema that houses the info that could be updated
        db: database session
    
    Return:
        UserUpdateSchema: if update was successful and shows new user information
    """
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    

    update_data = user_update.model_dump(exclude_unset=True)
    for attribute, new_value in update_data.items():
        # useful function, can be read as:
        # user.attribute = new_value
        setattr(user, attribute, new_value)

    db.commit()
    db.refresh(user)
    return user

@router.post("/create_partnership/{user_id_1}/{user_id_2}")
async def create_partnership(user_id_1: int, user_id_2: int, db: Session = Depends(get_db)):
    """
    create a partnership between two users

    Args:
        user_id_1: first user's id
        user_id_2: second user's id
        db: database session

    Return:
        []
    
    Raise:
        []
    """

    if user_id_1 == user_id_2:
        raise HTTPException(status_code=400, detail="user cannot be in a relationship with self")

    do_users_exist = db.query(UserModel).filter(or_(UserModel.user_id == user_id_1, UserModel.user_id == user_id_2)).first()
    if not do_users_exist:
        raise HTTPException(status_code=400, detail="user(s) not found")


    user_1 = db.query(UserModel).filter(UserModel.user_id == user_id_1).first();
    user_2 = db.query(UserModel).filter(UserModel.user_id == user_id_2).first();

    if (user_1.partnership_id is not None or user_2.partnership_id is not None):
        raise HTTPException(status_code=400, detail="one or more users are in a relationship")
    
    # create new entity in user_partnerships
    new_partnership = UserPartnerships(user_id_1, user_id_2)
    try:
        # we added a trigger to add partnership ids to the users attributes
        db.add(new_partnership)
        db.commit()
        db.refresh(new_partnership)
        logging.info(f"Created partnership for users: {new_partnership}")
        return {"success : partnership created"}
    except:
        # make sure to return the response given from the frontend!
        db.rollback()
        logging.error(f"Error creating partnership: {new_partnership}")
        raise HTTPException(status_code=400, detail=f"Error creating partnership: {new_partnership}")

@router.delete("/delete_partnership/{partnership_id}")
async def delete_partnership(partnership_id: int, db: Session = Depends(get_db)):
    """
    When love fails. Delete the partnership from the table

    Args:
        partnership_id: id of the partnership to delete
        db: database session

    Return:
        []
    
    Raise:
        []
    """

    partnership_to_delete = db.query(UserPartnerships).filter(UserPartnerships.partnership_id == partnership_id).delete()

    if partnership_to_delete:
        # we created a trigger in our database to also delete the partnership ids from user table
        db.commit()
        logging.info("deleted partnership")
        return JSONResponse(status_code=200, content={"success": "deleted partnership"})
    else:
        db.rollback()
        logging.error("Error deleting partnership")
        raise HTTPException(status_code=400, detail="Error deleting partnership")

