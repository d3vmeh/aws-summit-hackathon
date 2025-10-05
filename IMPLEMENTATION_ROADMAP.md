# Burnout Prevention Agent - Real Implementation Guide

## Current MVP vs Production Implementation

### Phase 1: Data Integration (Week 1-2)

#### Google Calendar Integration
**Current:** Mock calendar events
**Real Implementation:**

1. **OAuth 2.0 Flow**
```python
# backend/routers/auth.py
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

@router.get("/auth/google")
async def google_auth():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri='http://localhost:8000/auth/callback'
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return {"auth_url": auth_url}

@router.get("/auth/callback")
async def google_callback(code: str, db: Session):
    flow = Flow.from_client_secrets_file(...)
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Store credentials in database for user
    save_user_credentials(credentials, user_id)

    # Fetch calendar events
    service = build('calendar', 'v3', credentials=credentials)
    events = service.events().list(
        calendarId='primary',
        timeMin=datetime.utcnow().isoformat() + 'Z',
        maxResults=100,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return {"status": "connected", "events_count": len(events.get('items', []))}
```

**Frontend Integration:**
```typescript
// lib/auth.ts
export async function connectGoogleCalendar() {
  const response = await fetch(`${API_URL}/auth/google`);
  const { auth_url } = await response.json();
  window.location.href = auth_url; // Redirect to Google OAuth
}
```

**Why This Works:**
- User authorizes once, credentials stored securely
- Background job refreshes events every 15 minutes
- Real-time calendar density calculations
- Detects last-minute schedule changes

#### GitHub Integration (For Developers/CS Students)
**Current:** None
**Real Implementation:**

```python
# backend/utils/github_tracker.py
import httpx
from datetime import datetime, timedelta

async def fetch_github_activity(username: str, token: str):
    headers = {"Authorization": f"token {token}"}

    # Get commits from last 7 days
    since = (datetime.now() - timedelta(days=7)).isoformat()

    async with httpx.AsyncClient() as client:
        # Get user's repos
        repos = await client.get(
            f"https://api.github.com/user/repos",
            headers=headers
        )

        all_commits = []
        for repo in repos.json():
            commits = await client.get(
                f"https://api.github.com/repos/{repo['full_name']}/commits",
                params={"since": since, "author": username},
                headers=headers
            )
            all_commits.extend(commits.json())

    # Analyze commit patterns
    late_night_commits = [
        c for c in all_commits
        if datetime.fromisoformat(c['commit']['author']['date'].replace('Z', '+00:00')).hour > 23
    ]

    return {
        "total_commits": len(all_commits),
        "late_night_commits": len(late_night_commits),
        "burnout_signal": len(late_night_commits) > 5  # Red flag
    }
```

**Stress Calculation Enhancement:**
```python
# Add GitHub factor to stress score
if github_data['late_night_commits'] > 5:
    stress_score.task_factor += 15  # Late night coding = stress indicator
```

#### Notion/Todoist Task Integration
**Current:** Mock task list
**Real Implementation:**

```python
# backend/utils/notion_sync.py
from notion_client import Client

async def sync_notion_tasks(notion_token: str, database_id: str):
    notion = Client(auth=notion_token)

    # Query Notion database
    results = notion.databases.query(
        database_id=database_id,
        filter={
            "or": [
                {"property": "Status", "select": {"equals": "In Progress"}},
                {"property": "Status", "select": {"equals": "Not Started"}}
            ]
        }
    )

    tasks = []
    for page in results['results']:
        props = page['properties']

        # Extract task data
        task = Task(
            id=page['id'],
            title=props['Name']['title'][0]['text']['content'],
            due_date=props.get('Due Date', {}).get('date', {}).get('start'),
            priority=props.get('Priority', {}).get('select', {}).get('name', 'medium').lower(),
            completed=props['Status']['select']['name'] == 'Done'
        )
        tasks.append(task)

    return tasks
```

**Alternative: Todoist API:**
```python
# backend/utils/todoist_sync.py
from todoist_api_python.api import TodoistAPI

async def sync_todoist_tasks(api_token: str):
    api = TodoistAPI(api_token)

    tasks = api.get_tasks()

    return [
        Task(
            id=t.id,
            title=t.content,
            due_date=t.due.date if t.due else None,
            priority="high" if t.priority >= 4 else "medium" if t.priority >= 2 else "low",
            completed=t.is_completed
        )
        for t in tasks
    ]
```

