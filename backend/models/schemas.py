from pydantic import BaseModel, Field
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
    total_score: float = Field(..., ge=0, le=100, description="Overall stress score (0-100)")
    calendar_factor: float = Field(..., ge=0, le=100)
    task_factor: float = Field(..., ge=0, le=100)
    sleep_factor: float = Field(..., ge=0, le=100)
    risk_level: str  # low, medium, high, critical
    timestamp: datetime

class StressFactors(BaseModel):
    events_next_7_days: int
    overdue_tasks: int
    high_priority_tasks: int
    calendar_density: float  # percentage of day scheduled
    sleep_hours_available: float

class Intervention(BaseModel):
    id: str
    type: str  # reschedule, delegate, break_down, micro_break
    priority: str
    title: str
    description: str
    impact_score: float  # how much this reduces stress
    effort_score: float  # how much effort to implement

class BurnoutPrediction(BaseModel):
    stress_score: StressScore
    factors: StressFactors
    predictions: List[str]
    interventions: List[Intervention]
    historical_comparison: Optional[str] = None
