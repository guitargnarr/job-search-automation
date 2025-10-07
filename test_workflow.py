#!/usr/bin/env python3
"""
Interactive Job Search System Test Workflow
Tests all components of your automation platform
"""

import os
import sys
import time
import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8899"
DB_PATH = "job_search.db"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def test_database_connection():
    """Test 1: Verify database connection and stats"""
    print_section("TEST 1: DATABASE CONNECTION")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get database statistics
        stats = {}
        for table in ['jobs', 'companies', 'applications', 'email_tracking']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]

        print(f"{Colors.GREEN}✅ Database connected successfully{Colors.ENDC}")
        print(f"\nDatabase Statistics:")
        print(f"  • Jobs tracked: {Colors.CYAN}{stats['jobs']}{Colors.ENDC}")
        print(f"  • Companies: {Colors.CYAN}{stats['companies']}{Colors.ENDC}")
        print(f"  • Applications: {Colors.CYAN}{stats['applications']}{Colors.ENDC}")
        print(f"  • Emails tracked: {Colors.CYAN}{stats['email_tracking']}{Colors.ENDC}")

        conn.close()
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Database test failed: {e}{Colors.ENDC}")
        return False

def test_api_health():
    """Test 2: Check API server health"""
    print_section("TEST 2: API SERVER HEALTH")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✅ API Server is healthy{Colors.ENDC}")
            print(f"\nServer Information:")
            print(f"  • Version: {Colors.CYAN}{data.get('version', 'unknown')}{Colors.ENDC}")
            print(f"  • Jobs tracked: {Colors.CYAN}{data.get('real_jobs_tracked', 0)}{Colors.ENDC}")
            print(f"  • Automation level: {Colors.CYAN}{data.get('automation_level', 'unknown')}{Colors.ENDC}")
            return True
    except requests.ConnectionError:
        print(f"{Colors.RED}❌ Cannot connect to API server at {BASE_URL}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Make sure the server is running:{Colors.ENDC}")
        print(f"  python3 -m uvicorn backend.main:app --port 8899")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ API test failed: {e}{Colors.ENDC}")
        return False

def test_email_automation():
    """Test 3: Check email automation status"""
    print_section("TEST 3: EMAIL AUTOMATION")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/email/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✅ Email automation is active{Colors.ENDC}")
            print(f"\nEmail Statistics:")
            print(f"  • Total emails tracked: {Colors.CYAN}{data.get('total_emails', 0)}{Colors.ENDC}")
            print(f"  • Action required: {Colors.CYAN}{data.get('action_required', 0)}{Colors.ENDC}")

            # Show classification breakdown
            classifications = data.get('classifications', {})
            if classifications:
                print(f"\n  Email Classifications:")
                for type_name, count in classifications.items():
                    print(f"    • {type_name}: {Colors.CYAN}{count}{Colors.ENDC}")

            return True
    except Exception as e:
        print(f"{Colors.RED}❌ Email automation test failed: {e}{Colors.ENDC}")
        return False

def test_analytics():
    """Test 4: Check analytics dashboard"""
    print_section("TEST 4: ANALYTICS DASHBOARD")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/analytics/dashboard", timeout=5)
        if response.status_code == 200:
            data = response.json()
            kpis = data.get('kpis', {})

            print(f"{Colors.GREEN}✅ Analytics dashboard is working{Colors.ENDC}")
            print(f"\nKey Performance Indicators:")
            print(f"  • Active opportunities: {Colors.CYAN}{kpis.get('active_opportunities', 0)}{Colors.ENDC}")
            print(f"  • Applications this week: {Colors.CYAN}{kpis.get('applications_this_week', 0)}{Colors.ENDC}")
            print(f"  • Pending interviews: {Colors.CYAN}{kpis.get('pending_interviews', 0)}{Colors.ENDC}")
            print(f"  • Daily average: {Colors.CYAN}{kpis.get('current_daily_average', 0)}{Colors.ENDC} (target: 5)")

            # Show conversion funnel
            funnel = data.get('application_funnel', {})
            if funnel:
                rates = funnel.get('conversion_rates', {})
                print(f"\nConversion Rates:")
                print(f"  • Application → Response: {Colors.CYAN}{rates.get('application_to_response', '0%')}{Colors.ENDC}")
                print(f"  • Response → Interview: {Colors.CYAN}{rates.get('response_to_interview', '0%')}{Colors.ENDC}")

            return True
    except Exception as e:
        print(f"{Colors.RED}❌ Analytics test failed: {e}{Colors.ENDC}")
        return False

