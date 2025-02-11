from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
# from fastapi.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import os

load_dotenv()


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# FastAPI app setup
router = APIRouter()


# Add session middleware to store user credentials securely
# router.add_middleware(SessionMiddleware, secret_key="meep")  # Replace with a strong key

# Google API credentials
REDIRECT_URI = "https://luna-backend-production-0459.up.railway.app/oauth2callback"
# REDIRECT_URI = "http://127.0.0.1:8000/oauth2callback"
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Pydantic model for event data
class Event(BaseModel):
    summary: str
    location: str
    description: str
    start_datetime: str
    end_datetime: str
    time_zone: str
    attendees: list[str]


# OAuth flow
@router.get("/authorize")
async def authorize(request: Request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI

    # Log the redirect URI and state
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
    )
    print(f"Authorization URL: {authorization_url}")
    print(f"Redirect URI: {flow.redirect_uri}")
    print(f"State: {state}")

    request.session["state"] = state
    return RedirectResponse(url=authorization_url)


@router.get("/oauth2callback")
async def oauth2callback(request: Request):
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    state = request.session.get("state")
    print(f"Returned state: {request.query_params.get('state')}")  # In /oauth2callback
    if not state:
        return JSONResponse({"error": "Missing state in session"}, status_code=400)

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        state=state,
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_response = str(request.url)
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    credentials = flow.credentials
    request.session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    return JSONResponse({"message": "Authorization successful!"})


@router.post("/create-event")
async def create_event(request: Request, event: Event):
    credentials_dict = request.session.get("credentials")
    if not credentials_dict:
        # Redirect to /authorize if no credentials are found
        return RedirectResponse(url="/authorize")

    credentials = Credentials(**credentials_dict)
    service = build("calendar", "v3", credentials=credentials)

    event_data = {
        "summary": event.summary,
        "location": event.location,
        "description": event.description,
        "start": {
            "dateTime": event.start_datetime,
            "timeZone": event.time_zone,
        },
        "end": {
            "dateTime": event.end_datetime,
            "timeZone": event.time_zone,
        },
        "attendees": [{"email": email} for email in event.attendees],
    }

    try:
        event_result = service.events().insert(
            calendarId="primary", body=event_data, sendUpdates="all"
        ).execute()
        return {"message": "Event created successfully", "htmlLink": event_result["htmlLink"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@router.get("/invite")
async def invite():
    print("she clicked the gcal invite button")
    return JSONResponse({"message": "invite sent!"})