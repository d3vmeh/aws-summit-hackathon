from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Import your modules
from schemas import BurnoutPrediction, CalendarEvent, Task
from stress_calculator import StressCalculator
from ai_response import generate_burnout_predictions, generate_ai_interventions

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

# Optional endpoints for managing data
@app.get("/api/calendar/events")
def get_events():
    """Get all stored events"""
    return events_db

@app.post("/api/calendar/events")
def create_event(event: CalendarEvent):
    """Add an event"""
    events_db.append(event)
    return event

@app.get("/api/tasks/")
def get_tasks():
    """Get all stored tasks"""
    return tasks_db

@app.post("/api/tasks/")
def create_task(task: Task):
    """Add a task"""
    tasks_db.append(task)
    return task