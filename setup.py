#!/usr/bin/env python3
"""
Setup script for Job Search Automation Platform
Run this to install dependencies and configure the system
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    print("\n" + "="*60)
    print("🚀 JOB SEARCH AUTOMATION PLATFORM SETUP")
    print("Real automation that actually saves time")
    print("="*60 + "\n")

def check_python_version():
    """Ensure Python 3.8+ is installed"""
    print("📍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. You have: " + sys.version)
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected\n")

def install_requirements():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        # First, ensure pip is up to date
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

        # Install main requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

        # Install additional requirements for local development
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiosqlite", "python-multipart"])

        print("✅ Dependencies installed successfully\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Try running: pip install -r requirements.txt manually")
        sys.exit(1)

def download_spacy_model():
    """Download spaCy language model"""
    print("🧠 Downloading NLP model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✅ NLP model downloaded\n")
    except subprocess.CalledProcessError:
        print("⚠️  Failed to download spaCy model. Run: python -m spacy download en_core_web_sm")

def setup_directories():
    """Create necessary directories"""
    print("📁 Creating directory structure...")

    directories = [
        Path.home() / ".credentials",  # For API credentials
        Path("logs"),
        Path("data"),
        Path("backend/api/v1"),
        Path("backend/core"),
        Path("backend/models"),
        Path("backend/services"),
        Path("backend/tasks"),
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    print("✅ Directories created\n")

def create_env_file():
    """Create .env file template"""
    print("🔐 Creating environment configuration...")

    env_path = Path(".env")
    if env_path.exists():
        print("⚠️  .env file already exists, skipping...")
        return

    env_template = """# Job Search Automation Platform Configuration
# Copy this to .env and fill in your values

# Security
SECRET_KEY=your-secret-key-change-this-in-production

# Database (SQLite for local, PostgreSQL for production)
DATABASE_URL=sqlite:///./job_automation.db

# Gmail API (for email tracking)
GMAIL_CREDENTIALS_FILE=/Users/your-username/.credentials/gmail_credentials.json
GMAIL_TOKEN_FILE=/Users/your-username/.credentials/gmail_token.json

# LinkedIn Automation
LINKEDIN_EMAIL=your-linkedin-email@example.com
LINKEDIN_PASSWORD=your-linkedin-password

# OpenAI (for AI-powered features)
OPENAI_API_KEY=sk-your-openai-api-key

# Job Search Settings
JOB_SEARCH_LOCATION=Louisville, KY
JOB_SEARCH_RADIUS=50

# Redis (for task queue - optional for local dev)
REDIS_URL=redis://localhost:6379
"""

    with open(env_path, 'w') as f:
        f.write(env_template)

    print("✅ Created .env template - PLEASE EDIT WITH YOUR VALUES\n")

def setup_gmail_api():
    """Guide user through Gmail API setup"""
    print("📧 Gmail API Setup Instructions:")
    print("""
1. Go to: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable Gmail API:
   - Go to 'APIs & Services' > 'Library'
   - Search for 'Gmail API'
   - Click 'Enable'
4. Create credentials:
   - Go to 'APIs & Services' > 'Credentials'
   - Click 'Create Credentials' > 'OAuth client ID'
   - Choose 'Desktop app'
   - Download the JSON file
5. Save the JSON file as: ~/.credentials/gmail_credentials.json

Press Enter when complete...
""")
    input()

def create_run_script():
    """Create script to run the application"""
    print("🏃 Creating run script...")

    run_script = """#!/bin/bash
# Run the Job Search Automation Platform

echo "🚀 Starting Job Search Automation Platform..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the FastAPI server
echo "Starting API server..."
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "✅ API running at: http://localhost:8000"
echo "📊 API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop..."

# Wait for interrupt
trap "kill $API_PID; exit" INT
wait
"""

    script_path = Path("run.sh")
    with open(script_path, 'w') as f:
        f.write(run_script)

    # Make executable
    os.chmod(script_path, 0o755)

    print("✅ Run script created: ./run.sh\n")

def initialize_database():
    """Initialize the database with tables"""
    print("🗄️  Initializing database...")

    try:
        # Import and create tables
        from backend.core.database import engine, Base
        from backend.models import models  # Import to register models

        # Use sync engine for setup
        from sqlalchemy import create_engine
        sync_engine = create_engine("sqlite:///./job_automation.db")

        Base.metadata.create_all(bind=sync_engine)

        print("✅ Database initialized\n")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("The database will be created on first run\n")

def test_imports():
    """Test that core modules import correctly"""
    print("🧪 Testing imports...")

    modules_to_test = [
        "backend.main",
        "backend.core.config",
        "backend.services.email_service",
        "backend.services.ats_optimizer",
        "backend.services.linkedin_service",
    ]

    for module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")

    print()

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("""
Next Steps:

1. Edit .env file with your credentials:
   - Add Gmail API credentials
   - Add LinkedIn login (optional)
   - Add OpenAI API key (optional)

2. Set up Gmail API (if not done):
   - Follow instructions above
   - Run first email scan to authorize

3. Start the application:
   ./run.sh

4. Access the system:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

5. Run your first automation:
   - Email scanning: http://localhost:8000/api/v1/email/scan
   - ATS optimization: Upload resume via API
   - LinkedIn campaign: Configure and run

Remember: This system now provides REAL automation, not just file copying!
""")

def main():
    """Run complete setup"""
    print_header()

    # Run setup steps
    check_python_version()
    install_requirements()
    download_spacy_model()
    setup_directories()
    create_env_file()
    create_run_script()
    initialize_database()
    test_imports()

    # Gmail setup guide
    print("\n📧 Gmail API Setup Required!")
    print("Have you set up Gmail API credentials? (y/n): ", end="")
    response = input().lower()
    if response != 'y':
        setup_gmail_api()

    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)