---

### Phase 2: Intelligent Pattern Recognition (Week 3-4)

#### Historical Data Storage
**Current:** No persistence
**Real Implementation:**

```python
# backend/models/database.py
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    google_credentials = Column(String)  # Encrypted
    github_token = Column(String)  # Encrypted
    stress_scores = relationship("StressScore", back_populates="user")

class StressScoreRecord(Base):
    __tablename__ = "stress_scores"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime)
    total_score = Column(Float)
    calendar_factor = Column(Float)
    task_factor = Column(Float)
    sleep_factor = Column(Float)
    risk_level = Column(String)
    user = relationship("User", back_populates="stress_scores")

class BurnoutEvent(Base):
    __tablename__ = "burnout_events"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime)
    severity = Column(String)  # mild, moderate, severe
    days_predicted_in_advance = Column(Integer)  # How early we predicted it
    outcome = Column(String)  # prevented, occurred, false_alarm
```

**Usage:**
```python
# Save stress score every hour
@router.post("/api/stress/record")
async def record_stress_score(stress_score: StressScore, db: Session, user_id: int):
    record = StressScoreRecord(
        user_id=user_id,
        timestamp=datetime.now(),
        total_score=stress_score.total_score,
        calendar_factor=stress_score.calendar_factor,
        task_factor=stress_score.task_factor,
        sleep_factor=stress_score.sleep_factor,
        risk_level=stress_score.risk_level
    )
    db.add(record)
    db.commit()

    # Analyze trends
    recent_scores = db.query(StressScoreRecord).filter(
        StressScoreRecord.user_id == user_id,
        StressScoreRecord.timestamp > datetime.now() - timedelta(days=7)
    ).all()

    # Detect rising trend
    if len(recent_scores) > 10:
        trend = calculate_trend([s.total_score for s in recent_scores])
        if trend > 5:  # Score increasing by 5+ per day
            return {"alert": "Stress trending up rapidly - burnout risk in 3 days"}
```

#### Machine Learning Prediction
**Current:** Rule-based scoring
**Real Implementation:**

```python
# backend/utils/ml_predictor.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class BurnoutPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()

    def train(self, historical_data):
        """Train on user's historical burnout patterns"""
        # Features: past 7 days of stress scores, calendar density, task counts
        X = pd.DataFrame([
            {
                'avg_stress_7d': d['avg_stress'],
                'max_stress_7d': d['max_stress'],
                'calendar_density': d['calendar_density'],
                'overdue_tasks': d['overdue_tasks'],
                'sleep_hours': d['sleep_hours'],
                'late_commits': d['late_commits'],
                'stress_trend': d['stress_trend']  # slope of stress over time
            }
            for d in historical_data
        ])

        # Label: did burnout occur in next 3 days?
        y = [d['burnout_occurred'] for d in historical_data]

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict_burnout_probability(self, current_data):
        """Return probability of burnout in next 3 days"""
        X = self.scaler.transform([current_data])
        probability = self.model.predict_proba(X)[0][1]  # Prob of class 1 (burnout)

        return {
            "burnout_probability": probability,
            "risk_level": "critical" if probability > 0.7 else "high" if probability > 0.5 else "medium",
            "predicted_days_until_burnout": self._estimate_days(probability)
        }

    def _estimate_days(self, probability):
        # Simple heuristic: higher probability = sooner
        if probability > 0.8:
            return 1
        elif probability > 0.6:
            return 2
        elif probability > 0.4:
            return 3
        else:
            return 5
```

**Feature Engineering:**
```python
def extract_features_for_ml(user_id: int, db: Session):
    # Get last 7 days of data
    scores = db.query(StressScoreRecord).filter(
        StressScoreRecord.user_id == user_id,
        StressScoreRecord.timestamp > datetime.now() - timedelta(days=7)
    ).all()

    if len(scores) < 5:
        return None  # Not enough data

    stress_values = [s.total_score for s in scores]

    return {
        'avg_stress_7d': np.mean(stress_values),
        'max_stress_7d': max(stress_values),
        'std_stress_7d': np.std(stress_values),
        'stress_trend': calculate_slope(stress_values),
        'calendar_density': scores[-1].calendar_factor,
        'overdue_tasks': get_overdue_tasks_count(user_id),
        'sleep_hours': scores[-1].sleep_factor,
        'late_commits': get_late_night_commits(user_id)
    }
```

