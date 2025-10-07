#!/usr/bin/env python3
"""
Test all fixed API endpoints
Validates that all the fixes are working correctly
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8899"

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def test_endpoint(method: str, path: str, data: Dict = None, expected_status: int = 200) -> tuple:
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"

    try:
        if method == "GET":
            response = requests.get(url, params=data, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=5)
        else:
            return False, f"Unsupported method: {method}"

        if response.status_code == expected_status:
            try:
                return True, response.json()
            except:
                return True, response.text
        else:
            return False, f"Status {response.status_code}: {response.text[:200]}"

    except requests.exceptions.ConnectionError:
        return False, "Connection failed - is the server running?"
    except Exception as e:
        return False, f"Error: {str(e)}"

def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print formatted test result"""
    if passed:
        print(f"{Colors.GREEN}✅ {test_name}{Colors.ENDC}")
        if details and len(str(details)) < 200:
            print(f"   {Colors.BLUE}Response preview: {str(details)[:100]}...{Colors.ENDC}")
    else:
        print(f"{Colors.RED}❌ {test_name}{Colors.ENDC}")
        print(f"   {Colors.YELLOW}Error: {details}{Colors.ENDC}")

def run_tests():
    """Run all endpoint tests"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Testing Fixed API Endpoints - {datetime.now():%Y-%m-%d %H:%M:%S}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    total_tests = 0
    passed_tests = 0

    # Test 1: Health Check
    print(f"{Colors.BOLD}1. Health Check{Colors.ENDC}")
    passed, result = test_endpoint("GET", "/health")
    print_test_result("GET /health", passed, result if passed else str(result))
    total_tests += 1
    if passed: passed_tests += 1

    # Test 2: Jobs List (Fixed schema)
    print(f"\n{Colors.BOLD}2. Jobs API (Fixed Schema){Colors.ENDC}")
    passed, result = test_endpoint("GET", "/api/v1/jobs/list", {"limit": 5})
    print_test_result("GET /api/v1/jobs/list", passed,
                      f"Found {result.get('count', 0)} jobs" if passed and isinstance(result, dict) else result)
    total_tests += 1
    if passed: passed_tests += 1

    # Test 3: Applications List (Fixed schema)
    print(f"\n{Colors.BOLD}3. Applications API{Colors.ENDC}")
    passed, result = test_endpoint("GET", "/api/v1/applications/list", {"limit": 5})
    print_test_result("GET /api/v1/applications/list", passed,
                      f"Found {result.get('count', 0)} applications" if passed and isinstance(result, dict) else result)
    total_tests += 1
    if passed: passed_tests += 1

    # Test 4: Email Stats (Fixed classification field)
    print(f"\n{Colors.BOLD}4. Email Tracking API{Colors.ENDC}")
    passed, result = test_endpoint("GET", "/api/v1/email/stats")
    print_test_result("GET /api/v1/email/stats", passed,
                      f"Tracking {result.get('total_emails', 0)} emails" if passed and isinstance(result, dict) else result)
    total_tests += 1
    if passed: passed_tests += 1

    # Test 5: Follow-ups (Fixed 'sent' field)
    print(f"\n{Colors.BOLD}5. Follow-ups API{Colors.ENDC}")
    passed, result = test_endpoint("GET", "/api/v1/follow-ups/scheduled")
    print_test_result("GET /api/v1/follow-ups/scheduled", passed,
                      f"{result.get('total_pending', 0)} pending follow-ups" if passed and isinstance(result, dict) else result)
    total_tests += 1
    if passed: passed_tests += 1

    # Test 6: Analytics Dashboard (Fixed OFFERED enum)
    print(f"\n{Colors.BOLD}6. Analytics Dashboard{Colors.ENDC}")
    passed, result = test_endpoint("GET", "/api/v1/analytics/dashboard")
    if passed and isinstance(result, dict):
        kpis = result.get('kpis', {})
        details = f"Active: {kpis.get('active_opportunities', 0)}, Weekly: {kpis.get('applications_this_week', 0)}"
    else:
        details = result
    print_test_result("GET /api/v1/analytics/dashboard", passed, details)
    total_tests += 1
    if passed: passed_tests += 1

    # Test 7: Job Stats
    print(f"\n{Colors.BOLD}7. Job Statistics{Colors.ENDC}")
    passed, result = test_endpoint("GET", "/api/v1/jobs/stats/summary")
    print_test_result("GET /api/v1/jobs/stats/summary", passed,
                      f"Active jobs: {result.get('active_jobs', 0)}" if passed and isinstance(result, dict) else result)
    total_tests += 1
    if passed: passed_tests += 1

    # Test 8: Application Stats
    print(f"\n{Colors.BOLD}8. Application Statistics{Colors.ENDC}")
    passed, result = test_endpoint("GET", "/api/v1/applications/stats")
    print_test_result("GET /api/v1/applications/stats", passed,
                      f"Total: {result.get('total_applications', 0)}, Response rate: {result.get('response_rate', '0%')}"
                      if passed and isinstance(result, dict) else result)
    total_tests += 1
    if passed: passed_tests += 1

    # Test 9: Analytics Trends
    print(f"\n{Colors.BOLD}9. Analytics Trends{Colors.ENDC}")
    passed, result = test_endpoint("GET", "/api/v1/analytics/trends", {"metric": "applications", "period": 30})
    print_test_result("GET /api/v1/analytics/trends", passed,
                      f"Analyzed {result.get('period_days', 0)} days" if passed and isinstance(result, dict) else result)
    total_tests += 1
    if passed: passed_tests += 1

    # Test 10: Performance Score
    print(f"\n{Colors.BOLD}10. Performance Score{Colors.ENDC}")
    passed, result = test_endpoint("GET", "/api/v1/analytics/performance-score")
    print_test_result("GET /api/v1/analytics/performance-score", passed,
                      f"Score: {result.get('overall_score', 0)}/100, Grade: {result.get('grade', 'N/A')}"
                      if passed and isinstance(result, dict) else result)
    total_tests += 1
    if passed: passed_tests += 1

    # Print Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Test Summary{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    if passed_tests == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}✨ ALL TESTS PASSED! {passed_tests}/{total_tests} (100%){Colors.ENDC}")
    elif passed_tests > total_tests * 0.7:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  MOSTLY PASSING: {passed_tests}/{total_tests} ({success_rate:.1f}%){Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ TESTS FAILING: {passed_tests}/{total_tests} ({success_rate:.1f}%){Colors.ENDC}")

    print(f"\n{Colors.BLUE}Server URL: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.BLUE}Test completed at: {datetime.now():%Y-%m-%d %H:%M:%S}{Colors.ENDC}\n")

    return passed_tests, total_tests

if __name__ == "__main__":
    try:
        passed, total = run_tests()
        exit(0 if passed == total else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.ENDC}")
        exit(1)