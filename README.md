# Clarity AI - Burnout Prevention System

AI-powered burnout detection and prevention for university students using **Claude Sonnet 4.5** via AWS Bedrock.

## Project Structure

```
aws-summit-hackathon/
├── backend/                        # FastAPI backend with Claude Sonnet 4.5
│   ├── main.py                     # API server (port 8080)
│   ├── ai_response.py              # AWS Bedrock / Claude integration with retry logic
│   ├── schemas.py                  # Pydantic data models
│   ├── stress_calculator.py        # Stress scoring algorithm
│   ├── google_calendar.py          # OAuth + multi-calendar selection
│   ├── token.json                  # OAuth tokens (gitignored)
│   └── requirements.txt            # Python dependencies
├── frontend/                       # Next.js 15 + React 19 + Turbopack
│   ├── app/                        # Next.js App Router
│   ├── components/                 # React components (stress dashboard, UI)
│   ├── lib/                        # API client and utilities
│   └── package.json                # Frontend dependencies
├── CLAUDE.md                       # Development documentation for Claude Code
└── README.md                       # This file
```

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- AWS account with Bedrock access
- Google Cloud Console project (for Calendar OAuth)

### Backend Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file in the backend directory:
```bash
# AWS Bedrock (required)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-west-2

# Google Calendar OAuth (required)
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/google/callback
```

3. **Set up Google Calendar OAuth:**
- Follow instructions in `backend/GOOGLE_SETUP.md`
- Place `credentials.json` in `backend/` directory

4. **Run the server:**
```bash
cd backend
uvicorn main:app --reload --port 8080
```

Backend will be available at:
- API: http://localhost:8080
- API Docs: http://localhost:8080/docs

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Set up environment variables:**
Create a `.env.local` file in the frontend directory:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

3. **Run the development server:**
```bash
npm run dev
```

Frontend will be available at:
- http://localhost:3000 (or 3001/3002 if port is taken)

### Access the App

1. Open http://localhost:3000 in your browser
2. Click "Connect Google Calendar"
3. Authorize access to your calendars
4. Select which calendars to include in analysis
5. Click "Run Stress Analysis" to see your burnout risk assessment

## Features

### Core Functionality
- ✅ **Google Calendar Integration** - OAuth 2.0 with multi-calendar selection
- ✅ **AI-Powered Analysis** - Claude Sonnet 4.5 via AWS Bedrock with retry logic
- ✅ **Stress Scoring** - Multi-factor analysis (40% calendar, 30% tasks, 30% sleep)
- ✅ **Burnout Predictions** - 3 personalized predictions based on your schedule
- ✅ **Smart Interventions** - 5 actionable recommendations with impact/effort scores

### User Experience
- ✅ **Multi-Calendar Selection** - Choose which calendars to include in analysis
- ✅ **User-Controlled Analysis** - Click "Run Analysis" when ready (no auto-run)
- ✅ **Immediate Loading Feedback** - Loading spinner appears instantly
- ✅ **Modern UI** - Next.js 15 with Tailwind CSS 4 and shadcn/ui components
- ✅ **Turbopack** - Fast development builds

## How It Works

1. **Calendar Connection**: Securely connect your Google Calendar via OAuth 2.0
2. **Calendar Selection**: Choose which calendars to include (work, personal, etc.)
3. **Stress Calculation**: Algorithm analyzes:
   - Calendar density (% of waking hours scheduled)
   - Event count and distribution
   - Task deadlines and priorities
   - Sleep opportunity
4. **AI Analysis**: Claude Sonnet 4.5 generates:
   - Specific burnout predictions referencing your actual events
   - Personalized interventions sorted by ROI (impact/effort)
5. **Results**: View risk level, stress factors, predictions, and recommended actions

## Key API Endpoints

### Analysis
- `POST /api/stress/analyze` - Main stress analysis endpoint

### Authentication
- `GET /auth/google` - Initiate Google OAuth flow
- `GET /auth/google/callback` - OAuth callback handler
- `GET /auth/status` - Check authentication status
- `POST /auth/disconnect` - Disconnect calendar

### Calendar Management
- `GET /api/calendar/list` - List all available calendars
- `GET /api/calendar/selected` - Get selected calendar IDs
- `POST /api/calendar/selected` - Update calendar selection
- `GET /api/calendar/events` - Get events from selected calendars

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **AI Model**: Claude Sonnet 4.5 via AWS Bedrock
- **Model ID**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- **Region**: us-west-2
- **OAuth**: Google Calendar API with multi-calendar support

### Frontend
- **Framework**: Next.js 15.5.4 with App Router
- **Runtime**: React 19.1.0
- **Build Tool**: Turbopack
- **Styling**: Tailwind CSS 4
- **Components**: shadcn/ui (Card, Progress, Badge)
- **Language**: TypeScript

## Development

See [CLAUDE.md](./CLAUDE.md) for detailed development documentation, code patterns, and troubleshooting.

## Current Limitations

- No database - session-based storage
- Calendar selection resets on server restart
- Single region (us-west-2) for AWS Bedrock
- OAuth tokens stored in plaintext (not production-ready)
