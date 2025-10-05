from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import os
import json
from pathlib import Path

load_dotenv()

router = APIRouter()

# OAuth2 configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')

# Try to load from credentials.json, fallback to env vars
credentials_file = Path(__file__).parent.parent / 'credentials.json'

def get_flow():
    """Create OAuth2 flow"""
    # Always use our specified redirect URI, regardless of what's in credentials.json
    if credentials_file.exists():
        flow = Flow.from_client_secrets_file(
            str(credentials_file),
            scopes=SCOPES
        )
        # Override the redirect URI from the file
        flow.redirect_uri = REDIRECT_URI
        return flow
    else:
        # Fallback to environment variables
        client_config = {
            "web": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        return Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

# In-memory token storage (for MVP - use database in production)
user_tokens = {}
user_calendar_selections = {}  # Store which calendars each user wants to analyze

@router.get("/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    try:
        flow = get_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to get refresh token
        )

        # Store state for CSRF protection (in production, use session/database)
        return {
            "auth_url": authorization_url,
            "state": state,
            "message": "Redirect user to auth_url"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth initialization failed: {str(e)}")

@router.get("/callback")
async def google_callback(code: str, state: str = None):
    """Handle OAuth callback from Google"""
    try:
        flow = get_flow()

        # Exchange authorization code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Store credentials (in production, encrypt and store in database)
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        # For MVP, use a simple user_id (in production, use proper user management)
        user_id = "demo_user"
        user_tokens[user_id] = token_data

        # Save to file for persistence across restarts
        token_file = Path(__file__).parent.parent / 'token.json'
        with open(token_file, 'w') as f:
            json.dump(token_data, f)

        # Test the connection by fetching calendar info
        service = build('calendar', 'v3', credentials=credentials)
        calendar_list = service.calendarList().list().execute()

        # Redirect to frontend with success
        return RedirectResponse(
            url=f"http://localhost:3001?auth=success&calendars={len(calendar_list.get('items', []))}"
        )

    except Exception as e:
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"http://localhost:3001?auth=error&message={str(e)}"
        )

@router.get("/status")
async def auth_status():
    """Check if user has authenticated"""
    user_id = "demo_user"

    # Check in-memory first
    if user_id in user_tokens:
        return {
            "authenticated": True,
            "scopes": user_tokens[user_id].get('scopes', [])
        }

    # Check file
    token_file = Path(__file__).parent.parent / 'token.json'
    if token_file.exists():
        with open(token_file, 'r') as f:
            token_data = json.load(f)
            user_tokens[user_id] = token_data
            return {
                "authenticated": True,
                "scopes": token_data.get('scopes', [])
            }

    return {"authenticated": False}

@router.post("/logout")
async def logout():
    """Clear authentication"""
    user_id = "demo_user"

    # Clear from memory
    if user_id in user_tokens:
        del user_tokens[user_id]

    # Clear token file
    token_file = Path(__file__).parent.parent / 'token.json'
    if token_file.exists():
        token_file.unlink()

    return {"status": "logged_out"}

@router.get("/calendars/selected")
async def get_selected_calendars():
    """Get which calendars the user wants to analyze"""
    user_id = "demo_user"
    return {"selected_calendars": user_calendar_selections.get(user_id, [])}

@router.post("/calendars/select")
async def select_calendars(calendar_ids: list[str]):
    """Set which calendars to analyze"""
    user_id = "demo_user"
    user_calendar_selections[user_id] = calendar_ids
    return {"status": "updated", "selected_calendars": calendar_ids}

def get_selected_calendar_ids():
    """Get selected calendar IDs for current user"""
    user_id = "demo_user"
    return user_calendar_selections.get(user_id, None)  # None = use all/default

def get_credentials():
    """Get stored credentials for API calls"""
    user_id = "demo_user"

    # Try memory first
    if user_id in user_tokens:
        token_data = user_tokens[user_id]
        return Credentials(
            token=token_data['token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )

    # Try file
    token_file = Path(__file__).parent.parent / 'token.json'
    if token_file.exists():
        with open(token_file, 'r') as f:
            token_data = json.load(f)
            user_tokens[user_id] = token_data
            return Credentials(
                token=token_data['token'],
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes']
            )

    return None
