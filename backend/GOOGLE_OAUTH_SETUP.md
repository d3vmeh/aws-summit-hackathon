# Google Calendar OAuth Setup Guide

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "Burnout Prevention Agent"
4. Click "Create"

## Step 2: Enable Google Calendar API

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - User Type: "External" (for testing)
   - App name: "Burnout Prevention Agent"
   - User support email: (your email)
   - Developer contact: (your email)
   - Click "Save and Continue"
   - Scopes: Click "Add or Remove Scopes"
     - Add: `https://www.googleapis.com/auth/calendar.readonly`
     - Click "Update" → "Save and Continue"
   - Test users: Add your email (for testing)
   - Click "Save and Continue" → "Back to Dashboard"

4. Now create credentials:
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Name: "Burnout Agent Backend"
   - Authorized redirect URIs:
     - Add: `http://localhost:8000/auth/google/callback`
   - Click "Create"

5. Copy the Client ID and Client Secret

## Step 4: Download Credentials

1. Click the download icon next to your OAuth client
2. Save the JSON file as `credentials.json` in the `backend/` directory

**OR** manually create `backend/credentials.json`:
```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost:8000/auth/google/callback"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

## Step 5: Update .env file

Add to `backend/.env`:
```bash
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

## Testing OAuth Flow

Once setup is complete:
1. Start backend: `uvicorn main:app --reload`
2. Visit: http://localhost:8000/auth/google
3. You'll be redirected to Google login
4. Grant permissions
5. You'll be redirected back with calendar access

## Security Notes

- **NEVER commit credentials.json or .env to git**
- Add to `.gitignore`:
  ```
  credentials.json
  .env
  token.json
  ```
- For production, use environment variables, not files
