"""
AI-powered event stress classification using keyword analysis
Classifies calendar events as 'high_stress', 'neutral', or 'recreational'
"""
from typing import List, Dict
from schemas import CalendarEvent

# Keywords for event classification
HIGH_STRESS_KEYWORDS = [
    'exam', 'test', 'quiz', 'midterm', 'final', 'interview', 'presentation',
    'deadline', 'meeting', 'review', 'assessment', 'evaluation', 'project due',
    'submission', 'defense', 'thesis', 'dissertation', 'lab', 'homework'
]

RECREATIONAL_KEYWORDS = [
    'gym', 'workout', 'exercise', 'yoga', 'meditation', 'break', 'lunch',
    'dinner', 'coffee', 'social', 'party', 'game', 'movie', 'concert',
    'sports', 'club', 'relax', 'hobby', 'fun', 'hang out', 'chill'
]

def classify_event_stress(events: List[CalendarEvent]) -> Dict[str, str]:
    """
    Classify events as 'high_stress', 'neutral', or 'recreational' based on keywords

    Args:
        events: List of CalendarEvent objects

    Returns:
        Dictionary mapping event IDs to stress labels
    """
    classifications = {}

    for event in events:
        # Combine summary and description for analysis
        text = f"{event.summary} {event.description or ''}".lower()

        # Check for high stress keywords
        is_high_stress = any(keyword in text for keyword in HIGH_STRESS_KEYWORDS)

        # Check for recreational keywords
        is_recreational = any(keyword in text for keyword in RECREATIONAL_KEYWORDS)

        # Determine classification (high stress takes precedence)
        if is_high_stress:
            label = 'high_stress'
        elif is_recreational:
            label = 'recreational'
        else:
            label = 'neutral'

        classifications[event.id] = label

    return classifications
