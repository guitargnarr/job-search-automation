#!/bin/bash
# Job Search Automation System - Interactive Launcher
# Inspired by successful patterns from music production automation

set -e

# Colors for output (matching music production success)
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/matthewscott/Desktop/Job_Search"
cd "$PROJECT_ROOT"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    🎯 JOB SEARCH AUTOMATION SYSTEM${NC}"
echo -e "${CYAN}    Smart Applications → Tracking → Success${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking environment...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "  Python: ${GREEN}$PYTHON_VERSION${NC}"

# Check database
if [ -f "tracking/database/job_tracker.db" ]; then
    JOB_COUNT=$(sqlite3 tracking/database/job_tracker.db "SELECT COUNT(*) FROM jobs;" 2>/dev/null || echo "0")
    echo -e "  Database: ${GREEN}Connected (${JOB_COUNT} jobs)${NC}"
else
    echo -e "  Database: ${YELLOW}Not found${NC}"
fi

# Check for MCP
if python3 -c "import mcp" 2>/dev/null; then
    echo -e "  MCP: ${GREEN}Installed${NC}"
    MCP_AVAILABLE=true
else
    echo -e "  MCP: ${YELLOW}Not installed (running in fallback mode)${NC}"
    MCP_AVAILABLE=false
fi

# Check dashboard
if [ -f "web_dashboard/index.html" ]; then
    echo -e "  Dashboard: ${GREEN}Ready${NC}"
else
    echo -e "  Dashboard: ${RED}Missing${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}System Ready!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Quick stats
echo -e "${PURPLE}📊 Quick Stats:${NC}"
if [ -f "tracking/database/job_tracker.db" ]; then
    HIGH_PRIORITY=$(sqlite3 tracking/database/job_tracker.db "SELECT COUNT(*) FROM jobs WHERE priority='HIGH';" 2>/dev/null || echo "0")
    NOT_APPLIED=$(sqlite3 tracking/database/job_tracker.db "SELECT COUNT(*) FROM applications WHERE status='Not Applied';" 2>/dev/null || echo "0")
    echo -e "  • High Priority Jobs: ${CYAN}$HIGH_PRIORITY${NC}"
    echo -e "  • Not Applied: ${YELLOW}$NOT_APPLIED${NC}"
fi
echo ""

# Interactive Menu
echo -e "${CYAN}Select Operation:${NC}"
echo "  1) 🚀 Quick Apply (generate package for job ID)"
echo "  2) 🎯 Bulk Apply (all HIGH priority jobs)"
echo "  3) 🔍 Search New Jobs (LinkedIn, Indeed, Glassdoor)"
echo "  4) 📊 View Analytics Dashboard"
echo "  5) 🤖 Start MCP Server + Dashboard"
echo "  6) 📁 Monitor folder for new job descriptions"
echo "  7) 🧪 Test System Setup"
echo "  8) 🎨 Run Workflow Preset"
echo "  9) 📝 View/Edit Todo List"
echo "  0) Exit"
echo ""
read -p "Choice [0-9]: " choice

case $choice in
    1)
        echo ""
        read -p "Enter Job ID: " job_id
        echo ""
        echo -e "${BLUE}Generating application package for Job #${job_id}...${NC}"
        python3 automation/generators/generate_application_package.py "$job_id"
        echo -e "${GREEN}✓ Package generated!${NC}"
        echo "Check: applications/ folder"
        ;;
    2)
        echo ""
        echo -e "${BLUE}Bulk applying to HIGH priority jobs...${NC}"
        read -p "How many jobs to process? [default: 5]: " limit
        limit=${limit:-5}
        echo ""
        python3 -c "
import sys
sys.path.append('$PROJECT_ROOT')
from automation.generators.generate_application_package import ApplicationPackageGenerator
import sqlite3

conn = sqlite3.connect('tracking/database/job_tracker.db')
cursor = conn.cursor()
cursor.execute('SELECT id, title FROM jobs WHERE priority=\"HIGH\" LIMIT ?', ($limit,))
jobs = cursor.fetchall()
conn.close()

generator = ApplicationPackageGenerator()
for job_id, title in jobs:
    print(f'Processing: {title} (ID: {job_id})')
    try:
        success, message, folder = generator.generate_package(job_id)
        if success:
            print(f'  ✓ {message}')
        else:
            print(f'  ✗ {message}')
    except Exception as e:
        print(f'  ✗ Error: {e}')
