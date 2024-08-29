import bcrypt
import enum

from sqlalchemy import TIMESTAMP, Column, Enum, ForeignKey, Integer, String, func, DECIMAL
from .database import Base
from .schemas.user_schema import UserSchema
from .schemas.pin_schema import PinSchema

class OwnershipType(enum.Enum):
    primary = "primary"
    secondary = "secondary"

# sqlalchemy models
class UserModel(Base):
    def __init__(self, user: UserSchema):
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.username = user.username
        self.email = user.email
        self.hashed_password = self._hash_password(user.password)
    
    def _hash_password(self, password: str) -> str:
        # hash the retrieved password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False, index=True)
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    creation_date = Column(TIMESTAMP, nullable=True, server_default=func.current_timestamp())
    partnership_id = Column(Integer, ForeignKey("user_partnerships.partnership_id"), nullable=True, index=True)

    def __str__(self):
        return f"""
    User(
        id={self.user_id}, 
        first_name='{self.first_name}',
        last_name='{self.last_name}',
        username='{self.username}',
        email='{self.email}',
        password='{self.hashed_password},
        partnership_id= {self.partnership_id}'
    )"""

class UserPartnershipModel(Base):
    def __init__(self, user_id_1: int, user_id_2: int):
        self.user_id_1 = user_id_1
        self.user_id_2 = user_id_2

    __tablename__ = "user_partnerships"
    partnership_id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    user_id_1 = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    user_id_2 = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    partnership_date = Column(TIMESTAMP, nullable=True, server_default=func.current_timestamp())

class PinModel(Base):
    def __init__(self, pin: PinSchema):
        self.user_id = pin.user_id
        self.title = pin.title
        self.latitude = pin.latitude
        self.longitude = pin.longitude
        self.details = pin.details

    __tablename__ = "pins"
    pin_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), index=True, nullable=True)
    title = Column(String(255), nullable=True, default=None)
    latitude = Column(DECIMAL(9, 6), nullable=True, default=None)
    longitude = Column(DECIMAL(9, 6), nullable=True, default=None)
    creation_date = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=True)
    details = Column(String(255), nullable=True, default=None)  # Added field
    
    def __str__(self):
        return f"""
    Pin(
        pin_id={self.pin_id}, 
        user_id='{self.user_id}',
        title='{self.title}',
        latitude='{self.latitude}',
        longitude='{self.longitude}',
        creation_date='{self.creation_date}
    )"""

class UserPinModel(Base):
    __tablename__ = "user_pins"
    user_pin_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    pin_id = Column(Integer, ForeignKey("pins.pin_id"), nullable=True)
    ownership_type = Column(Enum(OwnershipType), nullable=False)
    creation_date = Column(TIMESTAMP, nullable=True, server_default=func.current_timestamp())
    removal_date = Column(TIMESTAMP, nullable=True)