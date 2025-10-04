from openai import OpenAI
from typing import List, Dict
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from models.schemas import CalendarEvent, Task

load_dotenv(override=True)  # Override shell environment variables with .env file

def get_openai_client():
    """Get OpenAI client, only if API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def generate_burnout_predictions(
    events: List[CalendarEvent],
    tasks: List[Task],
    stress_factors: Dict
) -> List[str]:
    """Generate AI-powered burnout predictions based on calendar and task data"""

    # Prepare context for AI
    now = datetime.now()
    events_summary = f"{len(events)} events scheduled"
    if events:
        event_types = [e.summary for e in events[:10]]  # Sample first 10
        events_summary += f", including: {', '.join(event_types[:5])}"

    tasks_summary = f"{len(tasks)} total tasks"
    overdue = stress_factors.get('overdue_tasks', 0)
    high_priority = stress_factors.get('high_priority_tasks', 0)
    if overdue > 0 or high_priority > 0:
        tasks_summary += f" ({overdue} overdue, {high_priority} high priority)"

    # Build detailed event timeline
    event_details = []
    for event in events[:10]:
        # Calculate days from now
        days_away = (event.start.replace(tzinfo=None) - now).days
        day_label = "Today" if days_away == 0 else f"in {days_away} days"
        event_details.append(f"  • {event.summary} ({day_label}, {event.start.strftime('%a %I:%M%p')})")

    # Build detailed task breakdown
    task_details = []
    for task in tasks[:10]:
        due_str = task.due_date.strftime('%a %b %d') if task.due_date else "No deadline"
        task_details.append(f"  • [{task.priority.upper()}] {task.title} - Due: {due_str}")

    prompt = f"""You are an expert burnout prevention coach analyzing a university student's actual schedule and workload.

DETAILED SCHEDULE ANALYSIS:

📅 Upcoming Events ({len(events)} total):
{chr(10).join(event_details) if event_details else '  • No upcoming events'}

📋 Current Tasks ({len(tasks)} total):
{chr(10).join(task_details) if task_details else '  • No tasks'}

KEY METRICS:
- Events in next 7 days: {stress_factors.get('events_next_7_days', 0)}
- Calendar density today: {stress_factors.get('calendar_density', 0):.1f}% (% of waking hours scheduled)
- Sleep opportunity: {stress_factors.get('sleep_hours_available', 8):.1f} hours
- Overdue tasks: {overdue}
- High priority pending tasks: {high_priority}

TASK: Analyze this ACTUAL schedule and provide 3-5 highly specific, personalized predictions about burnout risks.

Requirements:
1. Reference SPECIFIC events and tasks by name (e.g., "Your CS exam on Wed after back-to-back lectures...")
2. Identify concrete time conflicts or scheduling patterns
3. Point out recovery gaps or lack thereof
4. Notice if workload is front-loaded or back-loaded in the week
5. Highlight specific stress compounding factors (e.g., "exam prep + project deadline on same day")

DO NOT give generic advice. Be specific to THIS student's ACTUAL schedule.