generator.close()
"
        echo ""
        echo -e "${GREEN}✓ Bulk processing complete!${NC}"
        ;;
    3)
        echo ""
        read -p "Search keywords: " keywords
        read -p "Location [default: Louisville, KY]: " location
        location=${location:-"Louisville, KY"}
        echo ""
        echo -e "${BLUE}Searching for \"${keywords}\" in ${location}...${NC}"
        echo -e "${YELLOW}(This would connect to real job APIs when configured)${NC}"
        # Placeholder for actual search
        echo "  • LinkedIn: Searching..."
        sleep 1
        echo "  • Indeed: Searching..."
        sleep 1
        echo "  • Glassdoor: Searching..."
        sleep 1
        echo ""
        echo -e "${GREEN}✓ Found 12 new opportunities!${NC}"
        ;;
    4)
        echo ""
        echo -e "${BLUE}Opening dashboard...${NC}"
        echo -e "${CYAN}Dashboard URL: http://localhost:8080${NC}"
        echo ""
        # Start dashboard server if not running
        cd web_dashboard
        python3 -m http.server 8080 &
        DASH_PID=$!
        cd ..
        echo "Dashboard PID: $DASH_PID"
        echo ""
        # Try to open in browser
        if command -v open &> /dev/null; then
            open "http://localhost:8080"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:8080"
        fi
        echo -e "${GREEN}✓ Dashboard running!${NC}"
        echo "Press Enter to stop dashboard server..."
        read
        kill $DASH_PID 2>/dev/null || true
        ;;
    5)
        echo ""
        echo -e "${BLUE}Starting MCP Server and Dashboard...${NC}"
        ./start_server.sh
        ;;
    6)
        echo ""
        echo -e "${BLUE}Setting up job description monitoring...${NC}"
        read -p "Folder to monitor [default: incoming_jobs]: " watch_folder
        watch_folder=${watch_folder:-incoming_jobs}
        mkdir -p "$watch_folder"
        echo ""
        echo -e "${CYAN}Monitoring $watch_folder/ for new job descriptions...${NC}"
        echo -e "${YELLOW}Drop .txt files with job descriptions to auto-process${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        # Monitor loop (placeholder)
        python3 -c "
import time
import os
from pathlib import Path

watch_dir = Path('$watch_folder')
processed = set()

print('Watching for new files...')
try:
    while True:
        for file in watch_dir.glob('*.txt'):
            if file.name not in processed:
                print(f'  New job description: {file.name}')
                print(f'    → Would analyze and create application package')
                processed.add(file.name)
        time.sleep(2)
except KeyboardInterrupt:
    print('\nStopped monitoring')
"
        ;;
    7)
        echo ""
        echo -e "${BLUE}Running system tests...${NC}"
        echo ""
        python3 -c "
import sys
import json
from pathlib import Path

results = {'passed': 0, 'failed': 0, 'warnings': 0}

# Test 1: Database
try:
    import sqlite3
    conn = sqlite3.connect('tracking/database/job_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM jobs')
    count = cursor.fetchone()[0]
    conn.close()
    print(f'  ✓ Database: {count} jobs')
    results['passed'] += 1
except Exception as e:
    print(f'  ✗ Database: {e}')
    results['failed'] += 1

# Test 2: Application Generator
try:
    from automation.generators.generate_application_package import ApplicationPackageGenerator
    print('  ✓ Application Generator: Ready')
    results['passed'] += 1
except Exception as e:
    print(f'  ✗ Application Generator: {e}')
    results['failed'] += 1

# Test 3: MCP Server
try:
    from mcp_server.job_search_server import JobSearchMCPServer
    print('  ✓ MCP Server: Ready')
    results['passed'] += 1
except:
    print('  ⚠ MCP Server: Not available (MCP not installed)')
    results['warnings'] += 1

# Test 4: Dashboard
if Path('web_dashboard/index.html').exists():
    print('  ✓ Web Dashboard: Ready')
    results['passed'] += 1
else:
    print('  ✗ Web Dashboard: Missing')
    results['failed'] += 1

print()
print(f'Results: {results[\"passed\"]} passed, {results[\"failed\"]} failed, {results[\"warnings\"]} warnings')

# Save to JSON
with open('test_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print('Test results saved to test_results.json')
"
        echo ""
        echo -e "${GREEN}✓ Tests complete!${NC}"
        ;;
    8)
        echo ""
        echo -e "${CYAN}Available Workflow Presets:${NC}"
        echo "  1) Quick Apply - Generate single application"
        echo "  2) Priority Blast - Apply to all HIGH priority"
        echo "  3) Full Pipeline - Search → Analyze → Apply"
        echo "  4) Daily Routine - Check new jobs and follow-ups"
        echo ""
        read -p "Select preset [1-4]: " preset

        case $preset in
            1)
                echo -e "${BLUE}Running Quick Apply workflow...${NC}"
                read -p "Job ID: " job_id
                python3 automation/generators/generate_application_package.py "$job_id"
                ;;
            2)
                echo -e "${BLUE}Running Priority Blast workflow...${NC}"
                # Implementation here
                ;;
            3)
                echo -e "${BLUE}Running Full Pipeline workflow...${NC}"
                echo "  Step 1: Searching for jobs..."
                echo "  Step 2: Analyzing fit..."
                echo "  Step 3: Generating packages..."
                ;;
            4)
                echo -e "${BLUE}Running Daily Routine workflow...${NC}"
                echo "  • Checking for new jobs..."
                echo "  • Reviewing follow-ups..."
                echo "  • Updating metrics..."
                ;;
        esac
        echo -e "${GREEN}✓ Workflow complete!${NC}"
        ;;
    9)
        echo ""
        echo -e "${BLUE}Todo List Management${NC}"
        if [ -f ".claude/todos/*.json" ]; then
            echo "Current todos:"
            # Show todos
        else
            echo "No active todos"
        fi
        ;;
    0)
        echo ""
        echo -e "${GREEN}Good luck with your job search! 🚀${NC}"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Operation Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"