# System Safety Rules & Constraints
## Hard-Coded Guardrails for Job Search Automation

**Version**: 2.2.0
**Last Updated**: October 6, 2025
**Priority**: CRITICAL - These rules are inviolable

---

## 🚫 RULE #1: NEVER AUTOMATICALLY SEND EMAILS

### **What This Means**:
- The system can **READ** your Gmail inbox automatically
- The system can **CLASSIFY** responses automatically
- The system can **SCHEDULE reminders** for you to follow up
- The system **CANNOT** and **WILL NOT** send emails on your behalf

### **Implementation**:
- `backend/services/email_service.py` has `send_follow_up()` method
- This method is **MANUAL TRIGGER ONLY**
- NO automatic calling of this method from scheduled tasks
- NO background processes that send emails
- ALL email composition is human-reviewed before sending

### **Why This Rule Exists**:
1. **Professional reputation**: Automated emails can damage relationships
2. **Context matters**: You need to review each situation before responding
3. **Tone/timing**: Only humans understand nuance
4. **Legal/compliance**: Automated outreach can violate terms of service

### **How Follow-Ups Work** (Correct Workflow):
```
Day 7 After Application:
  ↓
System creates reminder: "Follow up on [Company] application"
  ↓
YOU check reminder (via API or scheduled task)
  ↓
YOU review application status
  ↓
YOU decide to send or not
  ↓
YOU manually compose and send email (or use template as starting point)
  ↓
System logs the follow-up action for tracking
```

---

## 🚫 RULE #2: ESPECIALLY NEVER CONTACT HUMANA

### **What This Means**:
- Humana is **EXCLUDED** from all job searches
- Humana is **EXCLUDED** from all automated processes
- If Humana appears in search results, **SKIP automatically**
- **NEVER** send any communication to Humana through this system

### **Implementation**:
```python
# In all job search code:
EXCLUDED_COMPANIES = ["Humana", "Humana Inc", "Humana Inc."]

# In web search queries:
query = "Healthcare Business Analyst remote -Humana"

# In CSV import:
if "Humana" in company_name:
    # Only import if user explicitly marked as different department
    # AND user has manually reviewed
    pass
```

### **Exception** (From Your CSV Job #35):
- "Business Process Analyst, Humana (Different Department)"
- Priority: MEDIUM
- Note: "Research carefully. Check internal applicant policies."

**This exception requires**:
- Manual research by you
- Verification of internal application rules
- NO automated outreach
- Your explicit decision to proceed

### **Why This Rule Exists**:
- Professional relationships require care
- Internal applications have specific protocols
- Former employer outreach must be strategic, not automated
- Reputation risk is high

---

## 🚫 RULE #3: NO AUTOMATIC APPLICATION SUBMISSION

### **What This Means**:
- System can **FIND** jobs via web search
- System can **ANALYZE** job-resume fit (ATS scoring)
- System can **PREPARE** application materials
- System **CANNOT** submit applications automatically

