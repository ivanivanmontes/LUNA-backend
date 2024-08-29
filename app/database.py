from fastapi import APIRouter
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# Fetch the environment variables
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

# Database connection string
DATABASE_URL = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
Base = declarative_base()

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


router = APIRouter()


@router.get("/check-db")
async def check_db_connection():
    """
    Try to connect to the database 

    Return:
        JSON Object: Connection Status
    """
    try:
        with engine.connect() as connection:
            # Execute the query using text() to construct the SQL statement
            result = connection.execute(text("SELECT 1"))
            # Fetch the result to ensure execution
            _ = result.fetchone()
        return {"status": "DB Connection successful!"}
    except OperationalError as e:
        # Error with the Database URL
        return {"status": "Connection failed", "error": str(e)}
    except Exception as e:
        # General Error
        return {"status": "An error occurred", "error": str(e)}