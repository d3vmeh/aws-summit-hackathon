from datetime import datetime, timedelta, timezone
from typing import List
from schemas import StressScore, StressFactors, CalendarEvent, Task

class StressCalculator:
    @staticmethod
    def _to_naive(dt: datetime) -> datetime:
        """Convert datetime to timezone-naive UTC"""
        if dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt

    @staticmethod
    def calculate_stress_score(events: List[CalendarEvent], tasks: List[Task]) -> StressScore:
        factors = StressCalculator.get_stress_factors(events, tasks)

        # Calculate individual factor scores (0-100 scale)
        calendar_score = min(100, factors.calendar_density * 1.2 +
                            factors.events_next_7_days * 2)

        task_score = min(100, factors.overdue_tasks * 10 +
                        factors.high_priority_tasks * 5)
        sleep_score = max(0, 100 - (factors.sleep_hours_available * 12))

        # Weighted total: calendar 40%, tasks 30%, sleep 30%
        total = (calendar_score * 0.4 + task_score * 0.3 + sleep_score * 0.3)

        # Determine risk level
        if total > 80:
            risk_level = "critical"
        elif total > 60:
            risk_level = "high"
        elif total > 40:
            risk_level = "medium"
        else:
            risk_level = "low"

        return StressScore(
            total_score=round(total, 1),
            calendar_factor=round(calendar_score, 1),
            task_factor=round(task_score, 1),
            sleep_factor=round(sleep_score, 1),
            risk_level=risk_level,
            timestamp=datetime.now()
        )

    @staticmethod
    def get_stress_factors(events: List[CalendarEvent], tasks: List[Task]) -> StressFactors:
        now = StressCalculator._to_naive(datetime.now())
        next_week = now + timedelta(days=7)

        # Convert all event datetimes to naive
        events_naive = [(StressCalculator._to_naive(e.start), StressCalculator._to_naive(e.end))
                        for e in events]

        # Count events in next 7 days
        events_next_7 = sum(1 for start, end in events_naive if now <= start <= next_week)

        # Calculate calendar density (% of today that's scheduled)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=59)
        today_events = [(start, end) for start, end in events_naive
                       if today_start <= start <= today_end]

        total_scheduled_hours = sum(
            (end - start).total_seconds() / 3600
            for start, end in today_events
        )
        calendar_density = (total_scheduled_hours / 16) * 100  # Assume 16 waking hours

        # Count overdue and high-priority tasks
        overdue = sum(
            1 for t in tasks
            if not t.completed and t.due_date and StressCalculator._to_naive(t.due_date) < now
        )
        high_priority = sum(
            1 for t in tasks
            if not t.completed and t.priority == "high"
        )

        # Calculate sleep opportunity (simplified)
        sleep_hours = 8.0  # Default assumption

        return StressFactors(
              events_next_7_days=events_next_7,
              overdue_tasks=overdue,
              high_priority_tasks=high_priority,
              calendar_density=round(calendar_density, 1),
              sleep_hours_available=sleep_hours
          )