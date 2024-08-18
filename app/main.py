from fastapi import FastAPI
from app.routes import user_routes
from app import database

app = FastAPI()
app.include_router(user_routes.router)
app.include_router(database.router)


@app.get("/")
async def root():
    """
    All routes will follow this type of format. This is a quick summary of the route
    If the argument, return type, or raised exception doesn't exist, do not include.

    Args:
        nameOfArguments (their type): one-line summary if neccesary

    Returns:
        ObjectType (usually JSON Object): simple message

    Raises:
        TypeOfException: Why
    """
    return {"message": "Hello World!"}
