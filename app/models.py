from sqlalchemy import Table
from .database import engine, Base
# sqlalchemy models
class User(Base):
    __tablename__ = 'users'
    __table__ = Table(__tablename__, Base.metadata, autoload_with=engine)