#!/usr/bin/env python3
"""Test what settings are being loaded"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.config import settings

print("=" * 60)
print("Settings Test")
print("=" * 60)
print(f"GMAIL_CREDENTIALS_FILE: {settings.GMAIL_CREDENTIALS_FILE}")
print(f"GMAIL_TOKEN_FILE: {settings.GMAIL_TOKEN_FILE}")
print(f"GMAIL_SCOPES: {settings.GMAIL_SCOPES}")
print(f"gmail_scopes_list: {settings.gmail_scopes_list}")
print("=" * 60)
