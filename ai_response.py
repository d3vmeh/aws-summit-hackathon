import os
import json
from dotenv import load_dotenv
import os
import boto3



load_dotenv(override=True)

def generate_burnout_predictions():

    client = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )


    prompt = f"""

    You are an expert in student and career counseling, mental health, and burnout prevention. You analyze a student's schedule and persoalize burnout prevention recommendations to them.


    DETAILED SCHEDULE ANALYSIS:
    Sunday

    Bruin Entrepreneurs App — 9–10 pm

    CHEM 20A Problem Set — 10–11 pm

    Monday

    MATH 32A (Bunche Hall 1209B) — 10:00 am

    CHEM 20A (Moore Hall 100) — 11:00 am

    ENGCOMP 3 Homework — (time not clearly specified on the calendar tile)

    ENGCOMP 3 — 12:30–1:45 pm

    ECE Seminar (Kinsey …) — 5:00–5:50 pm

    [Claude Builder Club] 1s (Engineering V, Los Angeles) — 6:00 pm (block looks ~1 hr)

    Bruin Baja GM — 8–9 pm

    MATH 32A Homework Due — 9–10 pm

    CHEM 20A Quiz Due — 10–11 pm

    KEY METRICS:
    - Stress Score: 43.7%
    - Events in next 7 days: 12
    - Calendar density today: 66.7% (% of waking hours scheduled)
    - Sleep opportunity: 6.5 hours
    - Overdue tasks: 0
    - High priority pending tasks: 1

    YOUR TASK: Analyze this student's schedule and provide 3 highly specific, personalized recommendations to help them avoid burnout.

    Requirements:

    Requirements:
    1. Reference SPECIFIC events and tasks by name (e.g., "Your CS exam on Wed after back-to-back lectures...")
    2. Identify concrete time conflicts or scheduling patterns
    3. Point out recovery gaps or lack thereof
    4. Notice if workload is front-loaded or back-loaded in the week
    5. Highlight specific stress compounding factors (e.g., "exam prep + project deadline on same day")

    DO NOT give generic advice. Be specific to this student's actual schedule.

    Response Format:

    Return JSON: {{"predictions": ["prediction 1", "prediction 2", ...]}}


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


    response = client.invoke_model(modelId=model_id, body=request)

    response_body = json.loads(response.get('body').read())

    text_response = response_body['content'][0]['text']

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
                # Fallback: return the raw text
                predictions_dict = {"predictions": [text_response]}
    return predictions_dict
