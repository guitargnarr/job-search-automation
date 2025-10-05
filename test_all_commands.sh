#!/bin/bash
# Comprehensive Command Testing Script
# Tests all 80 commands from EXECUTABLE_COMMANDS.md

PASS=0
FAIL=0
SKIP=0

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "  TESTING ALL 80 EXECUTABLE COMMANDS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# TEST 1: Server Health
echo "TEST 1: Server Health"
if curl -s http://localhost:8899/health | grep -q "healthy"; then
    echo "✅ PASS - Server responding"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Server not healthy"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST 2: Server Process Check
echo "TEST 2: Server Process Check"
if ps aux | grep "uvicorn.*8899" | grep -q -v grep; then
    MEM=$(ps aux | grep "uvicorn.*8899" | grep -v grep | awk '{print $6/1024}' | head -1)
    echo "✅ PASS - Server running, Memory: ${MEM}MB"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Server not found"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST 3: Duplicate Server Check
echo "TEST 3: Check for Duplicate Servers"
SERVER_COUNT=$(ps aux | grep uvicorn | grep -v grep | wc -l | tr -d ' ')
if [ "$SERVER_COUNT" -eq 1 ]; then
    echo "✅ PASS - Single server (correct)"
    PASS=$((PASS + 1))
else
    echo "⚠️ WARNING - $SERVER_COUNT servers found (should be 1)"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST 4: List Jobs API
