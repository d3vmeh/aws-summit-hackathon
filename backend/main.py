from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from typing import List

# Import your modules
from schemas import BurnoutPrediction, CalendarEvent, Task
from stress_calculator import StressCalculator
from ai_response import generate_burnout_predictions, generate_ai_interventions
from google_calendar import get_calendar_client

app = FastAPI(title="Burnout Prevention API", version="1.0.0")

# Enable CORS (allows frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (temporary - replace with database later)
events_db: List[CalendarEvent] = []
tasks_db: List[Task] = []

@app.get("/")
def root():
    return {
        "message": "Burnout Prevention API",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    events: List[CalendarEvent]
    tasks: List[Task]

@app.post("/api/stress/analyze", response_model=BurnoutPrediction)
async def analyze_stress(request: AnalyzeRequest):
    """
    Main endpoint: Analyze stress and generate predictions/interventions
    """
    try:
        print("Step 1: Calculating stress score...")
        # Step 1: Calculate stress score
        stress_score = StressCalculator.calculate_stress_score(request.events, request.tasks)
        factors = StressCalculator.get_stress_factors(request.events, request.tasks)
        print(f"Stress score calculated: {stress_score.total_score}")

        print("Step 2: Generating AI predictions...")
        # Step 2: Get AI predictions
        predictions = generate_burnout_predictions(request.events, request.tasks, factors)
        print(f"Predictions generated: {len(predictions)}")

        print("Step 3: Generating AI interventions...")
        # Step 3: Get AI interventions
        interventions = generate_ai_interventions(
            request.events, request.tasks, factors, stress_score.total_score
        )
        print(f"Interventions generated: {len(interventions)}")

        # Step 4: Return complete analysis
        return BurnoutPrediction(
            stress_score=stress_score,
            factors=factors,
            predictions=predictions,
            interventions=interventions,
            historical_comparison=None
        )

    except Exception as e:
        print(f"Error analyzing stress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Google Calendar OAuth endpoints
@app.get("/auth/google")
def google_auth():
    """Initiate Google Calendar OAuth flow"""
    try:
        client = get_calendar_client()
        auth_url = client.get_auth_url()
        return {"auth_url": auth_url}
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth initialization failed: {str(e)}")

@app.get("/auth/google/callback")
def google_callback(code: str):
    """Handle Google OAuth callback"""
    try:
        client = get_calendar_client()
        client.handle_oauth_callback(code)

        # Redirect to frontend with success
        return RedirectResponse(url="http://localhost:3000?auth=success")

    except Exception as e:
        # Redirect to frontend with error
        return RedirectResponse(url=f"http://localhost:3000?auth=error&message={str(e)}")

@app.get("/auth/status")
def auth_status():
    """Check if user is authenticated with Google Calendar"""
    client = get_calendar_client()
    return {
        "authenticated": client.is_authenticated(),
        "provider": "Google Calendar" if client.is_authenticated() else None
    }

@app.post("/auth/disconnect")
def disconnect():
    """Disconnect Google Calendar"""
    client = get_calendar_client()
    client.disconnect()
    return {"status": "disconnected"}

# Calendar endpoints
@app.get("/api/calendar/events")
def get_events(days_ahead: int = 7):
    """
    Get calendar events - from Google Calendar if connected, otherwise return empty list
    """
    client = get_calendar_client()

    if client.is_authenticated():
        try:
            # Fetch from Google Calendar
            events = client.fetch_events(days_ahead=days_ahead)
            return events
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")
    else:
        # Return empty list if not authenticated
        return []

@app.get("/api/calendar/sync")
def sync_calendar(days_ahead: int = 7):
    """
    Manually trigger calendar sync from Google Calendar
    """
    client = get_calendar_client()

    if not client.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated. Please connect Google Calendar first.")

    try:
        events = client.fetch_events(days_ahead=days_ahead)
        return {
            "status": "synced",
            "events_count": len(events),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

# Task endpoints
@app.get("/api/tasks/")
def get_tasks():
    """Get all stored tasks"""
    return tasks_db

@app.post("/api/tasks/")
def create_task(task: Task):
    """Add a task"""
    tasks_db.append(task)
    return task