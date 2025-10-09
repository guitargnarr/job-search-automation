# Sentinel-1 Usage Guide
Step-by-Step Workflow for Accelerated Job Applications

## E2E Workflow: Find → Verify → Generate → Submit → Track

### STEP 1: Finding Jobs (Web Search)

Request web search from Claude Code:
"Find 5 AI Governance OR Business Analyst healthcare roles Louisville OR remote -Humana"

Review results. Identify 2-3 high-value matches.

### STEP 2: Job Verification (Integrity Check)

For each promising job, run verification:

```bash
python3 verify_job_status.py <job_id>
```

Manually confirm job is active via company careers site.

### STEP 3: Add Job to Database

Edit and run job addition script:

```bash
python3 add_job_temp.py
```

Or use specific scripts (add_geico_jeffersonville.py, add_pwc_analytics.py, etc.)

### STEP 4: Application Generation

Generate tailored resume + cover letter:

For AI Governance roles:
```bash
python3 create_ai_governance_application.py <job_id>
```

For Technical/TAM roles:
```bash
python3 create_ai_app_CORRECTED.py <job_id>
```

For general roles:
```bash
python3 generate_application.py <job_id>
```

### STEP 5: Document Conversion (if needed)

Convert to PDF:
```bash
python3 convert_to_pdf.py <job_id>
```

Files will be in: applications/[date]_[company]_[role]/

### STEP 6: Submission & Tracking

1. Review generated documents in application folder
2. Replace any [COMPANY NAME] placeholders
3. Submit application via company portal
4. Mark as applied:

```bash
python3 mark_applied.py <job_id>
```

### STEP 7: Status Monitoring

Check current status:
```bash
python3 check_jobs_fixed.py
```

## Quick Reference

VIEW JOBS: python3 check_jobs_fixed.py
VERIFY JOB: python3 verify_job_status.py <job_id>
GENERATE APP: python3 create_ai_governance_application.py <job_id>
MARK APPLIED: python3 mark_applied.py <job_id>

## Time Savings

Traditional: 60+ minutes per application
Sentinel-1: 15 minutes per application
Savings: 75% reduction (45 minutes saved per application)

## Current Status

Database: 76 jobs tracked
Applications: 5 submitted (1 rejected, 1 interview pending, 3 awaiting response)
Ready to generate: 71 jobs available for instant application creation

## System Philosophy

Zero-defect methodology from 9 years Fortune 50 compliance applied to job search acceleration.
Regulatory rigor meets employment speed.
