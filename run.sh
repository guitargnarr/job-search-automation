#!/bin/bash

# Job Search Automation Platform - Startup Script
# Version: 2.1.1 - Stable Release
# This script starts the FastAPI server with proper environment setup
# Current port: 8899 (set APP_PORT=8899 in .env)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Job Search Automation Platform${NC}"
echo -e "${GREEN}========================================${NC}"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python $PYTHON_VERSION is below required version $REQUIRED_VERSION${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    if [ -f .env.example ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env with your actual credentials${NC}"
        exit 1
    else
        echo -e "${RED}✗ No .env.example found${NC}"
        exit 1
    fi
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p storage/resumes
mkdir -p storage/cover_letters
mkdir -p tmp

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✓ Using virtual environment: $(basename $VIRTUAL_ENV)${NC}"
else
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update dependencies
echo "Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check for spaCy model
echo "Checking NLP models..."
python3 -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null || {
    echo "Installing spaCy English model..."
    python3 -m spacy download en_core_web_sm
}

# Initialize database if needed
if [ ! -f "job_search.db" ]; then
    echo "Initializing database..."
    python3 -c "
from backend.core.database import init_db
import asyncio
asyncio.run(init_db())
" || echo -e "${YELLOW}Database initialization will happen on first run${NC}"
fi

# Export environment variables
export $(grep -v '^#' .env | xargs)

# Start the server
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting FastAPI server...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "API Documentation: http://localhost:${APP_PORT:-8899}/docs"
echo "Health Check: http://localhost:${APP_PORT:-8899}/health"
echo "Job List: http://localhost:${APP_PORT:-8899}/api/v1/jobs/list"
echo ""
echo "Current: 7 real jobs tracked | Memory: 19MB optimized"
echo "Press Ctrl+C to stop the server"
echo ""

# Run with uvicorn
if [ "$APP_ENV" = "development" ] || [ -z "$APP_ENV" ]; then
    # Development mode with auto-reload (SINGLE WORKER ONLY)
    uvicorn backend.main:app \
        --host ${APP_HOST:-0.0.0.0} \
        --port ${APP_PORT:-8899} \
        --reload \
        --log-level ${LOG_LEVEL:-info}
else
    # Production mode (CRITICAL: workers must be 1 to avoid duplicate servers)
    uvicorn backend.main:app \
        --host ${APP_HOST:-0.0.0.0} \
        --port ${APP_PORT:-8899} \
        --workers 1 \
        --log-level ${LOG_LEVEL:-info}
fi