### **You Must Manually**:
1. Review the job posting (verify it's legit)
2. Review the customized resume (verify accuracy)
3. Review the cover letter (verify tone/content)
4. Click "Submit" on the company's website yourself
5. Log the application in the database

### **Why This Rule Exists**:
- Application quality > application quantity
- Job postings can be scams or outdated
- Company culture fit requires human judgment
- Each application is a professional commitment

---

## 🚫 RULE #4: WEB SEARCH EXCLUSIONS ENFORCED

### **Excluded Companies** (ALWAYS):
- ❌ Humana (former employer - requires special handling)

### **Excluded Roles** (By Default):
- ❌ Internships (below experience level)
- ❌ "Junior" titles (below seniority)
- ❌ Part-time (unless explicitly requested)
- ❌ Unpaid (obvious)

### **Geographic Filters**:
✅ **Louisville, KY**: All job types accepted (remote, hybrid, onsite)
❌ **Outside Louisville**: MUST be remote/work-from-home ONLY

### **Salary Filters** (Based on Your CSV):
- Minimum threshold: $65k (MEDIUM priority)
- Target range: $75-110k (HIGH priority)
- Below $65k: SKIP (unless exceptional circumstances)

---

## ✅ RULE #5: HUMAN-IN-THE-LOOP FOR ALL ACTIONS

### **Automation Levels Defined**:

**Level 1: Fully Automated** (No human review)
- ✅ Email inbox scanning
- ✅ Email classification
- ✅ Database updates from email responses
- ✅ Reminder scheduling

**Level 2: Semi-Automated** (Human approval required)
- ⚠️ Job discovery via web search (you approve before adding)
- ⚠️ Resume customization (you review before using)
- ⚠️ ATS score improvements (you decide which keywords to add)

**Level 3: Manual Only** (No automation)
- 🔒 Email sending (always manual)
- 🔒 Application submission (always manual)
- 🔒 Interview scheduling (always manual)
- 🔒 Salary negotiation (always manual)

**Philosophy**: Automate the busy work (reading, classifying, reminding), never automate the relationship work (writing, submitting, committing).

---

## 🛡️ DATA PRIVACY & SECURITY

### **What Gets Stored**:
- ✅ Email subjects, senders, dates (for tracking)
- ✅ Email body excerpts (for classification)
- ✅ Job descriptions
- ✅ Application status
- ✅ Company information (public data)

### **What NEVER Gets Stored**:
- ❌ Full email bodies (truncated to 5000 chars)
- ❌ OAuth credentials in plain text (token file is encrypted)
- ❌ Personal identification numbers
- ❌ Salary expectations (only researched ranges)

### **What NEVER Gets Transmitted**:
- ❌ Resume content to third parties (ATS analysis is local NLP)
- ❌ Email content to external services
- ❌ Application data to analytics services

**Local-First Architecture**: All processing happens on your machine. No cloud dependencies except Gmail API (which you authorized).

---

## 🎯 RULE COMPLIANCE VERIFICATION

### **Daily Checks**:
```bash
# Verify no emails sent automatically
sqlite3 job_search.db "SELECT COUNT(*) FROM email_tracking WHERE sent_date IS NOT NULL;"
# Should be 0 (or only emails YOU manually sent and logged)

# Verify Humana exclusion
curl http://localhost:8899/api/v1/jobs/list | jq '.jobs[] | select(.company_name | contains("Humana"))'
# Should only show Job #35 if you imported CSV (manual exception)

# Verify reminder-only follow-ups
curl http://localhost:8899/api/v1/follow-ups/scheduled | jq '.[] | select(.sent == true)'
# Should be empty or only manually triggered sends
```

### **Weekly Audit**:
- Review all jobs in database for Humana (should be exception only)
- Check email tracking table for any sent emails (investigate if found)
- Verify all applications have manual application_date (not auto-submitted)

---

## 🚨 EMERGENCY SHUTDOWN

### **If System Misbehaves**:

**Scenario: Accidental email sending detected**

```bash
# 1. Kill the server immediately
pkill -9 uvicorn

# 2. Check what was sent
sqlite3 job_search.db "SELECT * FROM email_tracking WHERE sent = 1 ORDER BY sent_date DESC;"

# 3. Review the code for automatic sending
grep -r "send_follow_up" backend/

# 4. If Humana was contacted, emergency protocol:
# - Review what was sent
# - Assess damage
# - Consider direct personal outreach to explain/apologize if necessary
```

**Scenario: Humana exclusion filter failed**

```bash
# 1. Delete any Humana jobs from database
curl -X DELETE http://localhost:8899/api/v1/jobs/{humana_job_id}

# 2. Review import script for filter logic
# 3. Re-import CSV with corrected filter
```

---

## ✅ RULE #6: WEB SEARCH TRANSPARENCY

### **How Web Search Works**:
1. You request a job search (or I suggest one based on your profile)
2. I use Claude's WebSearch tool with your filters
3. Results are presented to you for review
4. You decide which to add to tracking
5. I add approved jobs via API

### **What You Control**:
- Search queries and keywords
- Geographic filters
- Company exclusions
- Which results to track
- Priority levels assigned

### **What's Automated**:
- Search execution
- Results aggregation
- Duplicate filtering
- Basic relevance scoring

**You always approve before any job is added to your tracking system.**

---

## 📋 CONFIGURATION FILE SAFETY

### **.env File Constraints**:

**MUST NEVER CONTAIN**:
- Actual Gmail password (uses OAuth token instead)
- Social Security Number
- Credit card information
- Bank account details

**SHOULD CONTAIN**:
- File paths (credentials, token) - ✅ Safe
- Gmail scopes - ✅ Safe (just API permissions)
- Database URL - ✅ Safe (local SQLite)
- Secret key - ✅ Safe (auto-generated random string)

**NEVER COMMIT .env TO GIT**
- Already in .gitignore
- Contains semi-sensitive file paths
- User-specific configuration

---

## 🎓 PHILOSOPHY: TRUST BUT VERIFY

**The System's Job**:
- Gather information (emails, job postings)
- Organize data (database, classifications)
- Calculate metrics (ATS scores, response rates)
- Remind you of next actions

**Your Job**:
- Make decisions (apply or skip)
- Build relationships (write emails, interview)
- Negotiate offers (salary, start date)
- Manage your career (strategy, goals)

**The Boundary**:
```
AUTOMATION                      HUMAN JUDGMENT
│                               │
├─ Read emails                  ├─ Write emails
├─ Classify responses           ├─ Decide how to respond
├─ Schedule reminders           ├─ Send follow-ups
├─ Score resumes                ├─ Choose which jobs to apply to
├─ Extract keywords             ├─ Interview preparation
├─ Find job postings            ├─ Accept/reject offers
└─ Track applications           └─ Negotiate compensation
```

**This boundary is not flexible. It's the design.**

---

## 🔒 COMMIT TO SAFETY

By using this system, you commit to:

1. ✅ **Manual email review** - Never send without reading
2. ✅ **Humana exclusion** - Never automatic contact
3. ✅ **Application approval** - Never auto-submit
4. ✅ **Data privacy** - Keep credentials secure
5. ✅ **Weekly audits** - Verify system compliance

**If any rule is violated, immediately**:
- Shut down the server
- Review logs
- Fix the code
- Document the incident in CHANGELOG.md

---

## 🎯 SAFE AUTOMATION EXAMPLES

### **✅ SAFE: Email Scanning**
```bash
# This is safe - reads only, no sending
curl -X POST http://localhost:8899/api/v1/email/scan -d '{"days_back": 7}'
```

### **✅ SAFE: Job Discovery**
```bash
# You request, I search, you approve
"Find Medicare Compliance Analyst remote jobs -Humana"
```

### **✅ SAFE: ATS Analysis**
```bash
# Analyzes text, suggests keywords, you decide what to use
curl -X POST http://localhost:8899/api/v1/ats/analyze-job -d '{"job_description": "..."}'
```

### **⚠️ REQUIRES APPROVAL: Resume Generation**
```bash
# Generates optimized resume, but you must review before using
curl -X POST http://localhost:8899/api/v1/ats/generate-optimized
```

### **🔒 ALWAYS MANUAL: Follow-Up Sending**
```bash
# You check reminders
curl http://localhost:8899/api/v1/follow-ups/scheduled

# You decide to send
# You compose email (using template as reference)
# You send via your Gmail interface
# You log it: POST /api/v1/follow-ups/{id}/complete
```

---

**This system amplifies your judgment, it doesn't replace it.**

**You are always in control.**

---

*Last Updated: October 6, 2025*
*Version: 2.2.0*
*Next Review: After first violation (hopefully never)*
