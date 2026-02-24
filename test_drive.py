# test_google_drive_oauth.py

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')  # or production if needed
django.setup()

from django.conf import settings
from google_auth_oauthlib.flow import Flow

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def generate_google_drive_auth_url():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_DRIVE_CLIENT_ID,
                "client_secret": settings.GOOGLE_DRIVE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_DRIVE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = settings.GOOGLE_DRIVE_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    print("✅ Google Drive OAuth URL:")
    print(authorization_url)
    print("\n🌐 After granting permission, Google will redirect to your redirect URI with `code=...` in query params.")
    print("⚠️ Manually extract the `code` and use it in the next step to fetch the token.")
    return flow, state

def exchange_code_for_token(code, state):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_DRIVE_CLIENT_ID,
                "client_secret": settings.GOOGLE_DRIVE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_DRIVE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = settings.GOOGLE_DRIVE_REDIRECT_URI
    auth_response = input("Paste the full redirect URL from browser: ").strip()
    flow.fetch_token(authorization_response=auth_response)
    
    credentials = flow.credentials

    print("\n🎯 Tokens received:")
    print("Access Token:", credentials.token)
    print("Refresh Token:", credentials.refresh_token)
    print("Token URI:", credentials.token_uri)
    print("Client ID:", credentials.client_id)
    print("Client Secret:", credentials.client_secret)
    print("Scopes:", credentials.scopes)

    # Save to file for testing or simulation
    with open("google_drive_token.json", "w") as f:
        f.write(credentials.to_json())
    print("\n✅ Token saved to google_drive_token.json")

if __name__ == '__main__':
    print("🔁 Starting OAuth Test for Google Drive")
    flow, state = generate_google_drive_auth_url()
    print("\n🚀 Visit the URL above and complete the flow. Then paste the redirect URL below.\n")
    exchange_code_for_token(code=None, state=state)
