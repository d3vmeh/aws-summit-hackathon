from typing import List
from models.schemas import Intervention, StressScore, StressFactors, Task, CalendarEvent
from datetime import datetime, timedelta
import uuid
from utils.stress_calculator import parse_datetime

class InterventionEngine:
    """Generate actionable interventions to reduce stress"""

    @staticmethod
    def generate_interventions(
        stress_score: StressScore,
        factors: StressFactors,
        tasks: List[Task],
        events: List[CalendarEvent]
    ) -> List[Intervention]:
        """Generate prioritized list of interventions"""
        interventions = []

        # High task factor interventions with specific task references
        now = datetime.now()
        if stress_score.task_factor > 60:
            if factors.overdue_tasks > 0:
                # Find first overdue task for specific reference
                overdue_tasks = [t for t in tasks if t.due_date and parse_datetime(t.due_date) < now and not t.completed]
                first_overdue = overdue_tasks[0] if overdue_tasks else None

                if first_overdue:
                    interventions.append(Intervention(
                        id=str(uuid.uuid4()),
                        type="delegate",
                        priority="critical",
                        title=f"Complete overdue: {first_overdue.title[:30]}",
                        description=f"'{first_overdue.title}' is overdue. Tackle this first thing today or delegate if possible. You have {factors.overdue_tasks} total overdue task(s) creating mental burden.",
                        impact_score=40.0,
                        effort_score=30.0
                    ))

            if factors.high_priority_tasks > 3:
                # Find a specific high priority task
                high_pri_tasks = [t for t in tasks if t.priority == "high" and not t.completed]
                if high_pri_tasks:
                    interventions.append(Intervention(
                        id=str(uuid.uuid4()),
                        type="break_down",
                        priority="high",
                        title=f"Break down: {high_pri_tasks[0].title[:30]}",
                        description=f"'{high_pri_tasks[0].title}' is complex. Split it into 3-4 smaller subtasks with mini-deadlines. You have {factors.high_priority_tasks} high-priority items competing for attention.",
                        impact_score=35.0,
                        effort_score=20.0
                    ))

        # High calendar density interventions
        if stress_score.calendar_factor > 60:
            if factors.calendar_density > 70:
                interventions.append(Intervention(
                    id=str(uuid.uuid4()),
                    type="reschedule",
                    priority="high",
                    title="Reduce Calendar Density",
                    description=f"Your calendar is {factors.calendar_density}% full. Consider rescheduling non-urgent meetings.",
                    impact_score=35.0,
                    effort_score=25.0
                ))

            # Find gaps for deep work
            interventions.append(Intervention(
                id=str(uuid.uuid4()),
                type="micro_break",
                priority="medium",
                title="Schedule Focus Blocks",
                description="Block 2-hour windows in your calendar for deep work on high-priority tasks.",
                impact_score=20.0,
                effort_score=10.0
            ))

        # Sleep deficit interventions
        if stress_score.sleep_factor > 60:
            interventions.append(Intervention(
                id=str(uuid.uuid4()),
                type="reschedule",
                priority="critical",
                title="Protect Sleep Time",
                description=f"You only have {factors.sleep_hours_available} hours for sleep. Move late evening commitments to daytime.",
                impact_score=40.0,
                effort_score=20.0
            ))

        # General wellness interventions
        if stress_score.total_score > 70:
            interventions.append(Intervention(
                id=str(uuid.uuid4()),
                type="micro_break",
                priority="high",
                title="Schedule Recovery Time",
                description="Block a 3-hour window this weekend for rest and recovery.",
                impact_score=30.0,
                effort_score=15.0
            ))

        # Identify specific events that can be rescheduled
        next_week = now + timedelta(days=7)
        upcoming_events = [e for e in events if now <= parse_datetime(e.start) <= next_week]

        if len(upcoming_events) > 10 and stress_score.total_score > 60:
            # Find events with "optional" or social keywords
            optional_keywords = ["coffee", "chat", "catch up", "social", "optional", "lunch", "networking"]
            reschedulable = [
                e for e in upcoming_events
                if any(keyword in e.summary.lower() for keyword in optional_keywords)
            ]

            if reschedulable:
                event = reschedulable[0]
                event_day = parse_datetime(event.start).strftime('%A')
                event_time = parse_datetime(event.start).strftime('%I:%M%p')
                interventions.append(Intervention(
                    id=str(uuid.uuid4()),
                    type="reschedule",
                    priority="medium",
                    title=f"Reschedule '{event.summary[:25]}'",
                    description=f"Move '{event.summary}' from {event_day} at {event_time} to next week. This gives you breathing room during a packed week with {len(upcoming_events)} events.",
                    impact_score=25.0,
                    effort_score=15.0
                ))

        # Suggest time-blocking for concentrated work if calendar is fragmented
        if factors.events_next_7_days > 8 and stress_score.total_score > 50:
            interventions.append(Intervention(
                id=str(uuid.uuid4()),
                type="micro_break",
                priority="high",
                title="Block 2-hour deep work sessions",
                description=f"With {factors.events_next_7_days} events this week, your schedule is fragmented. Block two 2-hour 'Do Not Disturb' sessions for focused work on high-priority tasks.",
                impact_score=30.0,
                effort_score=20.0
            ))

        # Sort by impact/effort ratio (highest first)
        interventions.sort(key=lambda x: x.impact_score / x.effort_score, reverse=True)

        return interventions[:5]  # Return top 5 interventions
