# Burnout Prevention Agent - Backend

FastAPI backend for AI-powered burnout detection and prevention system.

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

5. Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Stress Analysis
- `POST /api/stress/analyze` - Analyze stress levels from calendar and tasks

### Calendar
- `GET /api/calendar/events` - Get calendar events
- `POST /api/calendar/events` - Create event
- `GET /api/calendar/sync` - Sync with Google Calendar

### Tasks
- `GET /api/tasks/` - Get all tasks
- `POST /api/tasks/` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

## Architecture

```
backend/
├── main.py                 # FastAPI app entry point
├── models/
│   └── schemas.py         # Pydantic models
├── routers/
│   ├── stress.py          # Stress analysis endpoints
│   ├── calendar.py        # Calendar endpoints
│   └── tasks.py           # Task endpoints
└── utils/
    ├── stress_calculator.py    # Stress scoring logic
    └── intervention_engine.py  # Intervention generation
```

## Features

- Real-time stress scoring based on calendar density, task load, and sleep opportunity
- Multi-factor analysis (calendar, tasks, sleep)
- Intelligent intervention suggestions
- Risk level categorization (low/medium/high/critical)
- Mock data for MVP (ready for API integration)
