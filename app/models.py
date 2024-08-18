from random import randint
from sqlalchemy import TIMESTAMP, Column, Integer, String, func
from .database import engine, Base
from .schemas.user_schema import UserSchema
# sqlalchemy models
class UserModel(Base):

    #TODO: Let's write other private functions to generate user_ids and hashed_password

    def __init__(self, user: UserSchema):
        self.user_id = randint(0,100000)
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.username = user.username
        self.email = user.email
        self.hashed_password = user.password


    __tablename__ = 'users'
    # __table__ = Table(__tablename__, Base.metadata, autoload_with=engine)
    user_id = Column(Integer, primary_key=True, nullable=False, index=True)
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    creation_date = Column(TIMESTAMP, nullable=True, server_default=func.current_timestamp())

    def __str__(self):
        return f"""
    User(
        id={self.user_id}, 
        first_name='{self.first_name}',
        last_name='{self.last_name}',
        username='{self.username}',
        email='{self.email}',
        password='{self.hashed_password}'
    )"""