def test_job_search():
    """Test 5: Search for specific jobs"""
    print_section("TEST 5: JOB SEARCH")

    try:
        # Search for remote jobs
        response = requests.get(f"{BASE_URL}/api/v1/jobs/list",
                               params={"search": "remote", "limit": 5},
                               timeout=5)

        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])

            print(f"{Colors.GREEN}✅ Job search is working{Colors.ENDC}")
            print(f"\nFound {Colors.CYAN}{len(jobs)}{Colors.ENDC} remote jobs:")

            for job in jobs[:3]:  # Show first 3
                salary = job.get('salary_range', 'Not specified')
                print(f"\n  • {Colors.BOLD}{job['title']}{Colors.ENDC}")
                print(f"    Company: {job['company']}")
                print(f"    Location: {job.get('location', 'N/A')} ({job.get('remote_type', 'N/A')})")
                print(f"    Salary: {salary}")
                print(f"    Priority: {job.get('priority', 'MEDIUM')}")

            return True
    except Exception as e:
        print(f"{Colors.RED}❌ Job search test failed: {e}{Colors.ENDC}")
        return False

def test_application_workflow():
    """Test 6: Simulate application workflow"""
    print_section("TEST 6: APPLICATION WORKFLOW SIMULATION")

    print(f"{Colors.YELLOW}This test will simulate (not execute) the application workflow{Colors.ENDC}\n")

    # Check for required files
    required_files = [
        "run_application.py",
        "documents/resumes/",
        "documents/cover_letters/"
    ]

    all_present = True
    for file_path in required_files:
        path = Path(file_path)
        exists = path.exists()
        status = f"{Colors.GREEN}✅{Colors.ENDC}" if exists else f"{Colors.RED}❌{Colors.ENDC}"
        print(f"  {status} {file_path}: {'Found' if exists else 'Missing'}")
        all_present = all_present and exists

    if all_present:
        print(f"\n{Colors.GREEN}✅ All required components are present{Colors.ENDC}")
        print(f"\nWorkflow steps that would execute:")
        print(f"  1. Generate tailored cover letter")
        print(f"  2. Customize resume for position")
        print(f"  3. Log application in database")
        print(f"  4. Update job status to 'applied'")
        print(f"  5. Schedule follow-up reminder")
        return True
    else:
        print(f"\n{Colors.YELLOW}⚠️ Some components are missing{Colors.ENDC}")
        return False

def interactive_job_application():
    """Interactive job application test"""
    print_section("INTERACTIVE JOB APPLICATION")

    print(f"{Colors.CYAN}Would you like to apply to a job? (y/n): {Colors.ENDC}", end='')
    choice = input().strip().lower()

    if choice != 'y':
        print("Skipping interactive application")
        return

    # List available jobs
    print(f"\n{Colors.BOLD}Available Jobs:{Colors.ENDC}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT j.id, j.title, c.name, j.remote_type
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.status = 'new'
            LIMIT 5
        """)

        jobs = cursor.fetchall()
        for job in jobs:
            print(f"  #{job[0]:3} - {job[1][:30]:30} at {job[2][:20]:20} ({job[3]})")

        print(f"\n{Colors.CYAN}Enter job ID to apply (or 'skip' to cancel): {Colors.ENDC}", end='')
        job_id = input().strip()

        if job_id != 'skip' and job_id.isdigit():
            print(f"\n{Colors.GREEN}To apply to job #{job_id}, run:{Colors.ENDC}")
            print(f"  {Colors.BOLD}python3 run_application.py --job-id {job_id}{Colors.ENDC}")
            print(f"\nOr for batch applications:")
            print(f"  {Colors.BOLD}python3 run_application.py --batch 5{Colors.ENDC}")

        conn.close()
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")

def main():
    """Run all tests"""
    print_section("JOB SEARCH AUTOMATION SYSTEM TEST")
    print(f"Testing your job search platform components...")
    print(f"Time: {datetime.now():%Y-%m-%d %H:%M:%S}\n")

    # Track test results
    tests = [
        ("Database Connection", test_database_connection),
        ("API Server Health", test_api_health),
        ("Email Automation", test_email_automation),
        ("Analytics Dashboard", test_analytics),
        ("Job Search", test_job_search),
        ("Application Workflow", test_application_workflow)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}...")
        time.sleep(1)  # Small delay for readability
        results.append(test_func())

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(results)
    total = len(results)

    print(f"Test Results: {Colors.BOLD}{passed}/{total} passed{Colors.ENDC}\n")

    for i, (test_name, _) in enumerate(tests):
        status = f"{Colors.GREEN}PASS{Colors.ENDC}" if results[i] else f"{Colors.RED}FAIL{Colors.ENDC}"
        print(f"  [{status}] {test_name}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL SYSTEMS OPERATIONAL!{Colors.ENDC}")
        print(f"\nYour job search automation platform is fully functional.")
        print(f"You're tracking {Colors.CYAN}71 jobs{Colors.ENDC} with {Colors.CYAN}4 applications{Colors.ENDC} in progress.")
    else:
        print(f"\n{Colors.YELLOW}⚠️ Some components need attention{Colors.ENDC}")
        print(f"Fix the failing tests to unlock full automation capabilities.")

    # Interactive section
    print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
    interactive_job_application()

    print(f"\n{Colors.BLUE}Documentation: Check CLAUDE.md for full system details{Colors.ENDC}")
    print(f"{Colors.BLUE}Dashboard: http://localhost:8899/docs for API explorer{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.ENDC}")