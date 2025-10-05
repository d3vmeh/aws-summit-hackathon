from datetime import datetime, timedelta
from typing import List, Union
import math
from schemas import CalendarEvent, Task, StressScore, StressFactors

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

def get_week_range(target_date: datetime = None):
    """Return the start and end datetime for a 7-day window starting from target_date (default: today)"""
    if not target_date:
        target_date = datetime.now()
    start_of_week = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)
    return start_of_week, end_of_week

def get_sleep_quality_message(sleep_hours: float) -> str:
    """Provide research-based context about sleep quality for college students"""
    if sleep_hours >= 8:
        return "Excellent - meeting recommended 7-9 hours for optimal performance"
    elif sleep_hours >= 7:
        return "Good - within recommended range for young adults"
    elif sleep_hours >= 6:
        return "Insufficient - below 7-hour minimum, may impact performance"
    elif sleep_hours >= 4:
        return "Severely deprived - cognitive effects similar to 48-hour sleep deprivation"
    else:
        return "Critical - major health and academic risk, seek support immediately"

class StressCalculator:
    """Calculate stress scores based on calendar and task data"""

    @staticmethod
    def calculate_calendar_density(events: List[CalendarEvent], target_date: datetime = None) -> float:
        """Calculate percentage of waking hours scheduled for the week, with debug output"""
        week_start, week_end = get_week_range(target_date)
        weekly_events = [e for e in events if week_start <= parse_datetime(e.start) < week_end]
        print(f"[DEBUG] Week start: {week_start}, Week end: {week_end}")
        print(f"[DEBUG] Number of events in week: {len(weekly_events)}")
        for e in weekly_events:
            print(f"[DEBUG] Event: id={e.id}, summary={e.summary}, start={parse_datetime(e.start)}, end={parse_datetime(e.end)}")
        if not weekly_events:
            return 0.0
        total_minutes = sum([
            (parse_datetime(e.end) - parse_datetime(e.start)).total_seconds() / 60
            for e in weekly_events
        ])
        print(f"[DEBUG] Total scheduled minutes: {total_minutes}")
        waking_minutes = 16 * 60 * 7
        density = min((total_minutes / waking_minutes) * 100, 100)
        print(f"[DEBUG] Calendar density: {density}")
        return round(density, 2)

    @staticmethod
    def calculate_average_break_length(events: List[CalendarEvent], target_date: datetime = None) -> float:
        """Calculate average break length (in minutes) between events for the week"""
        week_start, week_end = get_week_range(target_date)
        weekly_events = [e for e in events if week_start <= parse_datetime(e.start) < week_end]
        if not weekly_events or len(weekly_events) == 1:
            return 16 * 60  # If 0 or 1 event, assume max break (all waking hours)
        # Sort events by start time
        sorted_events = sorted(weekly_events, key=lambda e: parse_datetime(e.start))
        breaks = []
        for i in range(1, len(sorted_events)):
            prev_end = parse_datetime(sorted_events[i-1].end)
            curr_start = parse_datetime(sorted_events[i].start)
            gap = (curr_start - prev_end).total_seconds() / 60
            if gap > 0:
                breaks.append(gap)
        if not breaks:
            return 0.0
        avg_break = sum(breaks) / len(breaks)
        return round(avg_break, 2)

    @staticmethod
    def calculate_sleep_opportunity(events: List[CalendarEvent], target_date: datetime = None) -> float:
        """Calculate available sleep hours based on largest gap in the typical sleep window (10pm-8am) for each night in the week (average per night)"""
        week_start, week_end = get_week_range(target_date)
        sleep_hours = []
        for day in range(7):
            day_start = week_start + timedelta(days=day)
            # Define sleep window: 10pm this day to 8am next day
            sleep_start = day_start.replace(hour=22, minute=0, second=0, microsecond=0)
            sleep_end = (day_start + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            # Get all events that overlap with the sleep window
            window_events = []
            for e in events:
                e_start = parse_datetime(e.start)
                e_end = parse_datetime(e.end)
                # If event overlaps with sleep window
                if e_end > sleep_start and e_start < sleep_end:
                    # Clip event to sleep window
                    clipped_start = max(e_start, sleep_start)
                    clipped_end = min(e_end, sleep_end)
                    window_events.append((clipped_start, clipped_end))
            # Add artificial window boundaries as 'events' for easier gap calculation
            window_events.append((sleep_start, sleep_start))
            window_events.append((sleep_end, sleep_end))
            # Sort by start time
            window_events.sort()
            # Find largest gap between events
            max_gap = 0
            for i in range(1, len(window_events)):
                prev_end = window_events[i-1][1]
                curr_start = window_events[i][0]
                gap = (curr_start - prev_end).total_seconds() / 3600
                if gap > max_gap:
                    max_gap = gap
            # Cap at 12 hours (max possible in window)
            sleep_hours.append(min(max_gap, 12.0))
        avg_sleep = sum(sleep_hours) / len(sleep_hours)
        return round(avg_sleep, 2)

    @staticmethod
    def calculate_immediate_tasks(tasks: List[Task]) -> int:
        """Calculate number of tasks due today or tomorrow"""
        now = datetime.now()
        tomorrow_end = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

        immediate_tasks = sum(
            1 for t in tasks
            if not t.completed
            and t.due_date
            and parse_datetime(t.due_date) <= tomorrow_end
        )

        return immediate_tasks

    @staticmethod
    def calculate_stress_score(events: List[CalendarEvent], tasks: List[Task]) -> StressScore:
        """Calculate comprehensive stress score, now including event AI stress classification, with debug output"""
        from utils.event_ai_classification import classify_event_stress
        now = datetime.now()
        week_start, week_end = get_week_range(now)
        upcoming_events = [e for e in events if week_start <= parse_datetime(e.start) < week_end]
        print(f"[DEBUG] Number of events considered for stress score: {len(upcoming_events)}")
        events_count = len(upcoming_events)
        event_stress_labels = classify_event_stress(upcoming_events)
        print(f"[DEBUG] Event stress labels: {event_stress_labels}")
        high_stress_count = sum(1 for eid, label in event_stress_labels.items() if label == 'high_stress')
        recreational_count = sum(1 for eid, label in event_stress_labels.items() if label == 'recreational')
        calendar_density = StressCalculator.calculate_calendar_density(events, now)
        sleep_hours = StressCalculator.calculate_sleep_opportunity(events, now)
        avg_break = StressCalculator.calculate_average_break_length(events, now)
        immediate_tasks = StressCalculator.calculate_immediate_tasks(tasks)
        print(f"[DEBUG] Immediate tasks (due today/tomorrow): {immediate_tasks}")
        # Calendar factor with floor bounds to prevent negative values
        calendar_factor = max(0, min(
            (calendar_density * 0.4) + (events_count * 1.2) + (high_stress_count * 4) - (recreational_count * 2),
            100
        ))
        print(f"[DEBUG] Calendar factor: {calendar_factor}")
        # Task factor using logarithmic scaling for more realistic stress progression
        # 0 tasks = 0, 1 task = 21, 3 tasks = 52, 5 tasks = 67, 10 tasks = 90
        task_factor = min(30 * math.log1p(immediate_tasks * 2), 100)
        print(f"[DEBUG] Task factor: {task_factor}")
        sleep_factor = max(100 - (sleep_hours * 12.5), 0)
        print(f"[DEBUG] Sleep factor: {sleep_factor}")
        if avg_break >= 60:
            break_factor = 0
        elif avg_break >= 30:
            break_factor = 30
        elif avg_break >= 15:
            break_factor = 60
        else:
            break_factor = 90
        print(f"[DEBUG] Break factor: {break_factor}")
        # Research-backed weights: Sleep and workload are primary burnout factors
        # Sleep: 30% (accounts for 25% variance in academic performance)
        # Calendar: 30% (75% of students overwhelmed by workload)
        # Breaks: 20% (important for recovery)
        # Tasks: 20% (immediate deadline pressure)
        total_score = (
            calendar_factor * 0.30 +
            task_factor * 0.20 +
            sleep_factor * 0.30 +
            break_factor * 0.20
        )
        print(f"[DEBUG] Total stress score: {total_score}")
        if total_score >= 80:
            risk_level = "critical"
        elif total_score >= 60:
            risk_level = "high"
        elif total_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"
        print(f"[DEBUG] Risk level: {risk_level}")
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
        """Get detailed stress factors, including break length and week analysis"""
        now = datetime.now()
        week_start, week_end = get_week_range(now)
        upcoming_events = [e for e in events if week_start <= parse_datetime(e.start) < week_end]
        immediate_tasks = StressCalculator.calculate_immediate_tasks(tasks)
        sleep_hours = StressCalculator.calculate_sleep_opportunity(events, now)
        return StressFactors(
            events_next_7_days=len(upcoming_events),
            immediate_action_tasks=immediate_tasks,
            calendar_density=StressCalculator.calculate_calendar_density(events, now),
            sleep_hours_available=sleep_hours,
            average_break_length=StressCalculator.calculate_average_break_length(events, now),
            sleep_quality_message=get_sleep_quality_message(sleep_hours)
        )
