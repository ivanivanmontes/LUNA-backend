from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from dotenv import load_dotenv
import os

load_dotenv()

# Fetch the environment variables
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")

app = FastAPI()

# Database connection string
#TODO: for some reason the root user doesn't have a password???
DATABASE_URL = f"mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_name}"

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/check-db")
async def check_db_connection():
    try:
        with engine.connect() as connection:
            # Execute the query using text() to construct the SQL statement
            result = connection.execute(text("SELECT 1"))
            # Fetch the result to ensure execution
            _ = result.fetchone()
        return {"status": "Connection successful!"}
    except OperationalError as e:
        # Error with the Database URL
        return {"status": "Connection failed", "error": str(e)}
    except Exception as e:
        # General Error
        return {"status": "An error occurred", "error": str(e)}