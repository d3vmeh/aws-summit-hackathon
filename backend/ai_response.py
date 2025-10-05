import os
import json
import re
import time
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from schemas import CalendarEvent, Task, StressFactors, Intervention
from typing import List, Dict

load_dotenv(override=True)

def get_client():
      print("Loading AWS credentials...")
      print(f"Region: {os.getenv('AWS_DEFAULT_REGION', 'us-west-2')}")
      print(f"Access Key exists: {os.getenv('AWS_ACCESS_KEY_ID') is not None}")

      client = boto3.client(
          'bedrock-runtime',
          region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2'),
          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
      )
      print("Client created successfully")
      return client

def invoke_model_with_retry(client, model_id: str, request_body: str, max_retries: int = 3):
    """Invoke Bedrock model with exponential backoff retry for throttling"""
    for attempt in range(max_retries):
        try:
            response = client.invoke_model(modelId=model_id, body=request_body)
            return json.loads(response.get('body').read())
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                    print(f"Throttled by AWS Bedrock. Waiting {wait_time}s before retry (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached for throttling.")
                    raise
            else:
                raise
    return None

def _to_naive(dt: datetime) -> datetime:
    """Convert datetime to timezone-naive"""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

def generate_burnout_predictions(events: List[CalendarEvent],
                                tasks: List[Task],
                                stress_factors: StressFactors) -> List[str]:

    client = get_client()

    event_details = []
    now = _to_naive(datetime.now())
    for event in events[:10]:
        event_start = _to_naive(event.start)
        days_away = (event_start - now).days
        day_label = "Today" if days_away == 0 else f"in {days_away} days"
        event_details.append(
            f"  • {event.summary} ({day_label}, {event_start.strftime('%a %I:%M%p')})"
        )

    task_details = []
    for task in tasks[:10]:
        due_str = task.due_date.strftime('%a %b %d') if task.due_date else "No deadline"
        task_details.append(
            f"  • [{task.priority.upper()}] {task.title} - Due: {due_str}"
        )

    prompt = f"""You are an expert in student and career counseling, mental health, and burnout prevention. You analyze a 
student's schedule and personalize burnout prevention recommendations to them.

DETAILED SCHEDULE ANALYSIS:

📅 UPCOMING EVENTS ({len(events)} total):
{chr(10).join(event_details) if event_details else '  • No upcoming events'}

📋 CURRENT TASKS ({len(tasks)} total):
{chr(10).join(task_details) if task_details else '  • No tasks'}

KEY METRICS:
- Events in next 7 days: {stress_factors.events_next_7_days}
- Calendar density today: {stress_factors.calendar_density:.1f}% (% of waking hours scheduled)
- Sleep opportunity: {stress_factors.sleep_hours_available:.1f} hours
- Overdue tasks: {stress_factors.overdue_tasks}
- High priority pending tasks: {stress_factors.high_priority_tasks}

YOUR TASK: Analyze this ACTUAL student's schedule and provide 3 highly specific, personalized predictions to help them avoid 
burnout.

Requirements:
1. Reference SPECIFIC events and tasks by name (e.g., "Your MATH 32A lecture after back-to-back meetings...")
2. Identify concrete time conflicts or scheduling patterns
3. Point out recovery gaps or lack thereof
4. Notice if workload is front-loaded or back-loaded in the week
5. Highlight specific stress compounding factors (e.g., "exam prep + project deadline on same day")

DO NOT give generic advice. Be specific to THIS student's ACTUAL schedule shown above.

Response Format:
Return JSON: {{"predictions": ["prediction 1", "prediction 2", "prediction 3"]}}
"""

    model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    model_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    request = json.dumps(model_request)

    try:
        response_body = invoke_model_with_retry(client, model_id, request)
        text_response = response_body['content'][0]['text']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ThrottlingException':
            return ["Rate limit reached. Please wait a moment and refresh."]
        raise

    # Parse JSON response to dictionary
    try:
        # Try direct parsing first
        predictions_dict = json.loads(text_response)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text_response, re.DOTALL)
        if json_match:
            predictions_dict = json.loads(json_match.group(1))
        else:
            # Try to find any JSON object in the response
            json_match = re.search(r'\{.*?\}', text_response, re.DOTALL)
            if json_match:
                predictions_dict = json.loads(json_match.group(0))
            else:
                # Fallback
                predictions_dict = {"predictions": ["Unable to generate predictions at this time."]}

    return predictions_dict.get('predictions', [])