Return JSON: {{"predictions": ["prediction 1", "prediction 2", ...]}}
"""

    client = get_openai_client()
    if not client:
        return generate_fallback_predictions(stress_factors)

    try:
        # Using GPT-5 mini (reasoning model)
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an expert in student mental health and burnout prevention. Provide specific, data-driven insights."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=5000,  # High limit for reasoning model (uses many tokens for internal reasoning before output)
            response_format={"type": "json_object"}
        )

        # GPT-4o-mini backup (kept for fallback)
        # response = client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[
        #         {"role": "system", "content": "You are an expert in student mental health and burnout prevention. Provide specific, data-driven insights."},
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=0.7,
        #     max_tokens=500,
        #     response_format={"type": "json_object"}
        # )

        result = json.loads(response.choices[0].message.content)
        predictions = result.get('predictions', [])

        # Ensure we have valid predictions
        if not predictions or len(predictions) == 0:
            return generate_fallback_predictions(stress_factors)

        return predictions[:5]  # Max 5 predictions

    except Exception as e:
        print(f"AI prediction error: {e}")
        if 'response' in locals():
            print(f"Response object: {response}")
        return generate_fallback_predictions(stress_factors)


def generate_ai_interventions(
    events: List[CalendarEvent],
    tasks: List[Task],
    stress_factors: Dict,
    stress_score: float
) -> List[Dict]:
    """Generate AI-powered personalized interventions"""

    # Build detailed context with timestamps and specifics
    now = datetime.now()
    events_context = []
    for i, event in enumerate(events[:8], 1):
        start_time = event.start.strftime('%a %b %d, %I:%M%p')
        duration = (event.end - event.start).total_seconds() / 3600
        events_context.append(f"{i}. {event.summary} - {start_time} ({duration:.1f}h)")

    tasks_context = []
    for i, task in enumerate(tasks[:8], 1):
        if task.due_date:
            days_until = (task.due_date - now).days
            due_str = f"DUE IN {days_until}d" if days_until > 0 else f"OVERDUE by {abs(days_until)}d"
        else:
            due_str = "No deadline"
        priority = task.priority.upper() if task.priority else "NORMAL"
        tasks_context.append(f"{i}. [{priority}] {task.title} - {due_str}")

    risk_label = 'CRITICAL' if stress_score > 80 else 'HIGH' if stress_score > 60 else 'MEDIUM' if stress_score > 40 else 'LOW'

    events_text = chr(10).join(events_context) if events_context else "No upcoming events"
    tasks_text = chr(10).join(tasks_context) if tasks_context else "No tasks"
    sleep_hrs = stress_factors.get('sleep_hours_available', 8)
    cal_density = stress_factors.get('calendar_density', 0)

    stress_info = f"{stress_score:.1f}/100 (Risk: {risk_label})"
    sleep_info = f"{sleep_hrs:.1f}"
    density_info = f"{cal_density:.1f}"
    overdue_count = stress_factors.get('overdue_tasks', 0)
    high_pri_count = stress_factors.get('high_priority_tasks', 0)

    prompt = (
        "You are an expert burnout prevention coach for university students.\n\n"
        f"STRESS LEVEL - {stress_info}\n\n"
        "UPCOMING EVENTS:\n"
        f"{events_text}\n\n"
        "TASKS:\n"
        f"{tasks_text}\n\n"
        "METRICS:\n"
        f"- Overdue tasks {overdue_count}\n"
        f"- High priority {high_pri_count}\n"
        f"- Sleep hours {sleep_info}\n"
        f"- Calendar density {density_info}%\n\n"
        "Generate 3-5 SPECIFIC interventions for THIS student. Reference actual event/task names.\n\n"
        "IMPORTANT: Return ONLY valid JSON with this EXACT structure:\n\n"
        '{"interventions": [\n'
        '  {\n'
        '    "id": "int-1",\n'
        '    "type": "reschedule",\n'
        '    "priority": "high",\n'
        '    "title": "Short title here",\n'
        '    "description": "Detailed description here",\n'
        '    "impact_score": 85,\n'
        '    "effort_score": 40\n'
        '  }\n'
        ']}\n\n'
        "Each intervention MUST include ALL fields:\n"
        "- id: string (int-1, int-2, etc)\n"
        "- type: REQUIRED string - MUST be one of: reschedule, delegate, break_down, micro_break\n"
        "- priority: string (low/medium/high/critical)\n"
        "- title: string (brief)\n"
        "- description: string (specific to this student's schedule)\n"
        "- impact_score: number 0-100\n"
        "- effort_score: number 0-100"
    )

    client = get_openai_client()
    if not client:
        return generate_fallback_interventions(stress_factors)

    try:
        # GPT-5 mini (reasoning model) - temperature not supported
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an expert student wellness advisor specializing in burnout prevention and stress management."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=8000,  # High limit for reasoning model (uses many tokens for internal reasoning before output)
            response_format={"type": "json_object"}
        )

        # Backup: GPT-4o-mini (if GPT-5 fails)
        # response = client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[
        #         {"role": "system", "content": "You are an expert student wellness advisor specializing in burnout prevention and stress management."},
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=0.7,
        #     max_tokens=800,
        #     response_format={"type": "json_object"}
        # )

        result = json.loads(response.choices[0].message.content)
        interventions = result.get('interventions', [])

        # Validate and return
        if not interventions or len(interventions) == 0:
            return generate_fallback_interventions(stress_factors)

        return interventions[:5]  # Max 5 interventions

    except Exception as e:
        print(f"AI intervention error: {e}")
        return generate_fallback_interventions(stress_factors)


def generate_fallback_predictions(stress_factors: Dict) -> List[str]:
    """Fallback predictions if AI fails"""
    predictions = []

    if stress_factors.get('overdue_tasks', 0) > 3:
        predictions.append("High number of overdue tasks may indicate difficulty with time management or task prioritization")

    if stress_factors.get('calendar_density', 0) > 70:
        predictions.append("Calendar density above 70% suggests limited time for breaks and recovery")

    if stress_factors.get('sleep_hours_available', 8) < 6:
        predictions.append("Sleep deficit detected - less than 6 hours available may impact cognitive performance")

    if stress_factors.get('events_next_7_days', 0) > 20:
        predictions.append("Heavy event load in upcoming week may lead to meeting fatigue")

    if not predictions:
        predictions.append("Current workload appears manageable with proper time management")

    return predictions


def generate_fallback_interventions(stress_factors: Dict) -> List[Dict]:
    """Fallback interventions if AI fails"""
    interventions = []

    if stress_factors.get('overdue_tasks', 0) > 0:
        interventions.append({
            "id": "1",
            "title": "Address overdue tasks immediately",
            "description": "Focus on completing or rescheduling overdue items to reduce mental burden",
            "priority": "critical",
            "impact_score": 80,
            "effort_score": 60
        })

    if stress_factors.get('sleep_hours_available', 8) < 7:
        interventions.append({
            "id": "2",
            "title": "Block sleep protection time",
            "description": "Schedule 7-8 hour sleep blocks in your calendar to ensure adequate rest",
            "priority": "high",
            "impact_score": 85,
            "effort_score": 30
        })

    if stress_factors.get('calendar_density', 0) > 60:
        interventions.append({
            "id": "3",
            "title": "Add recovery breaks between meetings",
            "description": "Schedule 10-15 minute breaks between back-to-back events",
            "priority": "medium",
            "impact_score": 65,
            "effort_score": 40
        })

    return interventions
