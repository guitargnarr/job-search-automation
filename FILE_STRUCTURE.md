# Complete File Structure Documentation
**Job Search Automation Platform v2.2.0**

## Directory Tree Overview

```
Job_Search/                          # Project root
├── 📁 backend/                      # FastAPI application
│   ├── api/                        # API endpoints
│   │   └── v1/                     # Version 1 endpoints
│   │       ├── analytics.py        # Analytics dashboard & metrics
│   │       ├── applications.py     # Application tracking
│   │       ├── ats.py             # ATS optimization
│   │       ├── email.py           # Email automation
│   │       ├── follow_ups.py      # Follow-up scheduling
│   │       └── jobs.py            # Job management
│   ├── core/                       # Core infrastructure
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database connection & sessions
│   │   ├── logging.py             # Logging configuration
│   │   └── scheduler.py           # Background task scheduler
│   ├── models/                     # Data models
│   │   └── models.py              # SQLAlchemy ORM models
│   ├── services/                   # Business logic services
│   │   ├── ats_optimizer.py       # Resume optimization (spaCy/NLP)
│   │   └── email_service.py       # Gmail API integration
│   ├── deprecated/                 # Archived code
│   │   └── linkedin_*.py          # LinkedIn automation (removed)
│   └── main.py                     # FastAPI application entry point
│
├── 📁 documents/                    # Generated application documents
│   ├── cover_letters/              # Cover letters
│   │   └── sent/                   # Generated cover letters
│   │       ├── *_PapaJohns_*.txt      # Papa John's application
│   │       ├── *_BrownForman_*.txt    # Brown-Forman application
│   │       ├── *_Salesforce_*.txt     # Salesforce application
│   │       └── *.docx                 # Word format documents
│   └── resumes/                    # Resumes
│       └── tailored/               # Customized resumes
│           ├── *_PapaJohns_*.txt      # Tailored for each job
│           ├── *_BrownForman_*.txt
│           ├── *_Salesforce_*.txt
│           └── *.docx
│
├── 📁 logs/                         # Application logs
│   └── job_automation.log          # Main application log
│
├── 📁 tests/                        # Test suite
│   ├── test_workflow.py            # Complete workflow tests
│   └── test_fixed_endpoints.py     # API endpoint tests
│
├── 📁 backups/                      # Database backups (not in git)
│   └── job_search_YYYYMMDD.db      # Daily backups
│
├── 📁 scripts/                      # Utility scripts
│   ├── health_check.sh             # System health monitoring
│   └── backup.sh                   # Automated backup script
│
├── 📄 Configuration Files
│   ├── .env                        # Environment variables (NOT IN GIT)
│   ├── .env.example                # Example configuration
│   ├── .gitignore                  # Git exclusions
│   └── requirements.txt            # Python dependencies
│
├── 📄 Database
│   └── job_search.db              # SQLite database (NOT IN GIT)
│       └── Tables:
│           ├── companies (53 records)
│           ├── jobs (71 records)
│           ├── applications (7 records)
│           ├── email_tracking (34 records)
│           ├── follow_ups
│           ├── analytics_events
│           └── template_performance
│
├── 📄 Application Scripts
│   ├── run_application.py          # Main automation runner
│   ├── init_database.py            # Database initialization
│   ├── create_papajohns_application.py     # Papa John's generator
│   ├── create_brownforman_application.py   # Brown-Forman generator
│   ├── create_salesforce_application.py    # Salesforce generator
│   ├── create_centene_cover_letter.py      # Centene templates
│   ├── create_cigna_application.py         # Cigna templates
│   ├── add_centene_job.py          # Job import utilities
│   ├── check_jobs.py               # Job viewer
│   ├── mark_applied.py             # Status updater
│   └── log_centene_application.py  # Application logger
│
├── 📄 Gmail Authentication
│   ├── gmail_token.json            # OAuth token (NOT IN GIT)
│   ├── client_secret_*.json        # Gmail credentials (NOT IN GIT)
│   └── setup_gmail_simple.py       # Gmail setup script
│
├── 📄 Documentation
│   ├── README.md                   # Main documentation
│   ├── CLAUDE.md                   # Development journal & capabilities
│   ├── API_DOCUMENTATION.md        # Complete API reference
│   ├── TESTING.md                  # Testing protocols
│   ├── MAINTENANCE.md              # Maintenance & reliability guide
│   ├── FILE_STRUCTURE.md           # This file
│   ├── DOCUMENTATION_STATUS.md     # Documentation progress tracker
│   ├── README_AUTOMATION.md        # Legacy automation docs
│   └── RETROSPECTIVE_COMPLETE.md   # Historical retrospective
│
├── 📄 Architecture
│   ├── architecture.dot            # Graphviz source
│   └── architecture.png            # System architecture diagram
│
└── 📄 Git
    └── .git/                       # Version control (initialized)
```

## File Descriptions by Category

### Core Application Files

| File | Purpose | Size | Critical |
|------|---------|------|----------|
| `backend/main.py` | FastAPI app entry point | ~8KB | ✅ Yes |
| `backend/core/database.py` | Database connections | ~3KB | ✅ Yes |
| `backend/services/email_service.py` | Gmail integration | ~15KB | ✅ Yes |
| `run_application.py` | Main automation script | ~12KB | ✅ Yes |
| `.env` | Configuration secrets | <1KB | ✅ Yes |
| `job_search.db` | SQLite database | 256KB | ✅ Yes |

