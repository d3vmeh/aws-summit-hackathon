"""
Simple Google Calendar Integration
Handles OAuth and fetching calendar events
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv

from schemas import CalendarEvent

load_dotenv()

# OAuth configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE = Path(__file__).parent / 'token.json'
CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'


class GoogleCalendarClient:
    """Simple Google Calendar client"""

    def __init__(self):
        self.credentials: Optional[Credentials] = None
        self._load_credentials()

    def _load_credentials(self):
        """Load credentials from token.json if it exists"""
        if TOKEN_FILE.exists():
            try:
                with open(TOKEN_FILE, 'r') as f:
                    token_data = json.load(f)

                self.credentials = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes', SCOPES)
                )

                # Refresh if expired
                if self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self._save_credentials()

            except Exception as e:
                print(f"Error loading credentials: {e}")
                self.credentials = None

    def _save_credentials(self):
        """Save credentials to token.json"""
        if not self.credentials:
            return

        token_data = {
            'token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token,
            'token_uri': self.credentials.token_uri,
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
            'scopes': self.credentials.scopes
        }

        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)

    def get_auth_url(self) -> str:
        """Get the OAuth authorization URL"""
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                f"credentials.json not found at {CREDENTIALS_FILE}. "
                "Please download it from Google Cloud Console."
            )

        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/auth/google/callback')

        flow = Flow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        return auth_url

    def handle_oauth_callback(self, code: str):
        """Handle OAuth callback and save credentials"""
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError("credentials.json not found")

        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/auth/google/callback')

        flow = Flow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

        flow.fetch_token(code=code)
        self.credentials = flow.credentials
        self._save_credentials()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.credentials is not None and self.credentials.valid

    def disconnect(self):
        """Disconnect/logout - remove token file"""
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
        self.credentials = None

    def fetch_events(self, days_ahead: int = 7) -> List[CalendarEvent]:
        """
        Fetch calendar events from Google Calendar

        Args:
            days_ahead: Number of days ahead to fetch events

        Returns:
            List of CalendarEvent objects
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated. Please connect Google Calendar first.")

        try:
            service = build('calendar', 'v3', credentials=self.credentials)

            # Time range
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

            # Fetch events from primary calendar
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Convert to CalendarEvent objects
            calendar_events = []
            for event in events:
                # Handle all-day vs timed events
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                # Parse datetime
                if 'T' in start:  # dateTime format
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                else:  # date format (all-day event)
                    start_dt = datetime.fromisoformat(start + 'T00:00:00')
                    end_dt = datetime.fromisoformat(end + 'T23:59:59')

                calendar_events.append(CalendarEvent(
                    id=event['id'],
                    summary=event.get('summary', 'No Title'),
                    start=start_dt,
                    end=end_dt,
                    description=event.get('description', '')
                ))

            return calendar_events

        except Exception as e:
            raise Exception(f"Failed to fetch Google Calendar events: {str(e)}")


# Global client instance
_calendar_client = None

def get_calendar_client() -> GoogleCalendarClient:
    """Get or create the global calendar client"""
    global _calendar_client
    if _calendar_client is None:
        _calendar_client = GoogleCalendarClient()
    return _calendar_client
