# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Clarity AI** - AI-powered burnout prevention system for university students using **Claude Sonnet 4.5** via AWS Bedrock. Analyzes Google Calendar events, tasks, and sleep patterns to generate personalized stress predictions and actionable interventions.

## Development Commands

### Backend (FastAPI - Python 3.12)

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate

# Run development server
uvicorn main:app --reload --port 8080

# API documentation available at:
# http://localhost:8080/docs
```

### Frontend (Next.js 15 + React 19)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server (with Turbopack)
npm run dev

# Build for production
npm run build

# Application available at:
# http://localhost:3000 (or 3001/3002 if port taken)
```

### Running Both Servers

Two terminal windows required:
1. Terminal 1: Backend on port 8080
2. Terminal 2: Frontend on port 3000

## Architecture

### Core Stress Analysis Flow

The system follows a 4-step analysis pipeline in `backend/main.py:44-75`:

1. **Calculate Stress Score** (`stress_calculator.py`)
   - Weighted formula: `(Calendar × 0.4) + (Tasks × 0.3) + (Sleep × 0.3)`
   - Risk levels: Low (0-40), Medium (41-60), High (61-80), Critical (81-100)

2. **Generate AI Predictions** (`ai_response.py`)
   - Claude Sonnet 4.5 analyzes schedule and generates 3 burnout predictions
   - Uses optimized prompts (500 tokens max) for fast response
   - Includes exponential backoff retry for AWS Bedrock throttling

3. **Generate AI Interventions** (`ai_response.py`)
   - Claude Sonnet 4.5 generates 3-5 actionable recommendations
   - Each intervention includes type, impact score, effort score
   - Types: reschedule, delegate, break_down, micro_break

4. **Return Complete Analysis**
   - Combined response with stress score, factors, predictions, interventions

### Multi-Calendar Architecture

**Flow**: `google_calendar.py` → `main.py` → `stress-dashboard.tsx`

- OAuth tokens stored in `backend/token.json` (gitignored)
- User selects multiple calendars via frontend
- Selection persists in `GoogleCalendarClient.selected_calendar_ids` (in-memory)
- Events fetched from all selected calendars and aggregated

### Timezone Handling Pattern

**Critical**: All datetime comparisons must use timezone-naive datetimes to avoid comparison errors.

Pattern in `stress_calculator.py:7-11` and `ai_response.py:47-51`:

```python
@staticmethod
def _to_naive(dt: datetime) -> datetime:
    """Convert datetime to timezone-naive"""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt
```

Usage:
```python
now = _to_naive(datetime.now())
event_start = _to_naive(event.start)
days_away = (event_start - now).days  # Safe comparison
```

### AWS Bedrock Integration

**Model**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (Claude Sonnet 4.5)
**Region**: `us-west-2`

**Retry Logic** (`ai_response.py:28-45`):
```python
def invoke_model_with_retry(client, model_id: str, request_body: str, max_retries: int = 3):
    """Invoke Bedrock model with exponential backoff retry for throttling"""
    for attempt in range(max_retries):
        try:
            response = client.invoke_model(modelId=model_id, body=request_body)
            return json.loads(response.get('body').read())
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
                    time.sleep(wait_time)
```

**Environment Variables Required**:
```bash
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-west-2
```

### Frontend State Management

**Loading States** (`stress-dashboard.tsx:20-21`):
```typescript
const [loading, setLoading] = useState(false);        // Active analysis
const [initializing, setInitializing] = useState(true); // Page load
```

**Pattern**:
- `loading=true`: Show spinner during AI analysis
- `initializing=true`: Show welcome screen on page load
- User must explicitly click "Run Analysis" (no auto-analysis)

**Calendar Selection** (`stress-dashboard.tsx:224`):
```typescript
async function toggleCalendarSelection(calendarId: string) {
  // ... update selection ...
  await api.setSelectedCalendars(newSelection);
  // Don't auto-reload - let user select multiple calendars then click "Run Analysis"
}
```

### React Key Pattern for Recurring Events

Google Calendar returns recurring events with identical IDs but different start times. Use compound keys:

```typescript
const uniqueKey = `${event.id}-${event.start}`;
<div key={uniqueKey}>...</div>
```

This prevents React duplicate key warnings.

## Environment Configuration

### Backend `.env`

```bash
# AWS Bedrock (required for AI analysis)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-west-2

# Google Calendar OAuth (required for calendar integration)
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/google/callback
```

### Frontend `.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### Google OAuth Setup

1. Create project at https://console.cloud.google.com
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials (Web application)
4. Add redirect URI: `http://localhost:8080/auth/google/callback`
5. Download `credentials.json` to `backend/` directory
6. Set `GOOGLE_REDIRECT_URI` in backend `.env`

## Key API Endpoints

### Analysis
- `POST /api/stress/analyze` - Main stress analysis (sends events + tasks, returns predictions)

### Google Calendar OAuth
- `GET /auth/google` - Get OAuth URL to initiate flow
- `GET /auth/google/callback` - OAuth callback handler (redirects to frontend)
- `GET /auth/status` - Check authentication status
- `POST /auth/disconnect` - Disconnect calendar

### Calendar Management
- `GET /api/calendar/list` - List all available calendars
- `GET /api/calendar/selected` - Get selected calendar IDs
- `POST /api/calendar/selected` - Update calendar selection
- `GET /api/calendar/events?days_ahead=7` - Get events from selected calendars

