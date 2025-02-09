from fastapi import FastAPI
from app.routes import user_routes, pin_routes, memory_routes, knuffle_bunny
from app import database
from app import s3
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
app.include_router(user_routes.router)
app.include_router(pin_routes.router)
app.include_router(database.router)
app.include_router(s3.router)
app.include_router(memory_routes.router)
app.include_router(knuffle_bunny.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")  # Replace with a strong key

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Allow all hosts
app.add_middleware(
    BaseHTTPMiddleware,
    dispatch=lambda scope, receive, send: (
        scope.update({"scheme": "https"}) or send  # Force HTTPS
    ),
)


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
