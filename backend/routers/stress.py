from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import BurnoutPrediction, CalendarEvent, Task
from utils.stress_calculator import StressCalculator
from utils.intervention_engine import InterventionEngine
from utils.ai_insights import generate_burnout_predictions, generate_ai_interventions, generate_fallback_predictions
import os

router = APIRouter()

def generate_fallback_predictions_local(factors):
    """Local fallback predictions if AI is not configured"""
    predictions = []

    if factors.overdue_tasks > 3:
        predictions.append("High number of overdue tasks may indicate difficulty with time management")

    if factors.calendar_density > 70:
        predictions.append("Calendar density above 70% suggests limited time for breaks and recovery")

    if factors.sleep_hours_available < 6:
        predictions.append("Sleep deficit detected - less than 6 hours available may impact cognitive performance")

    if factors.events_next_7_days > 20:
        predictions.append("Heavy event load in upcoming week may lead to meeting fatigue")

    if not predictions:
        predictions.append("Current workload appears manageable with proper time management")

    return predictions

@router.post("/analyze", response_model=BurnoutPrediction)
async def analyze_stress(events: List[CalendarEvent], tasks: List[Task]):
    """Analyze stress levels based on calendar and task data"""
    try:
        # Calculate stress score
        stress_score = StressCalculator.calculate_stress_score(events, tasks)

        # Get detailed factors
        factors = StressCalculator.get_stress_factors(events, tasks)

        # Generate AI-powered predictions or fallback to rule-based
        use_ai = os.getenv('OPENAI_API_KEY') is not None

        if use_ai:
            try:
                predictions = generate_burnout_predictions(
                    events,
                    tasks,
                    {
                        'events_next_7_days': factors.events_next_7_days,
                        'calendar_density': factors.calendar_density,
                        'sleep_hours_available': factors.sleep_hours_available,
                        'overdue_tasks': factors.overdue_tasks,
                        'high_priority_tasks': factors.high_priority_tasks
                    }
                )
            except Exception as e:
                print(f"AI predictions failed, using fallback: {e}")
                predictions = generate_fallback_predictions({
                    'events_next_7_days': factors.events_next_7_days,
                    'calendar_density': factors.calendar_density,
                    'sleep_hours_available': factors.sleep_hours_available,
                    'overdue_tasks': factors.overdue_tasks,
                    'high_priority_tasks': factors.high_priority_tasks
                })
        else:
            predictions = generate_fallback_predictions_local(factors)

        # Generate AI-powered interventions or fallback to rule-based
        if use_ai:
            try:
                interventions = generate_ai_interventions(
                    events,
                    tasks,
                    {
                        'events_next_7_days': factors.events_next_7_days,
                        'calendar_density': factors.calendar_density,
                        'sleep_hours_available': factors.sleep_hours_available,
                        'overdue_tasks': factors.overdue_tasks,
                        'high_priority_tasks': factors.high_priority_tasks
                    },
                    stress_score.total_score
                )
            except Exception as e:
                print(f"AI interventions failed, using fallback: {e}")
                interventions = InterventionEngine.generate_interventions(
                    stress_score, factors, tasks, events
                )
        else:
            interventions = InterventionEngine.generate_interventions(
                stress_score, factors, tasks, events
            )

        # Historical comparison (placeholder for MVP)
        historical_comparison = None
        if stress_score.total_score > 70:
            historical_comparison = "You're 2.3x busier than your average week"

        return BurnoutPrediction(
            stress_score=stress_score,
            factors=factors,
            predictions=predictions,
            interventions=interventions,
            historical_comparison=historical_comparison
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def stress_health():
    return {"status": "stress analysis service is running"}
