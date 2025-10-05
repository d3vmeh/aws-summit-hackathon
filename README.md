# AWS Summit Hackathon - Burnout Prevention Agent

AI-powered burnout detection and prevention system using **Claude Sonnet 4.5** via AWS Bedrock.

## Project Structure

```
aws-summit-hackathon/
├── backend/              # FastAPI backend with Claude Sonnet 4.5
│   ├── main.py          # API server entry point
│   ├── ai_response.py   # AWS Bedrock / Claude integration
│   ├── schemas.py       # Pydantic data models
│   ├── stress_calculator.py  # Stress scoring algorithm
│   ├── api_test.py      # Backend API tests
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js React frontend (TBD)
├── test_main_api.py     # Integration test for Claude API
├── CLAUDE.md            # Development documentation for Claude Code
└── archive/             # Old backend files (for reference)
```

## Quick Start

### Backend Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file in the backend directory:
```bash
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-west-2
```

3. **Run the server:**
```bash
cd backend
uvicorn main:app --reload --port 8080
```

Backend will be available at:
- API: http://localhost:8080
- Docs: http://localhost:8080/docs

### Test the API

```bash
python test_main_api.py
```

This will send mock calendar events and tasks to the API and display Claude's burnout predictions and interventions.

## Features

- **AI-Powered Analysis**: Uses Claude Sonnet 4.5 via AWS Bedrock for intelligent burnout predictions
- **Stress Scoring**: Multi-factor analysis (calendar density, task load, sleep opportunity)
- **Personalized Interventions**: Specific, actionable recommendations based on your schedule
- **REST API**: FastAPI backend with automatic OpenAPI documentation

## API Endpoints

- `GET /health` - Health check
- `POST /api/stress/analyze` - Analyze stress from calendar events and tasks
- `GET /api/calendar/events` - Get calendar events
- `GET /api/tasks/` - Get tasks

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **AI Model**: Claude Sonnet 4.5 (via AWS Bedrock)
- **Frontend**: Next.js + React + TypeScript (planned)
- **Cloud**: AWS Bedrock

## Model Configuration

Using Claude Sonnet 4.5:
- Model ID: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Region: `us-west-2`
- Max tokens: 1000 (predictions), variable for interventions

## Development

See [CLAUDE.md](./CLAUDE.md) for detailed development documentation.

## Archive

The `archive/old-backend/` directory contains the previous implementation with Google Calendar OAuth and OpenAI integration for reference.
