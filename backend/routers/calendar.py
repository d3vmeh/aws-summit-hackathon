from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional
from models.schemas import CalendarEvent
from datetime import datetime, timedelta
from utils.google_calendar import fetch_google_calendar_events, get_calendar_info
from utils.descope_utils import get_user_google_calendar_token, refresh_user_google_calendar_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_user_from_session(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user ID from Descope session token"""
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>" format
        token = authorization.replace("Bearer ", "")
        
        # For now, return a placeholder user ID
        # In production, you'd decode the JWT to get actual user ID
        return "user_from_token"
    except Exception as e:
        logger.error(f"Failed to extract user from session: {e}")
        return None

# Mock data for fallback when not authenticated
mock_events = [
    CalendarEvent(
        id="1",
        summary="CS 101 Lecture",
        start=(datetime.now() + timedelta(hours=2)).isoformat(),
        end=(datetime.now() + timedelta(hours=3)).isoformat(),
        description="Data Structures"
    ),
    CalendarEvent(
        id="2",
        summary="Group Project Meeting",
        start=(datetime.now() + timedelta(days=1, hours=10)).isoformat(),
        end=(datetime.now() + timedelta(days=1, hours=11, minutes=30)).isoformat(),
        description="Final project discussion"
    ),
    CalendarEvent(
        id="3",
        summary="Midterm Exam - Algorithms",
        start=(datetime.now() + timedelta(days=3, hours=14)).isoformat(),
        end=(datetime.now() + timedelta(days=3, hours=16)).isoformat(),
        description="Chapters 1-5"
    ),
]

@router.get("/events", response_model=List[CalendarEvent])
async def get_calendar_events(
    use_mock: bool = False,
    user_id: Optional[str] = Depends(get_user_from_session)
):
    """Get calendar events from Google Calendar via Descope outbound app or mock data"""

    if not user_id:
        # Return mock data if not authenticated
        return mock_events

    if use_mock:
        return mock_events

    try:
        # Get access token from Descope outbound app
        access_token = get_user_google_calendar_token(user_id)
        
        if not access_token:
            # Try to refresh the token
            access_token = refresh_user_google_calendar_token(user_id)
        
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="No Google Calendar access token available. Please reconnect your calendar."
            )

        # Create credentials object from access token
        from google.oauth2.credentials import Credentials
        credentials = Credentials(token=access_token)

        # Fetch real Google Calendar events
        events = fetch_google_calendar_events(
            credentials,
            days_ahead=7
        )
        return events
        
    except Exception as e:
        logger.error(f"Failed to fetch Google Calendar events: {e}")
        # Fall back to mock data on error
        return mock_events

@router.get("/info")
async def get_calendar_metadata(user_id: Optional[str] = Depends(get_user_from_session)):
    """Get user's calendar information"""
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please sign in first."
        )

    try:
        # Get access token from Descope outbound app
        access_token = get_user_google_calendar_token(user_id)
        
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="No Google Calendar access token available. Please connect your calendar."
            )

        # Create credentials object from access token
        from google.oauth2.credentials import Credentials
        credentials = Credentials(token=access_token)

        calendars = get_calendar_info(credentials)
        return {
            "calendars": calendars,
            "count": len(calendars)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch calendar info: {str(e)}"
        )

@router.get("/sync")
async def sync_google_calendar(user_id: Optional[str] = Depends(get_user_from_session)):
    """Sync with Google Calendar via Descope outbound app"""
    if not user_id:
        return {
            "status": "not_authenticated",
            "message": "Please sign in first"
        }

    try:
        # Get access token from Descope outbound app
        access_token = get_user_google_calendar_token(user_id)
        
        if not access_token:
            return {
                "status": "not_connected",
                "message": "Please connect your Google Calendar first"
            }

        # Create credentials object from access token
        from google.oauth2.credentials import Credentials
        credentials = Credentials(token=access_token)

        # Fetch latest events
        events = fetch_google_calendar_events(credentials, days_ahead=7)

        return {
            "status": "success",
            "events_synced": len(events),
            "last_sync": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sync failed: {str(e)}"
        )

@router.post("/events", response_model=CalendarEvent)
async def create_event(
    event: CalendarEvent,
    user_id: Optional[str] = Depends(get_user_from_session)
):
    """Create a new calendar event"""
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please sign in first."
        )

    # For now, just add to mock data
    # In production, you would create the event in Google Calendar using the access token
    mock_events.append(event)
    return event

@router.delete("/connection")
async def disconnect_google_calendar(user_id: Optional[str] = Depends(get_user_from_session)):
    """Disconnect Google Calendar via Descope outbound app"""
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please sign in first."
        )

    try:
        from utils.descope_utils import get_descope_client
        client = get_descope_client()
        client.mgmt.outbound_app.delete_user_tokens(
            app_id="google-calendar",
            user_id=user_id
        )
        return {"status": "success", "message": "Google Calendar disconnected successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to disconnect Google Calendar"
        )