def generate_ai_interventions(events: List[CalendarEvent],
                            tasks: List[Task],
                            stress_factors: StressFactors,
                            stress_score: float) -> List[Dict]:

    client = get_client()

    # Build event context
    events_context = []
    now = _to_naive(datetime.now())
    for i, event in enumerate(events[:8], 1):
        event_start = _to_naive(event.start)
        event_end = _to_naive(event.end)
        start_time = event_start.strftime('%a %b %d, %I:%M%p')
        duration = (event_end - event_start).total_seconds() / 3600
        events_context.append(f"{i}. {event.summary} - {start_time} ({duration:.1f}h)")

    # Build task context
    tasks_context = []
    for i, task in enumerate(tasks[:8], 1):
        if task.due_date:
            task_due = _to_naive(task.due_date)
            days_until = (task_due - now).days
            due_str = f"DUE IN {days_until}d" if days_until > 0 else f"OVERDUE by {abs(days_until)}d"
        else:
            due_str = "No deadline"
        priority = task.priority.upper() if task.priority else "NORMAL"
        tasks_context.append(f"{i}. [{priority}] {task.title} - {due_str}")

    # Determine risk level
    risk_label = 'CRITICAL' if stress_score > 80 else 'HIGH' if stress_score > 60 else 'MEDIUM' if stress_score > 40 else 'LOW'

    events_text = chr(10).join(events_context) if events_context else "No upcoming events"
    tasks_text = chr(10).join(tasks_context) if tasks_context else "No tasks"

    prompt = f"""You are an expert counselor in burnout prevention for university students.

STRESS LEVEL: {stress_score:.1f}/100 (Risk: {risk_label})

UPCOMING EVENTS:
{events_text}

TASKS:
{tasks_text}

METRICS:
- Overdue tasks: {stress_factors.overdue_tasks}
- High priority: {stress_factors.high_priority_tasks}
- Sleep hours: {stress_factors.sleep_hours_available:.1f}
- Calendar density: {stress_factors.calendar_density:.1f}%

YOUR TASK: Generate 3-5 SPECIFIC interventions to help this student avoid burnout. Reference actual event/task names.

Response format:
Return ONLY valid JSON with this EXACT structure:

{{"interventions": [
{{
    "id": "int-1",
    "type": "reschedule",
    "priority": "high",
    "title": "Short title here",
    "description": "Detailed description here",
    "impact_score": 85,
    "effort_score": 40
}}
]}}

Each intervention MUST include ALL fields:
- id: string (int-1, int-2, etc)
- type: REQUIRED string - MUST be one of: reschedule, delegate, break_down, micro_break
- priority: string (low/medium/high/critical)
- title: string (brief)
- description: string (specific to this student's schedule)
- impact_score: number 0-100
- effort_score: number 0-100
"""

    model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    model_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    request = json.dumps(model_request)

    try:
        response_body = invoke_model_with_retry(client, model_id, request)
        text_response = response_body['content'][0]['text']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ThrottlingException':
            return []  # Return empty interventions list on rate limit
        raise

    # Parse JSON response to dictionary
    try:
        # Try direct parsing first
        interventions_dict = json.loads(text_response)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text_response, re.DOTALL)
        if json_match:
            interventions_dict = json.loads(json_match.group(1))
        else:
            # Try to find any JSON object in the response
            json_match = re.search(r'\{.*?\}', text_response, re.DOTALL)
            if json_match:
                interventions_dict = json.loads(json_match.group(0))
            else:
                # Fallback: return empty interventions
                interventions_dict = {"interventions": []}

    return interventions_dict.get('interventions', [])