### Tasks
- `GET /api/tasks/` - Get stored tasks
- `POST /api/tasks/` - Create task

## Data Models (Pydantic)

**Core models** in `schemas.py`:

```python
CalendarEvent(id, summary, start, end, description?)
Task(id, title, description?, due_date?, priority, completed)
StressScore(total_score, calendar_factor, task_factor, sleep_factor, risk_level, timestamp)
StressFactors(events_next_7_days, overdue_tasks, high_priority_tasks, calendar_density, sleep_hours_available)
Intervention(id, type, priority, title, description, impact_score, effort_score)
BurnoutPrediction(stress_score, factors, predictions[], interventions[], historical_comparison?)
```

## Tech Stack

### Backend
- **Framework**: FastAPI
- **AI**: Claude Sonnet 4.5 via AWS Bedrock
- **OAuth**: Google Calendar API (`google-auth-oauthlib`, `googleapiclient`)
- **Storage**: In-memory (no database)

### Frontend
- **Framework**: Next.js 15.5.4 (App Router)
- **Runtime**: React 19.1.0
- **Build**: Turbopack (enabled via `--turbopack` flag)
- **Styling**: Tailwind CSS 4
- **Components**: shadcn/ui (Card, Progress, Badge)
- **Language**: TypeScript

## Important Patterns

### 1. User-Controlled Analysis Flow
Users must explicitly click "Run Analysis" button. Never auto-trigger analysis on:
- Calendar selection changes
- Page load
- Authentication success

### 2. Immediate Loading Feedback
Show loading spinner instantly when "Run Analysis" clicked:
```typescript
async function loadStressAnalysis() {
  setLoading(true);  // Spinner shows immediately
  try {
    // ... fetch data ...
  } finally {
    setLoading(false);
    setInitializing(false);
  }
}
```

### 3. Clean Disconnect Flow
Disconnect should return to initial state, not trigger analysis:
```typescript
async function handleDisconnectCalendar() {
  await api.disconnectCalendar();
  setPrediction(null);  // Clear prediction to return to welcome screen
}
```

### 4. AI Prompt Optimization
Keep prompts concise for faster responses:
- Limit event/task context to top 5-10 items
- Truncate long text to ~200 chars
- Request "1 sentence" descriptions
- Reduce `max_tokens` (predictions: 500, interventions: 800)

## Troubleshooting

### "TypeError: '<' not supported between offset-naive and offset-aware datetime"
**Cause**: Mixing timezone-aware and naive datetimes in comparisons
**Fix**: Use `_to_naive()` helper before all datetime arithmetic:
```python
now = _to_naive(datetime.now())
event_start = _to_naive(event.start)
```

### Google Calendar OAuth Redirect Loop
**Cause**: Mismatch between redirect URI in Google Console and `.env`
**Fix**: Ensure exact match:
- Google Console: `http://localhost:8080/auth/google/callback`
- `.env`: `GOOGLE_REDIRECT_URI=http://localhost:8080/auth/google/callback`

### AWS Bedrock ThrottlingException
**Cause**: Rate limit exceeded
**Fix**: Already handled by `invoke_model_with_retry()` with exponential backoff (1s, 2s, 4s)

### React Duplicate Key Warnings
**Cause**: Recurring calendar events share same event ID
**Fix**: Use compound key: `key={\`${event.id}-${event.start}\`}`

### Frontend Shows "Analyzing stress levels..." After Disconnect
**Cause**: `handleDisconnectCalendar()` calling `loadStressAnalysis()`
**Fix**: Change to `setPrediction(null)` to return to initial state

### Loading Spinner Doesn't Appear Immediately
**Cause**: Complex conditional logic delaying spinner render
**Fix**: Check for `loading` state at top of render tree:
```typescript
if (loading) {
  return <LoadingSpinner />;
}
```

## Current Limitations

- No database - uses in-memory storage (resets on server restart)
- Calendar selection persists only during server uptime
- Single region (us-west-2) for AWS Bedrock
- OAuth tokens stored in plaintext `token.json` (not production-ready)
- No historical pattern analysis (placeholder in response)
- No GitHub/Notion integrations (planned but not implemented)

## Project Structure

```
aws-summit-hackathon/
├── backend/
│   ├── main.py                  # FastAPI app + all endpoints
│   ├── schemas.py               # Pydantic models
│   ├── stress_calculator.py     # Core stress algorithm
│   ├── ai_response.py           # AWS Bedrock / Claude integration
│   ├── google_calendar.py       # OAuth + multi-calendar support
│   ├── credentials.json         # Google OAuth credentials (gitignored)
│   ├── token.json               # OAuth tokens (gitignored)
│   ├── .env                     # AWS + Google config (gitignored)
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main dashboard page
│   │   └── layout.tsx           # Root layout + metadata
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   └── stress-dashboard.tsx # Main dashboard component
│   ├── lib/
│   │   ├── api.ts               # Backend API client
│   │   └── types.ts             # TypeScript interfaces
│   ├── .env.local               # API URL config (gitignored)
│   └── package.json
├── archive/
│   ├── CLAUDE.md                # Old development docs
│   └── test_response_claude.json # Test files
└── README.md                    # User-facing documentation
```
