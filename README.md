# Burnout Prevention Agent

AI-powered burnout detection and prevention system for university students.

## Project Structure

```
burnout-agent/
├── backend/          # FastAPI Python backend
│   ├── venv/        # Python virtual environment
│   ├── main.py      # FastAPI application
│   ├── models/      # Pydantic schemas
│   ├── routers/     # API endpoints
│   ├── utils/       # Business logic
│   └── requirements.txt
└── frontend/        # Next.js React frontend
    ├── app/         # Next.js app directory
    ├── components/  # React components
    ├── lib/         # API client & utilities
    └── package.json
```

## Features

### Current (MVP)
- ✅ Real-time stress scoring based on calendar and task data
- ✅ Multi-factor analysis (calendar density, task load, sleep opportunity)
- ✅ Intelligent intervention suggestions
- ✅ Risk level categorization (low/medium/high/critical)
- ✅ Beautiful UI with Tailwind CSS and shadcn/ui
- ✅ Mock data for demo purposes

### Upcoming
- 🔄 Google Calendar OAuth integration
- 🔄 GitHub API integration (commit tracking)
- 🔄 Notion/Todoist task syncing
- 🔄 Historical pattern analysis
- 🔄 SMS/Email alert notifications
- 🔄 Machine learning burnout prediction

## Getting Started

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Activate virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies (already done):
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies (already done):
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## API Endpoints

### Stress Analysis
- `POST /api/stress/analyze` - Analyze stress from calendar events and tasks
  - Request body: `{ events: CalendarEvent[], tasks: Task[] }`
  - Response: `BurnoutPrediction`

### Calendar
- `GET /api/calendar/events` - Get all calendar events
- `POST /api/calendar/events` - Create calendar event
- `GET /api/calendar/sync` - Sync with Google Calendar (placeholder)

### Tasks
- `GET /api/tasks/` - Get all tasks
- `POST /api/tasks/` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

## How It Works

### Stress Calculation Algorithm

**Total Stress Score** = (Calendar Factor × 0.4) + (Task Factor × 0.3) + (Sleep Factor × 0.3)

**Calendar Factor:**
- Calendar density (% of day scheduled)
- Number of events in next 7 days

**Task Factor:**
- Number of overdue tasks (×10 weight)
- Number of high-priority tasks (×5 weight)

**Sleep Factor:**
- Inverse of available sleep hours
- Calculated from event schedule gaps

**Risk Levels:**
- 0-40: Low
- 41-60: Medium
- 61-80: High
- 81-100: Critical

### Intervention Engine

Generates prioritized interventions based on:
- Impact score (stress reduction potential)
- Effort score (implementation difficulty)
- ROI ratio (impact/effort)

Types of interventions:
1. **Reschedule** - Move non-urgent meetings
2. **Delegate** - Assign tasks to others
3. **Break Down** - Split large tasks into subtasks
4. **Micro Break** - Schedule recovery time

## Tech Stack

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.12
- **Validation:** Pydantic
- **API Integrations:** Google Calendar, GitHub, Notion (planned)

### Frontend
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **Icons:** Lucide React

## Environment Variables

### Backend (.env)
```bash
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
NOTION_API_KEY=your_notion_key
GITHUB_TOKEN=your_github_token
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Demo Data

The app includes mock data for demonstration:
- 3 calendar events (lecture, meeting, exam)
- 4 tasks (2 high priority, 1 overdue)

This generates a realistic stress score and interventions for testing.

## Development Notes

- Backend uses mock data stores (lists) - replace with database for production
- Google Calendar OAuth flow is stubbed - needs implementation
- Historical comparison is placeholder - needs user data tracking
- All calculations are synchronous - consider async for real API calls

## Next Steps for Hackathon

1. ✅ Basic full-stack setup - COMPLETE
2. 🔄 Add Google Calendar OAuth flow
3. 🔄 Implement GitHub commit tracking
4. 🔄 Add data persistence (SQLite/PostgreSQL)
5. 🔄 Create demo scenarios with realistic student data
6. 🔄 Polish UI/UX
7. 🔄 Prepare pitch deck

## Running Both Servers

Quick start both servers:

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

Or use the background processes already running:
- Backend: http://localhost:8000
- Frontend: http://localhost:3001 (auto-switched from 3000)

## Current Status

✅ Full-stack application is running and functional!
- Backend API: Serving mock data and stress analysis
- Frontend UI: Displaying stress dashboard with real-time calculations
- CORS: Configured for local development
- Components: Using shadcn/ui for professional appearance

Visit http://localhost:3001 to see the dashboard in action.
