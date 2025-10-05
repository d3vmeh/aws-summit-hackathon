# How to Start the Burnout Prevention Agent

## Quick Start (Both Servers Already Running!)

Good news! Both servers are already running in the background:
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:3001

**Just open your browser and visit: http://localhost:3001**

---

## If You Need to Restart

### Option 1: Start Both Servers (Recommended)

Open TWO terminal windows:

**Terminal 1 - Backend:**
```bash
cd /home/dmehra/Documents/ideas/burnout-agent/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd /home/dmehra/Documents/ideas/burnout-agent/frontend
npm run dev
```

Then visit: **http://localhost:3001**

### Option 2: Quick Start Script

Create a start script (optional):

```bash
# backend/start.sh
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

```bash
# frontend/start.sh
#!/bin/bash
cd "$(dirname "$0")"
npm run dev
```

Make executable and run:
```bash
chmod +x backend/start.sh frontend/start.sh
./backend/start.sh &
./frontend/start.sh
```

---

## What You'll See

### Dashboard Features:
1. **Google Calendar Connection Card**
   - Status: "Not Connected" (initially)
   - Button to connect your Google Calendar

2. **Stress Score Dashboard**
   - Overall stress level (0-100)
   - Risk level: Low/Medium/High/Critical
   - Calendar load factor
   - Task pressure factor
   - Sleep quality factor

3. **Burnout Predictions**
   - AI-generated insights
   - Timeline predictions

4. **Recommended Actions**
   - Prioritized interventions
   - Impact scores
   - Effort estimates

### Using Mock Data (Default):
- 3 sample calendar events
- 4 sample tasks (1 overdue)
- Calculated stress score based on mock data

### Using Real Data (After Connecting Google):
- Your actual Google Calendar events
- Real stress analysis based on YOUR schedule
- Personalized predictions

---

## Verify Everything is Working

### Check Backend:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

curl http://localhost:8000/auth/status
# Should return: {"authenticated":false}

curl http://localhost:8000/api/calendar/events
# Should return: [array of 3 mock events]
```

### Check Frontend:
- Open http://localhost:3001 in browser
- Should see full dashboard
- Check browser console (F12) for any errors

---

## Ports Used

- **Backend API:** 8000
- **Frontend:** 3001 (auto-switched from 3000)
- **API Docs:** http://localhost:8000/docs (Swagger UI)

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3001
lsof -ti:3001 | xargs kill -9
```

### Backend Won't Start
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt  # Reinstall dependencies
uvicorn main:app --reload --port 8000
```

### Frontend Won't Start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install  # Reinstall dependencies
npm run dev
```

### "Failed to fetch" in Browser
- Make sure backend is running on port 8000
- Check CORS settings allow localhost:3001
- Hard refresh browser (Ctrl+Shift+R)

---

## Development URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3001 | Main application UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Backend Health | http://localhost:8000/health | Health check endpoint |

---

## Next Steps After Starting

1. **Explore the Dashboard**
   - See mock data visualization
   - Understand stress scoring

2. **Optional: Connect Google Calendar**
   - Follow `GOOGLE_OAUTH_SETUP.md` to set up OAuth
   - Click "Connect Google Calendar" button
   - See your real calendar data analyzed

3. **Test Features**
   - View different stress factors
   - See intervention recommendations
   - Check predictions

---

## Stopping the App

### If running in foreground (Ctrl+C in each terminal)

### If running in background:
```bash
# Find and kill processes
lsof -ti:8000 | xargs kill
lsof -ti:3001 | xargs kill
```

Or use the shell IDs if you know them:
```bash
# Check running background jobs
jobs

# Kill specific job
kill %1  # Replace with job number
```

---

## Current Status

✅ Backend running on port 8000
✅ Frontend running on port 3001
✅ Mock data loaded and working
✅ OAuth endpoints ready (needs credentials.json)

**You're all set! Just visit http://localhost:3001**
