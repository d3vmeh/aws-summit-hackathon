"""
API Test Script for Burnout Prevention Agent (AWS Bedrock / Claude Sonnet 4.5)
Test the stress analysis endpoint with mock calendar events and tasks
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
BASE_URL = "http://localhost:8090"
ANALYZE_ENDPOINT = f"{BASE_URL}/api/stress/analyze"

def create_mock_calendar_events():
    """Create realistic mock calendar events for testing"""
    now = datetime.now()

    events = [
        # Today - Back-to-back classes
        {
            "id": "event-1",
            "summary": "Computer Science Lecture",
            "start": (now.replace(hour=9, minute=0, second=0, microsecond=0)).isoformat(),
            "end": (now.replace(hour=10, minute=30, second=0, microsecond=0)).isoformat(),
            "description": "Data Structures and Algorithms"
        },
        {
            "id": "event-2",
            "summary": "Mathematics Tutorial",
            "start": (now.replace(hour=11, minute=0, second=0, microsecond=0)).isoformat(),
            "end": (now.replace(hour=12, minute=0, second=0, microsecond=0)).isoformat(),
            "description": "Linear Algebra"
        },
        {
            "id": "event-3",
            "summary": "Project Team Meeting",
            "start": (now.replace(hour=14, minute=0, second=0, microsecond=0)).isoformat(),
            "end": (now.replace(hour=15, minute=30, second=0, microsecond=0)).isoformat(),
            "description": "Final year project discussion"
        },
        # Tomorrow - Heavy workload
        {
            "id": "event-4",
            "summary": "Physics Lab",
            "start": (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0).isoformat(),
            "end": (now + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0).isoformat(),
            "description": "Quantum Mechanics Lab Session"
        },
        {
            "id": "event-5",
            "summary": "Machine Learning Lecture",
            "start": (now + timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0).isoformat(),
            "end": (now + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0).isoformat(),
            "description": "Deep Learning Neural Networks"
        },
        {
            "id": "event-6",
            "summary": "Study Group Session",
            "start": (now + timedelta(days=1)).replace(hour=16, minute=0, second=0, microsecond=0).isoformat(),
            "end": (now + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0).isoformat(),
            "description": "Exam preparation"
        },
        # Day after tomorrow - Exam stress
        {
            "id": "event-7",
            "summary": "Midterm Exam - Data Structures",
            "start": (now + timedelta(days=2)).replace(hour=9, minute=0, second=0, microsecond=0).isoformat(),
            "end": (now + timedelta(days=2)).replace(hour=12, minute=0, second=0, microsecond=0).isoformat(),
            "description": "Comprehensive exam covering all topics"
        },
        # Later in the week - More commitments
        {
            "id": "event-8",
            "summary": "Coffee with Study Buddy",
            "start": (now + timedelta(days=3)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
            "end": (now + timedelta(days=3)).replace(hour=11, minute=0, second=0, microsecond=0).isoformat(),
            "description": "Informal catch-up"
        },
        {
            "id": "event-9",
            "summary": "Club Meeting - Tech Society",
            "start": (now + timedelta(days=4)).replace(hour=17, minute=0, second=0, microsecond=0).isoformat(),
            "end": (now + timedelta(days=4)).replace(hour=18, minute=30, second=0, microsecond=0).isoformat(),
            "description": "Monthly tech society meetup"
        },
        {
            "id": "event-10",
            "summary": "Assignment Workshop",
            "start": (now + timedelta(days=5)).replace(hour=14, minute=0, second=0, microsecond=0).isoformat(),
            "end": (now + timedelta(days=5)).replace(hour=16, minute=0, second=0, microsecond=0).isoformat(),
            "description": "Programming assignment help session"
        }
    ]

    return events

def create_mock_tasks():
    """Create realistic mock tasks for testing"""
    now = datetime.now()

    tasks = [
        # Overdue task - high stress
        {
            "id": "task-1",
            "title": "Submit Database Assignment",
            "description": "Complete SQL queries and ER diagrams",
            "due_date": (now - timedelta(days=2)).isoformat(),
            "priority": "high",
            "completed": False
        },
        # Due soon - high priority
        {
            "id": "task-2",
            "title": "Prepare for Data Structures Exam",
            "description": "Review all lecture notes and practice problems",
            "due_date": (now + timedelta(days=2)).isoformat(),
            "priority": "high",
            "completed": False
        },
        # Medium priority
        {
            "id": "task-3",
            "title": "Complete Chapter 5 Reading",
            "description": "Machine Learning textbook",
            "due_date": (now + timedelta(days=5)).isoformat(),
            "priority": "medium",
            "completed": False
        },
        # High priority - project
        {
            "id": "task-4",
            "title": "Finish Project Prototype",
            "description": "Build working demo for team meeting",
            "due_date": (now + timedelta(days=1)).isoformat(),
            "priority": "high",
            "completed": False
        },
        # Low priority
        {
            "id": "task-5",
            "title": "Update LinkedIn Profile",
            "description": "Add recent projects and skills",
            "due_date": (now + timedelta(days=10)).isoformat(),
            "priority": "low",
            "completed": False
        },
        # Another overdue - creating more stress
        {
            "id": "task-6",
            "title": "Submit Lab Report",
            "description": "Physics lab experiment writeup",
            "due_date": (now - timedelta(days=1)).isoformat(),
            "priority": "medium",
            "completed": False
        }
    ]

    return tasks

def test_stress_analysis():
    """Test the stress analysis endpoint"""
    print("=" * 80)
    print("BURNOUT PREVENTION AGENT - API TEST (Claude Sonnet 4.5 via AWS Bedrock)")
    print("=" * 80)
    print()

    # Create mock data
    events = create_mock_calendar_events()
    tasks = create_mock_tasks()

    print(f"📅 Created {len(events)} calendar events")
    print(f"📋 Created {len(tasks)} tasks")
    print()

    # Prepare request payload
    payload = {
        "events": events,
        "tasks": tasks
    }

    print(f"🔍 Sending request to: {ANALYZE_ENDPOINT}")
    print("⏳ Please wait - Claude Sonnet 4.5 is analyzing your schedule...")
    print()

    try:
        # Make API request
        response = requests.post(ANALYZE_ENDPOINT, json=payload, timeout=60)
        response.raise_for_status()

        # Parse response
        result = response.json()

        # Display results
        print("✅ API REQUEST SUCCESSFUL")
        print("=" * 80)
        print()

        # Stress Score
        stress_score = result['stress_score']
        print("📊 STRESS SCORE ANALYSIS")
        print("-" * 80)
        print(f"Total Score:      {stress_score['total_score']:.2f}/100")
        print(f"Risk Level:       {stress_score['risk_level'].upper()}")
        print(f"Calendar Factor:  {stress_score['calendar_factor']:.2f}/100")
        print(f"Task Factor:      {stress_score['task_factor']:.2f}/100")
        print(f"Sleep Factor:     {stress_score['sleep_factor']:.2f}/100")
        print()

        # Factors
        factors = result['factors']
        print("📈 STRESS FACTORS")
        print("-" * 80)
        print(f"Events (next 7 days):  {factors['events_next_7_days']}")
        print(f"Calendar Density:      {factors['calendar_density']:.1f}%")
        print(f"Sleep Hours Available: {factors['sleep_hours_available']:.1f} hours")
        print(f"Overdue Tasks:         {factors['overdue_tasks']}")
        print(f"High Priority Tasks:   {factors['high_priority_tasks']}")
        print()

        # Predictions (AI-generated by Claude)
        print("🔮 BURNOUT PREDICTIONS (Generated by Claude Sonnet 4.5)")
        print("-" * 80)
        for i, prediction in enumerate(result['predictions'], 1):
            print(f"{i}. {prediction}")
        print()

        # Interventions (AI-generated by Claude)
        print("💡 RECOMMENDED INTERVENTIONS (Generated by Claude Sonnet 4.5)")
        print("-" * 80)
        for i, intervention in enumerate(result['interventions'], 1):
            print(f"\n{i}. [{intervention['priority'].upper()}] {intervention['title']}")
            print(f"   Type: {intervention['type']}")
            print(f"   {intervention['description']}")
            print(f"   Impact: {intervention['impact_score']:.0f}/100 | Effort: {intervention['effort_score']:.0f}/100")
        print()

        # Historical comparison (if available)
        if result.get('historical_comparison'):
            print("📊 HISTORICAL COMPARISON")
            print("-" * 80)
            print(result['historical_comparison'])
            print()

        print("=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)

        # Save full response to file
        with open('test_response_claude.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\n💾 Full response saved to: test_response_claude.json")

    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Could not connect to {BASE_URL}")
        print("   Make sure the backend server is running on port 8090")
        print("   Run: uvicorn main:app --reload --port 8090")

    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT: Request took too long (>60 seconds)")
        print("   Claude Sonnet 4.5 via Bedrock might be slow or AWS credentials might be missing")
        print("   Check your .env file for AWS credentials")

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP ERROR: {e}")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:500]}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_health_check():
    """Test the health endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health Check: {response.json()}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")

def test_root():
    """Test the root endpoint"""
    print("🌐 Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root: {data.get('message')} - Status: {data.get('status')}")
        else:
            print(f"❌ Root Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root Error: {e}")

if __name__ == "__main__":
    # Run health checks first
    test_health_check()
    test_root()
    print()

    # Run main stress analysis test
    test_stress_analysis()
