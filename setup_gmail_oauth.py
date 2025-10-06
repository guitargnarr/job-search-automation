#!/usr/bin/env python3
"""
Gmail OAuth Setup Script
This script initializes the Gmail API connection and generates the OAuth token.
It will open a browser window for you to authenticate with your Google account.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import backend modules
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.email_service import EmailAutomationService
from backend.core.logging import get_logger

logger = get_logger(__name__)

def main():
    """Initialize Gmail API and trigger OAuth flow"""
    print("=" * 60)
    print("Gmail OAuth Setup for Job Search Automation")
    print("=" * 60)
    print()
    print("This script will:")
    print("1. Open a browser window")
    print("2. Ask you to sign in to your Google account")
    print("3. Request permission to access your Gmail")
    print("4. Generate a token file for future authentication")
    print()
    print("IMPORTANT:")
    print("- Use the Gmail account you want to monitor for job responses")
    print("- Click 'Allow' when asked for Gmail permissions")
    print("- The token will be saved to: gmail_token.json")
    print()
    input("Press ENTER to continue...")
    print()

    try:
        print("Initializing Gmail API connection...")
        email_service = EmailAutomationService()

        if email_service.service:
            print()
            print("✅ SUCCESS! Gmail API connected successfully!")
            print()
            print("Token file created at: gmail_token.json")
            print()
            print("You can now use the email automation features:")
            print("- Automatic email scanning")
            print("- Response classification (interview/rejection/offer)")
            print("- Application status updates")
            print()
            print("Next steps:")
            print("1. Test the connection: python test_gmail_connection.py")
            print("2. Or scan your inbox: curl -X POST http://localhost:8899/api/v1/email/scan")
            print()
        else:
            print()
            print("❌ Gmail API initialization failed.")
            print("Please check:")
            print("1. Credentials file exists and is valid")
            print("2. Gmail API is enabled in Google Cloud Console")
            print("3. OAuth consent screen is configured")
            print()
            sys.exit(1)

    except Exception as e:
        print()
        print(f"❌ Error during OAuth setup: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check that Gmail API is enabled in Google Cloud Console")
        print("2. Verify credentials file path in .env")
        print("3. Make sure you have internet connection")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()