---

### Phase 3: Proactive Interventions (Week 5-6)

#### Alert System
**Current:** Just displays interventions
**Real Implementation:**

```python
# backend/utils/notification_service.py
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText

class NotificationService:
    def __init__(self):
        self.twilio_client = Client(account_sid, auth_token)

    async def send_alert(self, user: User, alert_type: str, message: str):
        # SMS via Twilio
        if user.phone_number and user.sms_enabled:
            self.twilio_client.messages.create(
                body=f"🚨 Burnout Alert: {message}",
                from_='+1234567890',
                to=user.phone_number
            )

        # Email
        if user.email and user.email_enabled:
            msg = MIMEText(f"""
            Hi {user.name},

            Our AI has detected a high burnout risk:

            {message}

            Recommended actions:
            {generate_intervention_email(user)}

            View full dashboard: {FRONTEND_URL}/dashboard
            """)
            msg['Subject'] = f'Burnout Risk Alert - {alert_type}'
            msg['From'] = 'alerts@burnoutprevention.ai'
            msg['To'] = user.email

            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.starttls()
            smtp.login(email_user, email_password)
            smtp.send_message(msg)
            smtp.quit()

        # Push notification (if mobile app)
        if user.push_token:
            send_push_notification(user.push_token, message)
```

**Smart Scheduling:**
```python
# backend/utils/smart_scheduler.py
class SmartScheduler:
    """Automatically suggests reschedules and creates calendar blocks"""

    async def auto_create_recovery_blocks(self, user_id: int, stress_score: float):
        if stress_score > 75:
            # Find next available 2-hour window
            calendar_service = get_user_calendar_service(user_id)

            # Look for gaps in next 3 days
            free_slots = calendar_service.freebusy().query(
                body={
                    "timeMin": datetime.now().isoformat(),
                    "timeMax": (datetime.now() + timedelta(days=3)).isoformat(),
                    "items": [{"id": "primary"}]
                }
            ).execute()

            # Create "Recovery Time" block in first available slot
            event = {
                'summary': '🌿 Recovery Time (Auto-scheduled)',
                'description': 'Burnout prevention system detected high stress. Use this time to rest.',
                'start': {'dateTime': first_free_slot},
                'end': {'dateTime': first_free_slot + timedelta(hours=2)},
                'reminders': {'useDefault': False, 'overrides': [
                    {'method': 'popup', 'minutes': 30}
                ]}
            }

            calendar_service.events().insert(calendarId='primary', body=event).execute()

            return {"status": "created", "time": first_free_slot}

    async def suggest_reschedulable_events(self, user_id: int):
        """Find low-priority events that could be moved"""
        events = get_upcoming_events(user_id, days=7)

        # Heuristics for reschedulable events
        candidates = []
        for event in events:
            if any(keyword in event.summary.lower() for keyword in
                   ['coffee', 'chat', 'social', 'optional', 'networking']):
                candidates.append({
                    "event": event,
                    "reason": "Social event - can reschedule without major impact",
                    "impact_score": 15
                })

        return candidates
```

#### Intelligent Delegation
**Current:** Generic "delegate" suggestion
**Real Implementation:**

```python
# backend/utils/delegation_analyzer.py
class DelegationAnalyzer:
    """Analyzes tasks and suggests who can take them"""

    async def find_delegation_opportunities(self, user_id: int, team_members: list):
        user_tasks = get_user_tasks(user_id)

        suggestions = []
        for task in user_tasks:
            if task.priority == "low" or task.due_date > datetime.now() + timedelta(days=5):
                # Find team member with capacity
                for member in team_members:
                    member_stress = get_stress_score(member.id)
                    if member_stress < 40:  # They have capacity
                        # Check skill match (if using NLP)
                        skill_match = calculate_skill_match(task.title, member.skills)

                        if skill_match > 0.6:
                            suggestions.append({
                                "task": task,
                                "suggested_person": member.name,
                                "reason": f"{member.name} has capacity and relevant skills",
                                "confidence": skill_match
                            })

        return suggestions
```

---

### Phase 4: Frontend Intelligence (Week 7)

#### Real-Time Dashboard Updates
**Current:** Static data
**Real Implementation:**