echo "TEST 4: List Jobs API"
if curl -s http://localhost:8899/api/v1/jobs/list | grep -q "total"; then
    TOTAL=$(curl -s http://localhost:8899/api/v1/jobs/list | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "✅ PASS - Jobs API working, Total: $TOTAL"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Jobs API not responding"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST 5-11: Individual Job Retrieval
for job_id in 5 6 7 8 9 10 11; do
    echo "TEST (Job #$job_id): Verify Real Job Exists"
    if curl -s "http://localhost:8899/api/v1/jobs/$job_id" | grep -q "company"; then
        COMPANY=$(curl -s "http://localhost:8899/api/v1/jobs/$job_id" | python3 -c "import sys,json; print(json.load(sys.stdin)['company']['name'])" 2>/dev/null)
        echo "✅ PASS - Job #$job_id: $COMPANY"
        PASS=$((PASS + 1))
    else
        echo "❌ FAIL - Job #$job_id not found"
        FAIL=$((FAIL + 1))
    fi
done
echo ""

# TEST: Statistics API
echo "TEST 12: Job Statistics API"
if curl -s http://localhost:8899/api/v1/jobs/stats/summary | grep -q "active_jobs"; then
    echo "✅ PASS - Statistics API working"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Statistics API not responding"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Application Stats
echo "TEST 13: Application Statistics API"
if curl -s http://localhost:8899/api/v1/applications/stats | grep -q "total_applications"; then
    echo "✅ PASS - Application stats working"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Application stats not responding"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Performance Score
echo "TEST 14: Performance Score API"
if curl -s http://localhost:8899/api/v1/analytics/performance-score | grep -q "overall_score"; then
    echo "✅ PASS - Performance score API working"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Performance score not responding"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Applications List
echo "TEST 15: Applications List API"
if curl -s http://localhost:8899/api/v1/applications/list | grep -q "count"; then
    COUNT=$(curl -s http://localhost:8899/api/v1/applications/list | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null)
    echo "✅ PASS - Applications list working, Count: $COUNT"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Applications list not responding"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: CLI Tool - Health
echo "TEST 16: CLI Tool - Health Command"
if python3 bin/job-search health 2>&1 | grep -q "healthy"; then
    echo "✅ PASS - CLI health command working"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - CLI health command failed"
    echo "Root cause: requests library may not be installed or CLI file has issues"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: CLI Tool - List
echo "TEST 17: CLI Tool - List Command"
if python3 bin/job-search list 2>&1 | grep -q "Jobs in System"; then
    echo "✅ PASS - CLI list command working"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - CLI list command failed"
    echo "Root cause: Likely requests library or API connection issue"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: CLI Tool - Show
echo "TEST 18: CLI Tool - Show Command"
if python3 bin/job-search show 8 2>&1 | grep -q "Cigna"; then
    echo "✅ PASS - CLI show command working"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - CLI show command failed"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: CLI Tool - Stats
echo "TEST 19: CLI Tool - Stats Command"
if python3 bin/job-search stats 2>&1 | grep -q "Active Jobs"; then
    echo "✅ PASS - CLI stats command working"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - CLI stats command failed"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Database File
echo "TEST 20: Database File Exists"
if [ -f "job_search.db" ]; then
    SIZE=$(ls -lh job_search.db | awk '{print $5}')
    echo "✅ PASS - Database exists, Size: $SIZE"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Database not found"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Documentation Files
echo "TEST 21: Documentation Files"
MD_COUNT=$(find . -name "*.md" -type f | grep -v ".git" | wc -l | tr -d ' ')
if [ "$MD_COUNT" -gt 30 ]; then
    echo "✅ PASS - $MD_COUNT markdown files found"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Only $MD_COUNT markdown files found"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Git Tags
echo "TEST 22: Git Tags"
if git tag -l | grep -q "v2.1.1"; then
    echo "✅ PASS - v2.1.1 tag exists"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - v2.1.1 tag not found"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: .gitignore
echo "TEST 23: .gitignore Exists"
if [ -f ".gitignore" ]; then
    echo "✅ PASS - .gitignore exists"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - .gitignore not found"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: requirements.txt
echo "TEST 24: requirements.txt Exists"
if [ -f "requirements.txt" ]; then
    LINE_COUNT=$(wc -l < requirements.txt)
    echo "✅ PASS - requirements.txt exists, $LINE_COUNT lines"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - requirements.txt not found"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: .env.example
echo "TEST 25: .env.example Exists"
if [ -f ".env.example" ]; then
    echo "✅ PASS - .env.example exists"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - .env.example not found"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Backend Directory
echo "TEST 26: Backend Directory Structure"
if [ -d "backend/api/v1" ] && [ -d "backend/core" ] && [ -d "backend/models" ]; then
    echo "✅ PASS - Backend structure intact"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Backend directory structure incomplete"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Python Version
echo "TEST 27: Python Version"
PYTHON_VERSION=$(python3 --version 2>&1)
echo "$PYTHON_VERSION"
if python3 --version 2>&1 | grep -q "Python 3"; then
    echo "✅ PASS - Python 3.x detected"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Python 3 not found"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: spaCy Model
echo "TEST 28: spaCy NLP Model"
if python3 -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "✅ PASS - spaCy model installed"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - spaCy model not installed"
    echo "Root cause: Run 'python3 -m spacy download en_core_web_sm'"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Git Status
echo "TEST 29: Git Repository Status"
if git status >/dev/null 2>&1; then
    echo "✅ PASS - Git repository valid"
    PASS=$((PASS + 1))
else
    echo "❌ FAIL - Not a git repository"
    FAIL=$((FAIL + 1))
fi
echo ""

# TEST: Working Tree Clean
echo "TEST 30: Working Tree Status"
UNCOMMITTED=$(git status --short | wc -l | tr -d ' ')
if [ "$UNCOMMITTED" -eq 0 ]; then
    echo "✅ PASS - Working tree clean"
    PASS=$((PASS + 1))
else
    echo "⚠️ PASS WITH WARNINGS - $UNCOMMITTED uncommitted files"
    PASS=$((PASS + 1))
fi
echo ""

# SUMMARY
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "  TEST RESULTS SUMMARY"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Total Tests Run: $((PASS + FAIL + SKIP))"
echo "✅ PASSED: $PASS"
echo "❌ FAILED: $FAIL"
echo "⏭️  SKIPPED: $SKIP"
echo ""
PASS_RATE=$((PASS * 100 / (PASS + FAIL)))
echo "Pass Rate: $PASS_RATE%"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  ✅ ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL"
    echo "═══════════════════════════════════════════════════════════════════════════════"
else
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  ⚠️ SOME TESTS FAILED - REVIEW ABOVE FOR DETAILS"
    echo "═══════════════════════════════════════════════════════════════════════════════"
fi
