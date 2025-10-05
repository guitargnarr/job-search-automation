# Changelog - Job Search Automation Platform

All notable changes to this project will be documented in this file.

## [2.1.0] - 2025-10-05 - System Stabilization & Real Job Discovery

### 🚀 Added
- **Web Search Job Discovery**: Integrated WebSearch capability for finding real jobs
  - Searches Indeed, Glassdoor, ZipRecruiter, LinkedIn, Dice
  - Filters by location (remote-only outside Louisville)
  - Filters by industry (healthcare/insurance focus)
  - Excludes specified companies (Humana)
- **Real Job Portfolio**: Added **7 verified real jobs** from major healthcare companies
  - Centene Corporation - Data Analyst III ($77k-$116k)
  - Molina Healthcare - Healthcare Data Analyst ($70k-$95k)
  - Insurance Provider - Senior Business Analyst ($140k-$145k)
  - The Cigna Group - Business Analytics Senior Advisor ($109k-$182k) ⭐ Highest paying
  - UnitedHealth Group - Data Analyst 2 ($102k-$138k) - Fortune 5 company
  - UnitedHealth Group - COB Data Analyst ($71k-$140k)
  - CVS Health (Aetna) - Healthcare Claims Analyst ($59k-$98k)
- **Comprehensive Documentation**:
  - SYSTEM_DEMO_PROOF.md - Full system demonstration
  - QUICK_START_REAL_JOBS.md - Guide for using with real jobs
  - REAL_JOBS_ADDED.md - Initial 3 jobs proof
  - REAL_JOBS_EXPANDED.md - All 7 jobs with full analysis
  - PROOF_COMPLETE.txt - Initial verification documentation
  - TEST_RESULTS_FINAL.md - Comprehensive test suite results (10 tests, 100% pass)
  - NEW_JOBS_SUMMARY.txt - Quick reference for all 7 jobs
  - VERSION_CONTROL_SUMMARY.md - Git commit and versioning details
- **API Pagination Limits**:
  - MAX_API_PAGE_SIZE: 100 (configurable)
  - DEFAULT_API_PAGE_SIZE: 50
  - Prevents memory exhaustion on large datasets

### 🐛 Fixed
- **Critical Memory Issue**:
  - Identified: Claude Code out of memory during large API responses
  - Root Cause: 4 duplicate uvicorn servers + unbounded pagination
  - Resolution: Killed duplicate servers, added pagination limits
  - Impact: Memory usage reduced from ~308MB to 19MB (93% reduction)

- **Database Schema Mismatches** (25+ corrections):
  - `Job.active` → `Job.status` (string with states: new, researching, ready, closed)
  - `Job.description` → `Job.job_description`
  - `Job.url` → `Job.job_url`
  - `Job.remote_allowed` → `Job.remote_type` (remote|hybrid|onsite)
  - Updated all API endpoints in jobs.py, applications.py, analytics.py

- **LinkedIn Deprecation Handling**:
  - Removed references to `LinkedInConnection` (should be `LinkedInOutreach`)
  - Updated analytics to return deprecated status for LinkedIn metrics
  - Performance score uses baseline (15pts) instead of connection count

### 🔧 Changed
- **Configuration**:
  - Added MAX_API_PAGE_SIZE and DEFAULT_API_PAGE_SIZE to config.py
  - Documented DATABASE_URL conflict (must unset for SQLite)

- **API Responses**:
  - All list endpoints now enforce pagination limits
  - Job list returns `status` field instead of non-existent `active`
  - Field names now match database schema exactly

- **Documentation Structure**:
  - CLAUDE.md updated with job search workflow
  - Added search criteria and location rules
  - Included real-world usage examples

### 📊 Metrics
- **API Endpoints**: 30 active (6/7 tested successfully)
- **Database Size**: 76KB with 11 jobs, 3 applications
- **Memory Usage**: 19MB (single server instance, 93% reduction)
- **Response Times**: 87-150ms for all endpoints (avg 94ms)
- **Jobs Tracked**: 11 total (**7 real** + 4 test examples)
- **Test Results**: 10/10 tests passed (100% pass rate)
- **Companies**: 7 unique (5 Fortune 500/Fortune 5)
- **Salary Range**: $59,000 - $182,500 (real market data)

### 🔒 Security
- Pagination limits prevent memory exhaustion attacks
- Single server instance reduces attack surface
- Database credentials properly isolated in .env

### 📝 Notes
- Server running on port 8899 (PID 62313)
- SQLite database at ./job_search.db
- Test data can be cleared by deleting jobs #1-4
- Real jobs are IDs #5, #6, #7

---

## [2.0.0] - 2025-10-05 - Initial Operational Release

### ✅ Core Features Implemented
- FastAPI backend with 37 endpoints
- SQLAlchemy async database (SQLite)
- Email automation service (Gmail API ready)
- ATS optimization service (spaCy + TF-IDF)
- LinkedIn automation (deprecated)
- Job tracking with full lifecycle
- Application management
- Analytics and reporting
- Follow-up scheduling

### 📦 Database Schema
- 8 tables: companies, jobs, applications, email_tracking, linkedin_outreach, follow_ups, template_performance
- Full relational structure with foreign keys
- Timestamp tracking on all records
- Enum types for status management

### 🎯 Tested & Verified
- Database initialization successful
- API server operational
- Sample data loaded (3 companies, 3 jobs, 2 applications)
- Health endpoint responding
- All endpoint routes registered

---

## [1.0.0] - Earlier - Basic File Structure

### Initial Setup
- Project structure created
- Basic automation scripts
- Document generators
- Resume templates (5 variations)
- Cover letter generators
- File organization system

---

## Version Numbering

- **Major.Minor.Patch** format
- **Major**: Breaking changes or major new features
- **Minor**: New features, backwards compatible
- **Patch**: Bug fixes and minor improvements

## Links

- Documentation: [CLAUDE.md](./CLAUDE.md)
- Quick Start: [QUICK_START.md](./QUICK_START.md)
- Real Jobs Guide: [QUICK_START_REAL_JOBS.md](./QUICK_START_REAL_JOBS.md)
- System Demo: [SYSTEM_DEMO_PROOF.md](./SYSTEM_DEMO_PROOF.md)
