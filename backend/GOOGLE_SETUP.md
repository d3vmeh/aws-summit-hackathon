# Google Calendar OAuth Setup Guide

## Quick Setup

###  1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google Calendar API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: "External"
   - App name: "Burnout Prevention Agent"
   - Add your email as developer contact
   - Scopes: Add `https://www.googleapis.com/auth/calendar.readonly`
   - Test users: Add your email

4. Create OAuth Client:
   - Application type: **Web application**
   - Name: "Burnout Prevention Backend"
   - Authorized redirect URIs:
     ```
     http://localhost:8080/auth/google/callback
     ```
   - Click "Create"

### 3. Download credentials.json

1. Click the download button next to your OAuth 2.0 Client
2. Save the file as `credentials.json` in the `backend/` directory

### 4. Update .env file

Add to `backend/.env`:
```bash
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/google/callback
```

## Testing the Integration

1. Start the backend server:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8080
```

2. Check auth status:
```bash
curl http://localhost:8080/auth/status
# Should return: {"authenticated": false, "provider": null}
```

3. Get OAuth URL:
```bash
curl http://localhost:8080/auth/google
# Returns: {"auth_url": "https://accounts.google.com/o/oauth2/auth?..."}
```

4. Open the auth_url in your browser, authorize the app

5. After authorization, check status again:
```bash
curl http://localhost:8080/auth/status
# Should return: {"authenticated": true, "provider": "Google Calendar"}
```

6. Fetch your calendar events:
```bash
curl http://localhost:8080/api/calendar/events
# Returns your Google Calendar events for the next 7 days
```

## API Endpoints

- `GET /auth/google` - Get OAuth authorization URL
- `GET /auth/google/callback` - OAuth callback (handled by browser redirect)
- `GET /auth/status` - Check authentication status
- `POST /auth/disconnect` - Disconnect Google Calendar
- `GET /api/calendar/events?days_ahead=7` - Fetch calendar events
- `GET /api/calendar/sync?days_ahead=7` - Manually sync calendar

## Security Notes

- **credentials.json** and **token.json** are in .gitignore
- Never commit these files to git
- Token is refreshed automatically when expired
- Only read-only access to calendar (cannot modify events)

## Troubleshooting

**"credentials.json not found"**
- Make sure credentials.json is in the backend/ directory
- Download it from Google Cloud Console

**"Not authenticated"**
- Visit `/auth/google` to get the OAuth URL
- Complete the authorization in your browser

**"Redirect URI mismatch"**
- Make sure the redirect URI in Google Cloud Console exactly matches:
  `http://localhost:8080/auth/google/callback`
