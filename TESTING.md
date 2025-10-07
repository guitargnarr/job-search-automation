# Testing Protocol - Job Search Automation Platform

## Overview
Comprehensive testing procedures to validate system functionality and ensure reliability.

## Quick Test Commands

```bash
# 1. Full System Test (Recommended)
python test_workflow.py

# 2. API Endpoint Test
python test_fixed_endpoints.py

# 3. Single Application Test
python run_application.py --job-id 69

# 4. Health Check
curl http://localhost:8899/health
```

## Test Categories

### 1. System Health Tests

**Purpose**: Verify core system components are operational

```bash
# Database connectivity
sqlite3 job_search.db "SELECT COUNT(*) FROM jobs;"

# Server health
curl http://localhost:8899/health

# Expected: {"status": "healthy", "version": "2.2.0"}
```

### 2. API Endpoint Tests

**Test All 30 Endpoints**:
```bash
python test_fixed_endpoints.py
```

**Expected Output**: 10/10 tests passing (100%)

**Manual API Tests**:
```bash
# Jobs API
curl "http://localhost:8899/api/v1/jobs/list?limit=5"

# Applications API
curl http://localhost:8899/api/v1/applications/list

# Email API
curl http://localhost:8899/api/v1/email/stats

# Analytics API
curl http://localhost:8899/api/v1/analytics/dashboard

# Follow-ups API
curl http://localhost:8899/api/v1/follow-ups/scheduled

# ATS API (requires file upload)
# Test via http://localhost:8899/docs
```

### 3. Database Integrity Tests

```bash
# Check table counts
sqlite3 job_search.db <<EOF
SELECT 'Jobs: ' || COUNT(*) FROM jobs;
SELECT 'Companies: ' || COUNT(*) FROM companies;
SELECT 'Applications: ' || COUNT(*) FROM applications;
SELECT 'Emails: ' || COUNT(*) FROM email_tracking;
EOF

# Verify integrity
sqlite3 job_search.db "PRAGMA integrity_check;"
# Expected: ok

# Check for orphaned records
sqlite3 job_search.db "SELECT COUNT(*) FROM applications WHERE job_id NOT IN (SELECT id FROM jobs);"
# Expected: 0
```

### 4. Email Automation Tests

```bash
# Test email scanning
curl -X POST http://localhost:8899/api/v1/email/scan \
  -H "Content-Type: application/json" \
  -d '{"days_back": 7}'

# Verify email stats
curl http://localhost:8899/api/v1/email/stats

# Expected: total_emails > 0, classifications present
```

### 5. Document Generation Tests

```bash
# Test document creation
python run_application.py --job-id 69

# Verify files created
ls -lh documents/cover_letters/sent/ | tail -3
ls -lh documents/resumes/tailored/ | tail -3

# Check file sizes (should be > 0 bytes)
find documents/ -name "*.txt" -size 0
# Expected: no output (no empty files)
```

### 6. Application Workflow Tests

```bash
# Test complete workflow
python test_workflow.py

# Expected components:
# ✅ Database Connection
# ✅ API Server Health
# ✅ Email Automation
# ✅ Analytics Dashboard
# ✅ Job Search
# ✅ Application Workflow
```

## Regression Testing

**Run before making changes**:
```bash
# 1. Backup database
cp job_search.db job_search_backup_$(date +%Y%m%d).db

# 2. Run full test suite
python test_fixed_endpoints.py
python test_workflow.py

# 3. Test critical path
python run_application.py --list
curl http://localhost:8899/api/v1/analytics/dashboard
```

## Performance Testing

### Response Time Tests
```bash
# Test API response times (should be < 100ms)
time curl -s http://localhost:8899/health
time curl -s http://localhost:8899/api/v1/jobs/list
time curl -s http://localhost:8899/api/v1/analytics/dashboard
```

### Load Testing
```bash
# Send 100 requests
for i in {1..100}; do
  curl -s http://localhost:8899/health > /dev/null
done
# Monitor server logs for errors
```

### Database Performance
```bash
# Query performance
sqlite3 job_search.db <<EOF
.timer on
SELECT * FROM jobs WHERE status='new' ORDER BY priority DESC LIMIT 10;
SELECT COUNT(*) FROM applications;
EOF
# Should complete in < 10ms
```

## Integration Testing

### Gmail API Integration
```bash
# Test Gmail connection
python -c "
from backend.services.email_service import email_service
print('Gmail service:', 'Connected' if email_service.service else 'Not connected')
"
```

### Document Generation Integration
```bash
# Test document generators
python create_papajohns_application.py
python create_brownforman_application.py
python create_salesforce_application.py

# Verify output
ls -lh documents/*/*/Matthew_Scott* | wc -l
# Expected: > 0
```

## Test Data Validation

### Job Data Quality
```bash
sqlite3 job_search.db <<EOF
-- Check for jobs without companies
SELECT COUNT(*) FROM jobs WHERE company_id IS NULL;
-- Expected: 0

-- Check for invalid salaries
SELECT COUNT(*) FROM jobs WHERE salary_min > salary_max;
-- Expected: 0

-- Check for missing required fields
SELECT COUNT(*) FROM jobs WHERE title IS NULL OR title = '';
-- Expected: 0
EOF
```

### Application Data Quality
```bash
sqlite3 job_search.db <<EOF
-- Check for applications without jobs
SELECT COUNT(*) FROM applications WHERE job_id NOT IN (SELECT id FROM jobs);
-- Expected: 0

-- Check for future application dates
SELECT COUNT(*) FROM applications WHERE applied_date > datetime('now');
-- Expected: 0
EOF
```

## Automated Testing Schedule

### Daily Tests
- Run `test_workflow.py` every morning
- Check email automation status
- Verify server health

### Weekly Tests
- Full API endpoint test suite
- Database integrity check
- Performance benchmarks
- Backup verification

### Monthly Tests
- Complete regression testing
- Security audit
- Dependency updates check

## Test Failure Procedures

### If API Tests Fail
1. Check server is running: `curl http://localhost:8899/health`
2. Check logs: `tail -50 logs/job_automation.log`
3. Restart server if needed
4. Re-run tests

### If Database Tests Fail
1. Check database file exists: `ls -lh job_search.db`
2. Run integrity check: `sqlite3 job_search.db "PRAGMA integrity_check;"`
3. Restore from backup if corrupted
4. Re-initialize if necessary: `python init_database.py`

### If Email Tests Fail
1. Check Gmail token: `ls -lh gmail_token.json`
2. Verify credentials: Check `.env` file
3. Re-authenticate if needed: `python setup_gmail_simple.py`
4. Check API quotas

## Success Criteria

✅ **All tests must pass**:
- API: 10/10 endpoints working
- Workflow: 6/6 components passing
- Database: integrity_check = ok
- Email: Connection established
- Documents: Files generated > 0 bytes

✅ **Performance benchmarks**:
- API response time < 100ms
- Database queries < 10ms
- Document generation < 5 seconds

✅ **No errors in logs**:
```bash
grep -i "error\|exception\|failed" logs/job_automation.log | tail -20
# Should be empty or only minor warnings
```

## Continuous Integration

### Pre-commit Tests
```bash
# Run before every commit
python test_fixed_endpoints.py && \
python -m pytest tests/ && \
echo "✅ All tests passed - safe to commit"
```

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Database backed up
- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] Gmail authentication valid
- [ ] No secrets in code
- [ ] Documentation updated

---

**Test Status**: Last full test run October 7, 2025 - All systems operational (100% pass rate)