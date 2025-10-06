#!/usr/bin/env python3
"""
Simple Gmail OAuth Setup Script
Generates OAuth token without requiring database or backend imports
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Paths from .env
CREDENTIALS_FILE = '/Users/matthewscott/Desktop/Job_Search/client_secret_2_234263158377-qne0ms5qlreqnn0k7pm2lg8tl10kev82.apps.googleusercontent.com.json'
TOKEN_FILE = '/Users/matthewscott/Desktop/Job_Search/gmail_token.json'

def main():
    """Run OAuth flow and generate token"""
    print("=" * 70)
    print("Gmail OAuth Setup for Job Search Automation")
    print("=" * 70)
    print()
    print("This will open a browser window where you'll:")
    print("  1. Sign in to your Google account")
    print("  2. Grant permission to access Gmail")
    print("  3. Generate an authentication token")
    print()
    print("IMPORTANT:")
    print("  • Use the Gmail account you want to monitor for job responses")
    print("  • Click 'Continue' when you see the app isn't verified warning")
    print("  • Click 'Allow' when asked for Gmail permissions")
    print()

    print("Starting OAuth flow in 2 seconds...")
    print()

    creds = None
    token_path = Path(TOKEN_FILE)

    # Check if token already exists
    if token_path.exists():
        print("⚠️  Existing token found. Checking if it's still valid...")
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception as e:
            print(f"   Error loading existing token: {e}")
            creds = None

    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                print("   Starting new OAuth flow...")
                creds = None

        if not creds:
            # Check credentials file exists
            if not Path(CREDENTIALS_FILE).exists():
                print(f"❌ ERROR: Credentials file not found at:")
                print(f"   {CREDENTIALS_FILE}")
                print()
                print("Please make sure the credentials file is in the correct location.")
                return False

            print("🌐 Opening browser for authentication...")
            print()

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                # This will open a browser and wait for authorization
                creds = flow.run_local_server(port=0)
                print()
                print("✅ Authentication successful!")

            except Exception as e:
                print()
                print(f"❌ OAuth flow failed: {e}")
                print()
                print("Common issues:")
                print("  • Gmail API not enabled in Google Cloud Console")
                print("  • OAuth consent screen not configured")
                print("  • Incorrect credentials file")
                return False

        # Save the credentials for next time
        print()
        print("💾 Saving token to:", TOKEN_FILE)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    else:
        print("✅ Existing token is valid!")

    # Test the connection
    print()
    print("🧪 Testing Gmail API connection...")
    try:
        service = build('gmail', 'v1', credentials=creds)
        # Get user profile to verify connection
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress')

        print()
        print("=" * 70)
        print("🎉 SUCCESS! Gmail automation is now configured!")
        print("=" * 70)
        print()
        print(f"📧 Connected to: {email_address}")
        print(f"📊 Total messages: {profile.get('messagesTotal', 'N/A')}")
        print(f"📁 Threads total: {profile.get('threadsTotal', 'N/A')}")
        print()
        print("✅ Token saved to: gmail_token.json")
        print()
        print("Next steps:")
        print("  1. Start the server: /usr/bin/python3 -m uvicorn backend.main:app --port 8899")
        print("  2. Scan your inbox: curl -X POST http://localhost:8899/api/v1/email/scan")
        print()
        return True

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print()
        print("The token was created but Gmail API connection failed.")
        print("Please check that Gmail API is enabled in Google Cloud Console.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