```typescript
// components/live-stress-monitor.tsx
'use client';

import { useEffect, useState } from 'react';

export function LiveStressMonitor() {
  const [stressScore, setStressScore] = useState(null);

  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws/stress');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStressScore(data);

      // Show browser notification if critical
      if (data.risk_level === 'critical' && Notification.permission === 'granted') {
        new Notification('⚠️ Burnout Risk Critical', {
          body: 'Your stress levels are dangerously high. Take a break now.',
          icon: '/alert-icon.png'
        });
      }
    };

    // Update every 15 minutes
    const interval = setInterval(() => {
      ws.send(JSON.stringify({ action: 'refresh' }));
    }, 15 * 60 * 1000);

    return () => {
      ws.close();
      clearInterval(interval);
    };
  }, []);

  return <StressDashboard data={stressScore} />;
}
```

**Backend WebSocket:**
```python
# backend/main.py
from fastapi import WebSocket

@app.websocket("/ws/stress")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()

    while True:
        # Recalculate stress every time we get new data
        events = await fetch_calendar_events(user_id)
        tasks = await fetch_tasks(user_id)

        stress_score = StressCalculator.calculate_stress_score(events, tasks)

        await websocket.send_json(stress_score.dict())

        # Wait for next update trigger
        await asyncio.sleep(900)  # 15 minutes
```

---

### Phase 5: Production Deployment

#### Infrastructure
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/burnout_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://api.burnoutprevention.ai

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    # For caching and background jobs

  worker:
    build: ./backend
    command: celery -A tasks worker
    # Background jobs: sync calendars, send alerts

  scheduler:
    build: ./backend
    command: celery -A tasks beat
    # Periodic tasks: check stress scores every hour

volumes:
  postgres_data:
```

#### Background Jobs
```python
# backend/tasks.py
from celery import Celery

celery = Celery('burnout_agent', broker='redis://localhost:6379')

@celery.task
def sync_all_user_calendars():
    """Run every 15 minutes"""
    users = db.query(User).all()
    for user in users:
        events = fetch_google_calendar(user.google_credentials)
        update_user_events(user.id, events)

@celery.task
def check_burnout_risks():
    """Run every hour"""
    users = db.query(User).all()
    for user in users:
        stress_score = calculate_current_stress(user.id)

        if stress_score.risk_level in ['high', 'critical']:
            send_alert(user, stress_score)

        # Record in database
        save_stress_score(user.id, stress_score)

@celery.beat_schedule = {
    'sync-calendars': {
        'task': 'tasks.sync_all_user_calendars',
        'schedule': 900.0,  # 15 minutes
    },
    'check-burnout': {
        'task': 'tasks.check_burnout_risks',
        'schedule': 3600.0,  # 1 hour
    },
}
```

---

## Summary: How It Really Works

### Data Flow (Production)
1. **User onboards** → Connects Google Calendar, GitHub, Notion
2. **Background sync** → Every 15 min, fetch latest events/tasks/commits
3. **Real-time calculation** → Update stress score based on new data
4. **ML prediction** → Use historical patterns to predict burnout 3-5 days ahead
5. **Proactive alerts** → If risk high, send SMS/email/push notification
6. **Smart interventions** → Auto-create recovery blocks, suggest rescheduling
7. **Learning loop** → Track if user burned out → improve ML model

### Key Technologies Needed
- **Auth:** OAuth 2.0 (Google), GitHub tokens, Notion API keys
- **Database:** PostgreSQL (user data, historical scores)
- **Cache:** Redis (fast lookups, session storage)
- **Background Jobs:** Celery + Redis (periodic syncs)
- **ML:** scikit-learn or TensorFlow (burnout prediction)
- **Notifications:** Twilio (SMS), SendGrid (email), Firebase (push)
- **Hosting:** AWS/GCP/DigitalOcean + Docker

### What Makes It Actually Work
1. **Continuous data sync** - Not one-time analysis, but always monitoring
2. **Pattern learning** - Gets smarter the more you use it
3. **Proactive** - Predicts problems before they happen
4. **Actionable** - Doesn't just say "you're stressed", creates solutions
5. **Integrated** - Works with tools students already use

The MVP you have now is the UI/UX skeleton. Real implementation = connecting the pipes to live data sources and adding intelligence layer.
