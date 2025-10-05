import os
from typing import Optional
from descope import DescopeClient, AuthException

def get_descope_client():
    """Get Descope client instance"""
    project_id = os.getenv("DESCOPE_PROJECT_ID")
    management_key = os.getenv("DESCOPE_MANAGEMENT_KEY")
    
    if not project_id or not management_key:
        raise ValueError("DESCOPE_PROJECT_ID and DESCOPE_MANAGEMENT_KEY must be set")
    
    return DescopeClient(project_id=project_id, management_key=management_key)

def get_user_google_calendar_token(user_id: str) -> Optional[str]:
    """Get Google Calendar access token for user from Descope outbound app"""
    try:
        client = get_descope_client()
        tokens = client.mgmt.outbound_app.get_user_tokens(
            app_id="google-calendar",
            user_id=user_id
        )
        
        if tokens and tokens.get("tokens"):
            return tokens["tokens"][0].get("accessToken")
        return None
    except AuthException:
        return None

def refresh_user_google_calendar_token(user_id: str) -> Optional[str]:
    """Refresh Google Calendar access token for user"""
    try:
        client = get_descope_client()
        refreshed_tokens = client.mgmt.outbound_app.refresh_user_tokens(
            app_id="google-calendar",
            user_id=user_id
        )
        
        if refreshed_tokens and refreshed_tokens.get("tokens"):
            return refreshed_tokens["tokens"][0].get("accessToken")
        return None
    except AuthException:
        return None
