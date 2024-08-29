import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pymysql import IntegrityError
from sqlalchemy import and_, or_
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

@router.get("/get_pin/{pin_id}")
async def get_pin(pin_id: int, db: Session = Depends(get_db)):
    """
    retrieve a single pin's information given their id

    Args:
        pin_id: pin id
        db: database session

    Return:
        []

    Raise:
        []
    """


@router.get("/get_all_pins/{user_id}")
async def get_all_pins(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all the pins belonging to a user

    Args:
        user_id: user id to check against pins
    """
    all_pins = db.query(PinModel).filter(PinModel.user_id == user_id).first()
    return all_pins


@router.post("/create_pin/{user_id}", response_model=PinSchema)
async def create_pin(user_id: int, pin_info: PinSchema, db: Session = Depends(get_db)) -> PinSchema:
    """
    create a new pin. trigger called after_pin_create was created to also add an entry into user_pins
    """

    # edge cases
    new_pin = PinModel(pin_info)
    is_pin_duplicate = db.query(PinModel).filter(and_(PinModel.latitude == new_pin.latitude, PinModel.longitude == new_pin.longitude)).first()
    if is_pin_duplicate:
        raise HTTPException(status_code=400, detail="Pin location already exist")
    
    try:
        db.add(new_pin)
        db.commit()
        db.refresh(new_pin)
        logging.info(f"Created new pin: {new_pin}")
        return pin_info
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating pin: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating pin: {e}")
    