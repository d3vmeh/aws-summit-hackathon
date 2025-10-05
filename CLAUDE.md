# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Burnout Prevention Agent** - AI-powered burnout detection and prevention system for university students. The system analyzes calendar events, task loads, and sleep patterns to calculate real-time stress scores and provide actionable interventions.

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.12) with Pydantic for data validation
- **Frontend**: Next.js 15.5.4 with React 19, TypeScript, Tailwind CSS 4, Turbopack
- **AI Integration**: Claude Sonnet 4.5 via AWS Bedrock with exponential backoff retry logic
- **APIs**: Google Calendar OAuth 2.0 with multi-calendar selection support

### Backend Structure (`/backend`)

```
backend/
├── main.py                        # FastAPI app entry point, CORS, calendar selection endpoints
├── schemas.py                     # Pydantic models: CalendarEvent, Task, StressScore, BurnoutPrediction
├── stress_calculator.py           # Core stress scoring algorithm with timezone handling
├── ai_response.py                 # AWS Bedrock Claude Sonnet 4.5 integration with retry logic
├── google_calendar.py             # Google Calendar OAuth + multi-calendar selection
├── token.json                     # OAuth tokens (gitignored)
├── credentials.json               # Google OAuth credentials (gitignored)
├── .env                           # Environment variables (gitignored)
└── requirements.txt               # Python dependencies
```

### Frontend Structure (`/frontend`)

```
frontend/
├── app/
│   ├── page.tsx                   # Main page with StressDashboard
│   └── layout.tsx                 # Root layout
├── components/
│   ├── stress-dashboard.tsx       # Main dashboard with calendar selection UI
│   └── ui/                        # shadcn/ui components (Card, Progress, Badge)
├── lib/
│   ├── api.ts                     # Backend API client
│   ├── types.ts                   # TypeScript type definitions
│   └── mock-data.ts               # Mock events/tasks for testing
├── .env.local                     # Frontend env vars (NEXT_PUBLIC_API_URL)
└── package.json                   # npm dependencies
```

## Key Algorithms

### Stress Calculation (stress_calculator.py)

**Total Stress Score = (Calendar Factor × 0.4) + (Task Factor × 0.3) + (Sleep Factor × 0.3)**

- **Calendar Factor**: Based on calendar density (% of waking hours scheduled) + event count
- **Task Factor**: Overdue tasks × 10 + High priority tasks × 5
- **Sleep Factor**: Inverse of available sleep hours (8 hours = 0 stress)
- **Risk Levels**: Low (0-40), Medium (41-60), High (61-80), Critical (81-100)

**Important**: Always use `_to_naive()` helper to convert datetimes to timezone-naive before comparisons. Frontend sends ISO strings with timezone info.

### AI Integration (ai_response.py)

