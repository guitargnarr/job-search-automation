# API Documentation - Job Search Automation Platform v2.2.0

## Base URL
```
http://localhost:8899
```

## Core Endpoints

### Health Check
```bash
GET /health
curl http://localhost:8899/health
```

### Jobs
```bash
# List jobs
GET /api/v1/jobs/list?limit=10
curl "http://localhost:8899/api/v1/jobs/list?limit=10"

# Create job
POST /api/v1/jobs/create
curl -X POST http://localhost:8899/api/v1/jobs/create \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "title": "Software Engineer",
    "job_description": "Description here",
    "job_url": "https://example.com/job",
    "salary_min": 80000,
    "salary_max": 120000
  }'

# Get job details
GET /api/v1/jobs/{id}
curl http://localhost:8899/api/v1/jobs/69
```

### Applications
```bash
# List applications
GET /api/v1/applications/list
curl http://localhost:8899/api/v1/applications/list

# Application stats
GET /api/v1/applications/stats
curl http://localhost:8899/api/v1/applications/stats
```

### Email Automation
```bash
# Scan emails
POST /api/v1/email/scan
curl -X POST http://localhost:8899/api/v1/email/scan \
  -d '{"days_back": 30}'

# Email stats
GET /api/v1/email/stats
curl http://localhost:8899/api/v1/email/stats
```

### Analytics
```bash
# Dashboard
GET /api/v1/analytics/dashboard
curl http://localhost:8899/api/v1/analytics/dashboard

# Performance score
GET /api/v1/analytics/performance-score
curl http://localhost:8899/api/v1/analytics/performance-score
```

### Follow-ups
```bash
# Get scheduled follow-ups
GET /api/v1/follow-ups/scheduled
curl http://localhost:8899/api/v1/follow-ups/scheduled
```

## Testing All Endpoints
```bash
# Run comprehensive test
python test_fixed_endpoints.py
```

## Authentication
Currently no authentication required (single-user system).

## Rate Limits
No rate limits for local deployment.

## Response Format
All responses are JSON with this structure:
```json
{
  "status": "success|error",
  "data": {},
  "message": "Optional message"
}
```