from datetime import datetime, timedelta
from schemas import CalendarEvent, Task
import requests

# Create mock data
mock_events = [
    CalendarEvent(
        id="1",
        summary="MATH 32A Lecture",
        start=datetime.now() + timedelta(hours=2),
        end=datetime.now() + timedelta(hours=3),
        description="Linear Algebra"
    ),
    CalendarEvent(
        id="2",
        summary="CHEM 20A Lab",
        start=datetime.now() + timedelta(hours=4),
        end=datetime.now() + timedelta(hours=6),
        description="Chemistry Lab"
    ),
    CalendarEvent(
        id="3",
        summary="ENGCOMP 3",
        start=datetime.now() + timedelta(days=1, hours=1),
        end=datetime.now() + timedelta(days=1, hours=2),
    ),
]

mock_tasks = [
    Task(
        id="1",
        title="MATH 32A Homework",
        due_date=datetime.now() + timedelta(days=2),
        priority="high",
        completed=False
    ),
    Task(
        id="2",
        title="CHEM Quiz Prep",
        due_date=datetime.now() + timedelta(days=1),
        priority="high",
        completed=False
    ),
    Task(
        id="3",
        title="Read Chapter 5",
        due_date=datetime.now() + timedelta(days=3),
        priority="medium",
        completed=False
    ),
]

if __name__ == "__main__":
    # Convert to dict for JSON with mode='json' to serialize datetime properly
    events_json = [e.model_dump(mode='json') for e in mock_events]
    tasks_json = [t.model_dump(mode='json') for t in mock_tasks]

    print("=" * 60)
    print("Testing Burnout Prevention API")
    print("=" * 60)
    print(f"Events: {len(events_json)}")
    print(f"Tasks: {len(tasks_json)}")
    print()

    try:
        print("Sending request to API...")
        response = requests.post(
            "http://localhost:8001/api/stress/analyze",
            json={
                "events": events_json,
                "tasks": tasks_json
            }
        )

        print(f"Status Code: {response.status_code}\n")

        if response.status_code == 200:
            data = response.json()

            print("✅ SUCCESS!\n")
            print("=" * 60)
            print("STRESS ANALYSIS")
            print("=" * 60)
            print(f"Overall Score: {data['stress_score']['total_score']}/100")
            print(f"Risk Level: {data['stress_score']['risk_level'].upper()}")
            print(f"Calendar Factor: {data['stress_score']['calendar_factor']}")
            print(f"Task Factor: {data['stress_score']['task_factor']}")
            print(f"Sleep Factor: {data['stress_score']['sleep_factor']}")

            print("\n" + "=" * 60)
            print("BURNOUT PREDICTIONS")
            print("=" * 60)
            for i, pred in enumerate(data['predictions'], 1):
                print(f"{i}. {pred}\n")

            print("=" * 60)
            print("RECOMMENDED INTERVENTIONS")
            print("=" * 60)
            for i, interv in enumerate(data['interventions'], 1):
                print(f"{i}. {interv['title']}")
                print(f"   Type: {interv['type']}")
                print(f"   Priority: {interv['priority']}")
                print(f"   Impact: {interv['impact_score']}/100")
                print(f"   Effort: {interv['effort_score']}/100")
                print(f"   {interv['description']}\n")

        else:
            print(f"❌ ERROR: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server!")
        print("\nPlease start the server first:")
        print("  uvicorn main:app --reload --port 8001")

    except Exception as e:
        print(f"❌ ERROR: {e}")