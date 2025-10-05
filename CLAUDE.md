# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Burnout Prevention Agent** - AI-powered burnout detection and prevention system for university students. The system analyzes calendar events, task loads, and sleep patterns to calculate real-time stress scores and provide actionable interventions.

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.12) with Pydantic for data validation
- **Frontend**: Mentioned in docs but not present in current directory (Next.js/React/TypeScript)
- **AI Integration**: OpenAI GPT-5-mini for predictions and interventions (with rule-based fallback)
- **APIs**: Google Calendar OAuth 2.0, planned GitHub and Notion/Todoist integrations

### Backend Structure (`/backend`)

```
backend/
├── main.py                        # FastAPI app entry point, CORS config, router registration
├── models/schemas.py              # Pydantic models: CalendarEvent, Task, StressScore, BurnoutPrediction
├── routers/
│   ├── auth.py                    # Google OAuth flow, token management (in-memory + file)
│   ├── stress.py                  # POST /api/stress/analyze - main analysis endpoint
│   ├── calendar.py                # Calendar CRUD, auto-switches between Google/mock data
│   └── tasks.py                   # Task CRUD operations
└── utils/
    ├── stress_calculator.py       # Core stress scoring algorithm
    ├── intervention_engine.py     # Rule-based intervention generation
    ├── ai_insights.py             # OpenAI integration for predictions/interventions
    ├── google_calendar.py         # Google Calendar API wrapper
    └── descope_utils.py           # Auth utilities
```

## Key Algorithms

### Stress Calculation (utils/stress_calculator.py)

**Total Stress Score = (Calendar Factor × 0.4) + (Task Factor × 0.3) + (Sleep Factor × 0.3)**

- **Calendar Factor**: Based on calendar density (% of waking hours scheduled) + event count
- **Task Factor**: Overdue tasks × 10 + High priority tasks × 5
- **Sleep Factor**: Inverse of available sleep hours (8 hours = 0 stress)
- **Risk Levels**: Low (0-40), Medium (41-60), High (61-80), Critical (81-100)

The `parse_datetime()` helper handles timezone-naive datetime conversions - always use this when working with event/task dates.

### Intervention Engine (utils/intervention_engine.py)

Generates specific, actionable interventions by:
1. Analyzing stress factors and referencing specific tasks/events by name
2. Identifying reschedulable events (social keywords: "coffee", "chat", "optional", "lunch")
3. Calculating impact/effort ratios and sorting by ROI
4. Returning top 5 interventions

Intervention types: `reschedule`, `delegate`, `break_down`, `micro_break`

### AI Insights (utils/ai_insights.py)

- Uses **OpenAI GPT-5-mini** (reasoning model) with `max_completion_tokens` (not `max_tokens`)
- Requires `OPENAI_API_KEY` in .env, gracefully falls back to rule-based if unavailable
- Generates context-aware predictions referencing specific calendar events and tasks
- Always includes fallback functions for when AI calls fail

## Development Commands

### Backend Setup & Running

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000

# API Documentation (auto-generated)
# http://localhost:8000/docs (Swagger)
# http://localhost:8000/redoc (ReDoc)
```

### Testing

```bash
# Run test file (if present)
python test_api.py

# Manual API testing
curl http://localhost:8000/health
curl http://localhost:8000/auth/status
curl http://localhost:8000/api/calendar/events
```

## Google Calendar OAuth Integration

The app supports real Google Calendar data via OAuth 2.0:

1. **Setup**: Follow `backend/GOOGLE_OAUTH_SETUP.md` to create Google Cloud project and credentials
2. **Files**: Place `credentials.json` in `/backend` (gitignored)
3. **Flow**: `/auth/google` → User consent → `/auth/callback` → Tokens stored in `token.json`
4. **Token Management**: In-memory storage + file persistence for MVP, needs database for production
5. **Auto-switching**: Calendar router automatically uses Google data when authenticated, falls back to mock data otherwise

### Important OAuth Notes
- Single-user mode using `user_id = "demo_user"` (MVP limitation)
- Tokens stored in plaintext `token.json` - NOT production-ready
- Redirect URI MUST match: `http://localhost:8000/auth/google/callback`
- Requires scope: `https://www.googleapis.com/auth/calendar.readonly`

## Environment Variables

### Backend `.env` (see `.env.example`)
```bash
# Google Calendar API (required for OAuth)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# OpenAI API (optional - enables AI predictions)
OPENAI_API_KEY=...

# Application Settings
DEBUG=True
API_PORT=8000
```

## Critical API Endpoints

### Stress Analysis
- `POST /api/stress/analyze` - Main endpoint accepting `{events: CalendarEvent[], tasks: Task[]}`, returns `BurnoutPrediction` with stress score, factors, AI predictions, and interventions

### Auth Flow
- `GET /auth/google` - Returns auth URL for OAuth flow
- `GET /auth/callback?code=...` - Handles OAuth callback, stores tokens
- `GET /auth/status` - Check authentication status
- `POST /auth/logout` - Clear tokens

### Calendar
- `GET /api/calendar/events` - Returns Google Calendar events if authenticated, else mock data
- `GET /api/calendar/sync` - Trigger manual calendar sync
- `GET /api/calendar/info` - Get calendar metadata

## Code Patterns

### Adding New Stress Factors

1. Update `StressFactors` model in `models/schemas.py`
2. Add calculation logic in `StressCalculator.get_stress_factors()`
3. Integrate into total score in `StressCalculator.calculate_stress_score()`
4. Update AI prompt context in `ai_insights.py` to include new factor

### Working with Datetime

Always use `parse_datetime()` from `utils/stress_calculator.py` - handles both string ISO format and datetime objects, strips timezone info for consistency. The codebase works with timezone-naive datetimes.

### AI Integration Pattern

```python
# Check if API key exists
use_ai = os.getenv('OPENAI_API_KEY') is not None

if use_ai:
    try:
        result = generate_ai_predictions(...)
    except Exception:
        result = generate_fallback_predictions(...)
else:
    result = generate_fallback_predictions(...)
```

Always provide fallback functions that don't require external APIs.

## Current Limitations (MVP)

- No database persistence - uses in-memory storage and files
- Single-user mode (`demo_user` hardcoded)
- Tokens stored in plaintext
- No background jobs/syncing
- No historical pattern analysis (placeholder only)
- Frontend not included in this directory
- No GitHub or Notion integration yet (mentioned in roadmap)

## Production Readiness Checklist

Based on `guides/IMPLEMENTATION_ROADMAP.md`:
- [ ] Replace in-memory storage with PostgreSQL
- [ ] Encrypt tokens before storage
- [ ] Implement proper multi-user authentication
- [ ] Add Celery + Redis for background calendar syncing
- [ ] Implement WebSocket for real-time updates
- [ ] Add GitHub OAuth and commit pattern tracking
- [ ] Add Notion/Todoist task integration
- [ ] Implement ML-based burnout prediction (sklearn/TensorFlow)
- [ ] Add notification system (Twilio SMS, email, push)
- [ ] Deploy with Docker Compose

## Important Files to Check

- `guides/START_APP.md` - How to run the application
- `guides/PHASE1_COMPLETE.md` - Google OAuth implementation details
- `guides/IMPLEMENTATION_ROADMAP.md` - Future architecture plans
- `backend/GOOGLE_OAUTH_SETUP.md` - OAuth setup instructions

## Git Practices

- **Never commit**: `.env`, `credentials.json`, `token.json` (enforced via `.gitignore`)
- Recent commits show work on OAuth integration and file reorganization
- Main branch: `main`