- Uses **Claude Sonnet 4.5** via AWS Bedrock (model ID: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`)
- **Retry Logic**: `invoke_model_with_retry()` with exponential backoff (1s, 2s, 4s) for throttling
- **Predictions**: Analyzes schedule to provide 3 specific, personalized burnout predictions
- **Interventions**: Generates 5 actionable recommendations referencing specific events/tasks
- Handles `ThrottlingException` gracefully and returns fallback messages on max retries

### Google Calendar Multi-Calendar Selection (google_calendar.py)

- **Default**: Fetches from `primary` calendar only
- **List Calendars**: `/api/calendar/list` returns all available calendars with colors
- **Selection**: Users can select multiple calendars; events are merged from all selected calendars
- **Persistence**: Selection stored in `GoogleCalendarClient.selected_calendar_ids` (session-based)
- **Endpoints**:
  - `GET /api/calendar/selected` - Get selected calendar IDs
  - `POST /api/calendar/selected` - Update calendar selection

## Development Commands

### Backend Setup & Running

```bash
# Navigate to backend
cd backend

# Activate virtual environment (if needed)
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server (port 8080)
uvicorn main:app --reload --port 8080

# API Documentation (auto-generated)
# http://localhost:8080/docs (Swagger)
# http://localhost:8080/redoc (ReDoc)
```

### Frontend Setup & Running

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server (uses Turbopack)
npm run dev
# Access: http://localhost:3000 or http://localhost:3001

# Build for production
npm run build --turbopack
```

### Testing

```bash
# Backend health check
curl http://localhost:8080/health

# Check auth status
curl http://localhost:8080/auth/status

# List available calendars
curl http://localhost:8080/api/calendar/list

# Get selected calendars
curl http://localhost:8080/api/calendar/selected

# Get calendar events from selected calendars
curl http://localhost:8080/api/calendar/events
```

## Google Calendar OAuth Integration

The app supports real Google Calendar data via OAuth 2.0 with multi-calendar selection:

1. **Setup**: Create Google Cloud project and OAuth credentials
2. **Files**: Place `credentials.json` in `/backend` (gitignored)
3. **Flow**:
   - User clicks "Connect Google Calendar" in frontend
   - Backend redirects to Google OAuth consent screen
   - On approval, tokens stored in `token.json`
   - User selects which calendars to include in analysis
4. **Multi-Calendar**: Events are fetched from all selected calendars and merged

### Important OAuth Notes
- Redirect URI MUST match: `http://localhost:8080/auth/google/callback`
- Update this in both `.env` and Google Cloud Console
- Tokens stored in plaintext `token.json` - NOT production-ready
- Calendar selection is session-based (resets on server restart)
- Requires scope: `https://www.googleapis.com/auth/calendar.readonly`

## Environment Variables

### Backend `.env`
```bash
# AWS Bedrock (required for AI predictions)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-west-2

# Google Calendar OAuth (required)
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/google/callback
```

### Frontend `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## Critical API Endpoints

### Stress Analysis
- `POST /api/stress/analyze` - Main endpoint accepting `{events: CalendarEvent[], tasks: Task[]}`, returns `BurnoutPrediction` with stress score, factors, AI predictions, and interventions

### Auth Flow
- `GET /auth/google` - Returns auth URL for OAuth flow
- `GET /auth/google/callback?code=...` - Handles OAuth callback, stores tokens, redirects to frontend
- `GET /auth/status` - Check authentication status (`{authenticated: bool, provider: string}`)
- `POST /auth/disconnect` - Clear tokens and disconnect calendar

### Calendar
- `GET /api/calendar/list` - Get all available Google calendars with colors and metadata
- `GET /api/calendar/selected` - Get currently selected calendar IDs
- `POST /api/calendar/selected` - Update calendar selection (accepts `List[str]` of calendar IDs)
- `GET /api/calendar/events` - Returns events from selected calendars (empty list if not authenticated)
- `GET /api/calendar/sync` - Trigger manual calendar sync

## Code Patterns

### Working with Datetime (Critical)

**Always convert to timezone-naive before comparisons:**
```python
from datetime import datetime

def _to_naive(dt: datetime) -> datetime:
    """Convert datetime to timezone-naive"""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

# Usage
now = _to_naive(datetime.now())
event_start = _to_naive(event.start)
days_away = (event_start - now).days
```

Frontend sends ISO strings with timezone info; backend uses timezone-naive datetimes to avoid comparison errors.

### AWS Bedrock Retry Pattern

**Handle throttling with exponential backoff:**
```python
def invoke_model_with_retry(client, model_id: str, request_body: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = client.invoke_model(modelId=model_id, body=request_body)
            return json.loads(response.get('body').read())
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
                    time.sleep(wait_time)
                else:
                    raise
```

### Frontend Dashboard Pattern

**User-controlled analysis flow:**
1. Load auth status and calendars on mount (no auto-analysis)
2. Show "Connect Google Calendar" button if not authenticated
3. Show "Select Calendars" UI with checkboxes after connection
4. User clicks "Run Stress Analysis" button to trigger AI analysis
5. Button changes to "Refresh Analysis" after first run

```typescript
useEffect(() => {
  checkAuthStatus();
  // Don't auto-load analysis - let user select calendars first
}, []);
```

## Current Limitations & Known Issues

- **Token Storage**: Plaintext `token.json` - NOT production-ready
- **Calendar Selection**: Session-based, resets on server restart
- **Task Management**: In-memory only, no persistence
- **AWS Throttling**: May encounter rate limits with heavy usage (handled with retry logic)
- **Single Region**: AWS Bedrock configured for `us-west-2` only
- **No Database**: All data is session/file-based

## Key Features Implemented

✅ Google Calendar OAuth 2.0 with multi-calendar selection
✅ AWS Bedrock Claude Sonnet 4.5 integration with retry logic
✅ User-controlled stress analysis (no auto-run)
✅ Calendar selection UI with color indicators
✅ Timezone-aware datetime handling
✅ Next.js 15 frontend with Turbopack
✅ Full-stack integration (backend + frontend)

## Important Files

**Documentation:**
- `CLAUDE.md` - This file, development guidance
- `README.md` - Project overview and quick start
- `backend/GOOGLE_SETUP.md` - Google OAuth setup guide

**Backend Core:**
- `backend/main.py:44` - Main stress analysis endpoint
- `backend/ai_response.py:28` - Bedrock retry logic
- `backend/google_calendar.py:32` - Multi-calendar selection
- `backend/stress_calculator.py:47` - Timezone conversion helper

**Frontend Core:**
- `frontend/components/stress-dashboard.tsx:28` - No auto-analysis pattern
- `frontend/lib/api.ts` - Backend API client
- `frontend/.env.local` - API URL configuration

## Common Errors & Troubleshooting

### "redirect_uri_mismatch" (Google OAuth)
- **Cause**: Mismatch between `.env` redirect URI and Google Cloud Console settings
- **Fix**: Ensure both use `http://localhost:8080/auth/google/callback`

### "can't compare offset-naive and offset-aware datetimes"
- **Cause**: Datetime comparison without timezone normalization
- **Fix**: Use `_to_naive()` helper before all datetime comparisons

### "ThrottlingException" (AWS Bedrock)
- **Cause**: Too many API requests in short time
- **Fix**: Already handled with `invoke_model_with_retry()` exponential backoff

### Dashboard runs analysis automatically
- **Cause**: `loadStressAnalysis()` called in `useEffect`
- **Fix**: Remove auto-load, require user to click "Run Analysis" button

### Calendar selection not persisting
- **Expected behavior**: Selection is session-based, resets on server restart
- **Future fix**: Persist to database or localStorage

## Git Practices

- **Never commit**: `.env`, `credentials.json`, `token.json` (enforced via `.gitignore`)
- **Main branch**: `main`
- **Current branch**: `dmehra`
- **Backend port**: 8080 (not 8000)
- **Frontend redirect**: OAuth redirects to `http://localhost:3000?auth=success`