### API Endpoints (backend/api/v1/)

| Endpoint File | Routes | Functionality |
|--------------|--------|---------------|
| `jobs.py` | 6 routes | Job CRUD, search, stats |
| `applications.py` | 5 routes | Application tracking |
| `email.py` | 4 routes | Email scanning, stats |
| `analytics.py` | 3 routes | Metrics, dashboard, trends |
| `follow_ups.py` | 8 routes | Reminder scheduling |
| `ats.py` | 4 routes | Resume optimization |

### Document Generators

| Script | Purpose | Output Location |
|--------|---------|-----------------|
| `create_papajohns_application.py` | Papa John's docs | `documents/` |
| `create_brownforman_application.py` | Brown-Forman docs | `documents/` |
| `create_salesforce_application.py` | Salesforce docs | `documents/` |
| `create_centene_cover_letter.py` | Centene templates | `documents/` |

### Test Files

| File | Test Coverage | Pass Rate |
|------|---------------|-----------|
| `test_fixed_endpoints.py` | 10 API endpoints | 100% |
| `test_workflow.py` | 6 system components | 100% |

### Documentation Files

| Document | Purpose | Last Updated |
|----------|---------|--------------|
| `README.md` | Main project overview | Oct 7, 2025 |
| `CLAUDE.md` | System capabilities & journal | Oct 7, 2025 |
| `API_DOCUMENTATION.md` | API reference | Oct 7, 2025 |
| `TESTING.md` | Test protocols | Oct 7, 2025 |
| `MAINTENANCE.md` | Maintenance guide | Oct 7, 2025 |
| `FILE_STRUCTURE.md` | This file | Oct 7, 2025 |

## File Locations Quick Reference

### Critical Files (Never Delete)

```bash
# Database
./job_search.db                      # All your data

# Configuration
./.env                              # Your credentials
./gmail_token.json                  # Gmail authentication
./client_secret_*.json              # Gmail API credentials

# Core Application
./backend/main.py                   # Server entry point
./run_application.py                # Main automation script
```

### Generated Content

```bash
# Application Documents
./documents/cover_letters/sent/*.txt    # Cover letters
./documents/resumes/tailored/*.txt      # Resumes

# Backups
./backups/job_search_*.db               # Database backups

# Logs
./logs/job_automation.log               # Application logs
```

### Utility Scripts Location

```bash
# Job Application Generators
./create_*_application.py           # Company-specific generators

# Database Utilities
./init_database.py                  # Initialize database
./check_jobs.py                     # View jobs
./mark_applied.py                   # Update status

# Testing
./test_*.py                         # Test scripts
```

## Important .gitignore Patterns

**Never Committed**:
- `*.env` - Environment variables
- `gmail_token.json` - OAuth tokens
- `client_secret*.json` - API credentials
- `*.db` - Database files
- `documents/**/*.docx` - Personal documents
- `documents/**/*.pdf` - Personal documents
- `backups/` - Database backups
- `logs/` - Log files

**Always Committed**:
- `*.py` - Python source code
- `*.md` - Documentation
- `.gitignore` - Git exclusions
- `requirements.txt` - Dependencies
- `architecture.dot` - Architecture diagrams

## File Size Guidelines

| Category | Typical Size | Warning If Exceeds |
|----------|--------------|-------------------|
| Database | 100-500KB | 1MB |
| Logs | 1-10MB | 100MB |
| Backups (each) | ~256KB | 1MB |
| Documents (each) | 20-40KB | 100KB |
| Python files | 1-15KB | 50KB |

## File Modification Frequency

| File | Update Frequency |
|------|------------------|
| `job_search.db` | Multiple times daily |
| `gmail_token.json` | When OAuth refreshes |
| `logs/*.log` | Continuously |
| `documents/*` | When generating applications |
| `*.py` | During development |
| `*.md` | Weekly/monthly |
| `requirements.txt` | Monthly |

## Storage Requirements

**Current Usage**:
- Database: 256KB
- Documents: ~200KB (6 applications)
- Logs: ~5MB
- Code: ~500KB
- **Total**: ~6MB

**Recommended Minimums**:
- Free Disk Space: 1GB
- Backup Storage: 100MB
- Development: 5GB (with all dependencies)

## File Access Permissions

**Secure Files** (chmod 600):
- `.env`
- `gmail_token.json`
- `client_secret_*.json`

**Executable Scripts** (chmod 755):
- `run_application.py`
- `*.py` (application scripts)
- `scripts/*.sh`

**Normal Files** (chmod 644):
- `*.md` documentation
- `requirements.txt`
- `*.dot` diagrams

## Quick File Lookup

**Find a specific file**:
```bash
# Find all Python scripts
find . -name "*.py" -not -path "./.venv/*"

# Find all documentation
find . -name "*.md"

# Find all generated documents
find documents/ -type f

# Find large files
find . -size +10M

# Find recently modified
find . -mtime -1 -type f
```

**File statistics**:
```bash
# Count Python files
find . -name "*.py" -not -path "./.venv/*" | wc -l

# Total code size
find . -name "*.py" -not -path "./.venv/*" -exec wc -l {} + | tail -1

# Document count
ls -1 documents/*/* | wc -l
```

---

**Last Updated**: October 7, 2025
**Total Files**: ~100+
**Total Directories**: ~15
**Project Size**: ~6MB (excluding dependencies)