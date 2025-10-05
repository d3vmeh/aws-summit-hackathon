from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from typing import List
from models.schemas import CalendarEvent

def fetch_google_calendar_events(
    credentials: Credentials,
    days_ahead: int = 7,
    calendar_ids: List[str] = None
) -> List[CalendarEvent]:
    """Fetch calendar events from Google Calendar"""
    try:
        service = build('calendar', 'v3', credentials=credentials)

        # Time range
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

        # Default to primary calendar if no specific calendars selected
        if not calendar_ids:
            calendar_ids = ['primary']

        # Fetch events from all selected calendars
        all_events = []
        for calendar_id in calendar_ids:
            try:
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=100,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                all_events.extend(events_result.get('items', []))
            except Exception as e:
                print(f"Warning: Failed to fetch from calendar {calendar_id}: {e}")
                continue

        events = all_events

        # Convert to our schema
        calendar_events = []
        for event in events:
            # Handle all-day events vs timed events
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # Parse datetime strings
            if 'T' in start:  # dateTime format
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            else:  # date format (all-day event)
                start_dt = datetime.fromisoformat(start + 'T00:00:00')
                end_dt = datetime.fromisoformat(end + 'T23:59:59')

            calendar_events.append(CalendarEvent(
                id=event['id'],
                summary=event.get('summary', 'No Title'),
                start=start_dt.isoformat(),
                end=end_dt.isoformat(),
                description=event.get('description', '')
            ))

        return calendar_events

    except Exception as e:
        raise Exception(f"Failed to fetch Google Calendar events: {str(e)}")

def get_calendar_info(credentials: Credentials):
    """Get user's calendar metadata"""
    try:
        service = build('calendar', 'v3', credentials=credentials)

        # Get calendar list
        calendar_list = service.calendarList().list().execute()

        calendars = []
        for calendar in calendar_list.get('items', []):
            calendars.append({
                'id': calendar['id'],
                'summary': calendar.get('summary', 'Unknown'),
                'primary': calendar.get('primary', False),
                'backgroundColor': calendar.get('backgroundColor', '#000000')
            })

        return calendars

    except Exception as e:
        raise Exception(f"Failed to fetch calendar info: {str(e)}")
