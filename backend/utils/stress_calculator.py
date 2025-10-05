from datetime import datetime, timedelta
from typing import List, Union
from models.schemas import CalendarEvent, Task, StressScore, StressFactors
import math

def parse_datetime(dt: Union[str, datetime]) -> datetime:
    """Parse datetime string or return datetime object (always timezone-naive)"""
    if isinstance(dt, str):
        # Handle ISO format with timezone
        if 'T' in dt:
            # Parse the datetime
            dt_obj = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            # Always return timezone-naive (strip timezone)
            return dt_obj.replace(tzinfo=None)
        else:
            return datetime.fromisoformat(dt)
    # If already datetime, make sure it's naive
    if isinstance(dt, datetime) and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

class StressCalculator:
    """Calculate stress scores based on calendar and task data"""

    @staticmethod
    def calculate_calendar_density(events: List[CalendarEvent], target_date: datetime = None) -> float:
        """Calculate percentage of day that is scheduled"""
        if not target_date:
            target_date = datetime.now()

        # Get events for target date
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        daily_events = [
            e for e in events
            if day_start <= parse_datetime(e.start) < day_end
        ]

        if not daily_events:
            return 0.0

        # Calculate total scheduled hours (assuming 16 waking hours)
        total_minutes = sum([
            (parse_datetime(e.end) - parse_datetime(e.start)).total_seconds() / 60
            for e in daily_events
        ])

        waking_minutes = 16 * 60  # 16 hours
        density = min((total_minutes / waking_minutes) * 100, 100)

        return round(density, 2)

    @staticmethod
    def calculate_sleep_opportunity(events: List[CalendarEvent]) -> float:
        """Calculate available sleep hours based on schedule gaps"""
        if not events:
            return 8.0  # default assumption

        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        # Get all events from past 24 hours and next 24 hours
        yesterday = today - timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)

        recent_events = [e for e in events if yesterday <= parse_datetime(e.start) < day_after]

        if not recent_events:
            return 8.0

        # Find the latest event that ended before now or today
        past_events = [e for e in recent_events if parse_datetime(e.end) <= now]
        if past_events:
            last_event_end = max([parse_datetime(e.end) for e in past_events])
        else:
            # No past events, assume reasonable bedtime
            last_event_end = today.replace(hour=22)

        # Find the earliest upcoming event
        future_events = [e for e in recent_events if parse_datetime(e.start) > now]
        if future_events:
            next_event_start = min([parse_datetime(e.start) for e in future_events])
        else:
            # No future events, assume reasonable wake time
            next_event_start = tomorrow.replace(hour=8)

        # Calculate potential sleep window
        # Assume sleep starts at max(last_event_end, 10 PM) and ends at min(next_event_start, 8 AM next day)
        reasonable_sleep_start = today.replace(hour=22) if last_event_end < today.replace(hour=22) else last_event_end
        reasonable_wake_time = tomorrow.replace(hour=8) if next_event_start > tomorrow.replace(hour=8) else next_event_start

        # Calculate sleep hours
        if reasonable_wake_time > reasonable_sleep_start:
            sleep_hours = (reasonable_wake_time - reasonable_sleep_start).total_seconds() / 3600
            # Cap at reasonable max (12 hours)
            return round(min(sleep_hours, 12.0), 2)
        else:
            return 0.0

    @staticmethod
    def calculate_task_pressure(tasks: List[Task]) -> tuple[int, int]:
        """Calculate number of overdue and high priority tasks"""
        now = datetime.now()

        overdue = sum(1 for t in tasks if t.due_date and parse_datetime(t.due_date) < now and not t.completed)
        high_priority = sum(1 for t in tasks if t.priority == "high" and not t.completed)

        return overdue, high_priority

    @staticmethod
    def calculate_stress_score(events: List[CalendarEvent], tasks: List[Task]) -> StressScore:
        """Calculate comprehensive stress score"""
        now = datetime.now()
        next_week = now + timedelta(days=7)

        # Get events in next 7 days
        upcoming_events = [e for e in events if now <= parse_datetime(e.start) <= next_week]
        events_count = len(upcoming_events)

        # Calculate factors
        calendar_density = StressCalculator.calculate_calendar_density(events, now)
        sleep_hours = StressCalculator.calculate_sleep_opportunity(events)
        overdue, high_priority = StressCalculator.calculate_task_pressure(tasks)

        # Calculate individual factor scores (0-100)

        # Calendar factor: based on density and number of events
        calendar_factor = min(
            (calendar_density * 0.6) + (events_count * 2),
            100
        )

        # Task factor: based on overdue and high priority tasks
        task_factor = min(
            (overdue * 10) + (high_priority * 5),
            100
        )

        # Sleep factor: inverse of sleep hours (less sleep = higher stress)
        sleep_factor = max(100 - (sleep_hours * 12.5), 0)  # 8 hours = 0 stress

        # Total stress score (weighted average)
        total_score = (
            calendar_factor * 0.4 +
            task_factor * 0.3 +
            sleep_factor * 0.3
        )

        # Determine risk level
        if total_score >= 80:
            risk_level = "critical"
        elif total_score >= 60:
            risk_level = "high"
        elif total_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"

        return StressScore(
            total_score=round(total_score, 2),
            calendar_factor=round(calendar_factor, 2),
            task_factor=round(task_factor, 2),
            sleep_factor=round(sleep_factor, 2),
            risk_level=risk_level,
            timestamp=now
        )

    @staticmethod
    def get_stress_factors(events: List[CalendarEvent], tasks: List[Task]) -> StressFactors:
        """Get detailed stress factors"""
        now = datetime.now()
        next_week = now + timedelta(days=7)

        upcoming_events = [e for e in events if now <= parse_datetime(e.start) <= next_week]
        overdue, high_priority = StressCalculator.calculate_task_pressure(tasks)

        return StressFactors(
            events_next_7_days=len(upcoming_events),
            overdue_tasks=overdue,
            high_priority_tasks=high_priority,
            calendar_density=StressCalculator.calculate_calendar_density(events, now),
            sleep_hours_available=StressCalculator.calculate_sleep_opportunity(events)
        )
