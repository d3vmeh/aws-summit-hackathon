from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CalendarEvent(BaseModel):
    id: str
    summary: str
    start: datetime
    end: datetime
    description: Optional[str] = None

class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high
    completed: bool = False

class StressScore(BaseModel):
    total_score: float
    calendar_factor: float
    task_factor: float
    sleep_factor: float
    risk_level: str  # low, medium, high, critical
    timestamp: datetime

class StressFactors(BaseModel):
    events_next_7_days: int
    overdue_tasks: int
    high_priority_tasks: int
    calendar_density: float
    sleep_hours_available: float

class Intervention(BaseModel):
    id: str
    type: str
    priority: str
    title: str
    description: str
    impact_score: float
    effort_score: float

class BurnoutPrediction(BaseModel):
    stress_score: StressScore
    factors: StressFactors
    predictions: List[str]
    interventions: List[Intervention]
    historical_comparison: Optional[str] = None