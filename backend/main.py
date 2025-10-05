from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from routers import stress, calendar, tasks, auth

load_dotenv(override=True)  # Override shell environment variables with .env file

app = FastAPI(
    title="Burnout Prevention Agent API",
    description="AI-powered burnout detection and prevention system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],  # Next.js ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(stress.router, prefix="/api/stress", tags=["stress"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

@app.get("/")
async def root():
    return {"message": "Burnout Prevention Agent API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
