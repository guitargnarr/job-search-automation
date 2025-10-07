# Quick Start Guide - Job Search Automation Platform

## 🚀 Getting Started in 5 Minutes

### Step 1: Verify System Health (30 seconds)
```bash
# Check if server is running
curl http://localhost:8899/health
```

Expected output: `{"status": "healthy", "version": "2.1.1"}`

### Step 2: View Available Jobs (1 minute)
```bash
# See all jobs ready to apply to
python3 run_application.py --list | head -10
```

### Step 3: Apply to Your First Job (3 minutes)
```bash
# Prepare documents for a job (e.g., job #69)
python3 run_application.py --job-id 69

# Documents are created in:
# - documents/cover_letters/sent/
# - documents/resumes/tailored/
```

### Step 4: Submit Application (Manual - 10 minutes)
1. Review generated documents
2. Visit company website
3. Upload and submit
4. System tracks automatically

### Step 5: Monitor Progress (30 seconds)
```bash
# Check your application stats
curl http://localhost:8899/api/v1/applications/stats
```

## 📋 Daily Workflow

### Morning (5 minutes)
```bash
# 1. Check for email responses
curl http://localhost:8899/api/v1/email/stats

# 2. View dashboard
curl http://localhost:8899/api/v1/analytics/dashboard

# 3. Check scheduled follow-ups
curl http://localhost:8899/api/v1/follow-ups/scheduled
```

### During Day (20-30 minutes)
```bash
# Prepare 3-5 applications
python3 run_application.py --batch 3

# Submit manually on company websites
```

### Evening (5 minutes)
```bash
# Review performance
curl http://localhost:8899/api/v1/analytics/performance-score

# Check updated stats
python3 test_workflow.py
```

## 🎯 Your Current Pipeline

**Ready to Submit**:
- Job #68: Brown-Forman Senior PM ($95k-$125k) - HIGHEST VALUE
- Job #66: Salesforce BA Remote ($80k-$110k)  
- Job #69: Papa John's IT QA ($60k-$82k)

**Total Opportunity Value**: $235k - $317k

## 📞 Quick Commands Reference

| Task | Command |
|------|---------|
| List jobs | `python3 run_application.py --list` |
| Apply to job | `python3 run_application.py --job-id <ID>` |
| Batch apply | `python3 run_application.py --batch 5` |
| Test system | `python3 test_workflow.py` |
| Check health | `curl http://localhost:8899/health` |
| View analytics | `curl http://localhost:8899/api/v1/analytics/dashboard` |

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Server not responding | Restart: `python3 -m uvicorn backend.main:app --port 8899 --reload` |
| Can't find database | Check you're in `/Users/matthewscott/Desktop/Job_Search` |
| Gmail errors | Re-auth: `python3 setup_gmail_simple.py` |
| Empty documents | Use company-specific scripts (e.g., `create_papajohns_application.py`) |

## 📚 Full Documentation

- **README.md** - Main overview
- **CLAUDE.md** - System capabilities
- **API_DOCUMENTATION.md** - API reference
- **TESTING.md** - Test protocols
- **MAINTENANCE.md** - Maintenance guide
- **FILE_STRUCTURE.md** - File organization
- **EXECUTIVE_SUMMARY.md** - Current status

## ⏰ Time Investment

- **Setup**: 5 minutes (already done!)
- **Per Application**: 20 minutes (vs 65 without system)
- **Daily Maintenance**: 5 minutes
- **Weekly Review**: 15 minutes

**Monthly Time Saved**: 20+ hours
**Annual Value**: $7,000+ (at $30/hour)

---

**You're all set! Start with:** `python3 run_application.py --job-id 68` (Brown-Forman - your highest paying opportunity!)
