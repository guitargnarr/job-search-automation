#!/usr/bin/env python3
"""
Create Sentinel-1 Master Control Spreadsheet
Generates comprehensive tracking Excel file with 3 tabs
"""

import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path

# Database connection
conn = sqlite3.connect('job_search.db')

# TAB 1: APPLICATION PIPELINE
print("Creating Application Pipeline tab...")

# Query applications with full details
query = """
SELECT
    a.id as App_ID,
    j.id as Job_ID,
    c.name as Company_Name,
    j.title as Job_Title,
    j.location as Location,
    CASE
        WHEN j.salary_min IS NOT NULL AND j.salary_max IS NOT NULL
        THEN '$' || CAST(j.salary_min AS TEXT) || ' - $' || CAST(j.salary_max AS TEXT)
        ELSE 'TBD'
    END as Salary_Range,
    j.job_url as Job_URL,
    '' as Workday_Job_Req_ID,
    a.applied_date as Application_Date,
    a.application_method as Application_Method,
    '' as Resume_Path,
    '' as CoverLetter_Path,
    a.resume_version as Resume_Version,
    '' as Generator_Used,
    a.status as Status,
    a.response_date as Response_Date,
    a.response_type as Response_Type,
    '' as Notes,
    '' as Next_Action
FROM applications a
JOIN jobs j ON a.job_id = j.id
LEFT JOIN companies c ON j.company_id = c.id
ORDER BY a.applied_date DESC
"""

df_apps = pd.read_sql_query(query, conn)

# Manually update specific fields from known data
df_apps.loc[df_apps['App_ID'] == 13, 'Workday_Job_Req_ID'] = 'R2787'
df_apps.loc[df_apps['App_ID'] == 13, 'Resume_Path'] = '/Users/matthewscott/Desktop/Resumes/Waystar_Strategic_Solutions_FINAL_Resume.pdf'
df_apps.loc[df_apps['App_ID'] == 13, 'CoverLetter_Path'] = '/Users/matthewscott/Desktop/Resumes/Waystar_Strategic_Solutions_FINAL_CoverLetter.pdf'
df_apps.loc[df_apps['App_ID'] == 13, 'Generator_Used'] = 'create_waystar_strategic_solutions.py'
df_apps.loc[df_apps['App_ID'] == 13, 'Notes'] = 'Strategic Solutions Analyst - Client Success role. Posted 14 days ago (verified active). Perfect match for stakeholder coordination background.'

df_apps.loc[df_apps['App_ID'] == 12, 'Workday_Job_Req_ID'] = 'JR-00009314'
df_apps.loc[df_apps['App_ID'] == 12, 'Resume_Path'] = '/Users/matthewscott/Desktop/Resumes/BrownForman_Complete_Application_Final.pdf'
df_apps.loc[df_apps['App_ID'] == 12, 'Generator_Used'] = 'create_brownforman_ea_application.py'

df_apps.loc[df_apps['App_ID'] == 9, 'Resume_Path'] = '/Users/matthewscott/Desktop/Resumes/Matthew_Scott_Resume_Cedar_TAM_2025.pdf'
df_apps.loc[df_apps['App_ID'] == 9, 'CoverLetter_Path'] = '/Users/matthewscott/Desktop/Resumes/Matthew_Scott_CoverLetter_Cedar_TAM_2025.pdf'
df_apps.loc[df_apps['App_ID'] == 9, 'Generator_Used'] = 'create_cedar_tam_application.py'

# TAB 2: SYSTEM REFERENCE FOR CLAUDE
print("Creating System Reference tab...")

system_ref_data = [
    ['SECTION', 'ITEM', 'PATH/COMMAND', 'STATUS', 'NOTES'],
    ['=== CORE SYSTEM FILES ===', '', '', '', ''],
    ['Database', 'SQLite Database', '/Users/matthewscott/Desktop/Job_Search/job_search.db', '☐', '79 jobs, 6 applications tracked'],
    ['Server', 'FastAPI Main', '/Users/matthewscott/Desktop/Job_Search/backend/main.py', '☐', '30 API endpoints'],
    ['Config', 'Settings', '/Users/matthewscott/Desktop/Job_Search/backend/core/config.py', '☐', 'OAuth disabled'],
    ['README', 'System Overview', '/Users/matthewscott/Desktop/Job_Search/README.md', '☐', 'Sentinel-1 documentation'],
    ['Requirements', 'Dependencies', '/Users/matthewscott/Desktop/Job_Search/requirements.txt', '☐', 'Python 3.9+ libs'],

    ['=== WORKING GENERATORS ===', '', '', '', ''],
    ['AI Governance', 'Governance Generator', 'create_ai_governance_application.py', '☐', 'For AI compliance roles'],
    ['TAM/Client Success', 'Waystar Generator', 'create_waystar_strategic_solutions.py', '☐', 'Used for Waystar'],
    ['Executive Assistant', 'EA Generator', 'create_brownforman_ea_application.py', '☐', 'Used for Brown-Forman'],
    ['Cedar TAM', 'TAM Specific', 'create_cedar_tam_application.py', '☐', 'Used for Cedar'],

    ['=== UTILITY SCRIPTS ===', '', '', '', ''],
    ['Job Checker', 'Database Viewer', 'check_jobs_fixed.py', '☐', 'Shows all jobs and apps'],
    ['Job Verifier', 'Posting Validator', 'verify_job_status.py', '☐', 'Checks if job still active'],
    ['Job Adder', 'Quick Add', 'add_job_temp.py', '☐', 'Add jobs to database'],
    ['Tracker', 'Mark Applied', 'mark_applied.py', '☐', 'Update after submission'],
    ['PDF Converter', 'Document Converter', 'convert_to_pdf.py', '☐', 'Text to PDF'],

    ['=== DOCUMENTATION ===', '', '', '', ''],
    ['Usage Guide', 'E2E Workflow', 'SENTINEL_USAGE.md', '☐', 'How to use system'],
    ['Credibility', 'Positioning Rationale', 'CREDIBILITY_RATIONALE.md', '☐', 'Resume positioning ethics'],
    ['Workday Context', 'Manual Process', 'MANUAL_WORKDAY_CONTEXT.md', '☐', 'Form filling guide'],
    ['Interview Prep', 'AI Governance Strategy', 'INTERVIEW_STRATEGY_AI_GOVERNANCE.txt', '☐', 'Interview talking points'],

    ['=== SERVER OPERATIONS ===', '', '', '', ''],
    ['Start Server', 'Launch Command', 'unset DATABASE_URL; /Users/matthewscott/google-env/bin/python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8899', '☐', 'Starts on port 8899'],
    ['Stop Server', 'Kill Command', 'lsof -ti:8899 | xargs kill -9', '☐', 'Terminates server'],
    ['Health Check', 'Verify Running', 'curl http://localhost:8899/health', '☐', 'Returns JSON status'],
    ['API Docs', 'Swagger UI', 'http://localhost:8899/docs', '☐', 'Interactive API explorer'],

    ['=== DATABASE OPERATIONS ===', '', '', '', ''],
    ['View Apps', 'SQL Query', 'sqlite3 job_search.db "SELECT * FROM applications ORDER BY applied_date DESC;"', '☐', 'All applications'],
    ['High Priority Jobs', 'SQL Query', 'sqlite3 job_search.db "SELECT * FROM jobs WHERE priority=\'HIGH\' ORDER BY id DESC;"', '☐', 'Priority jobs'],
    ['Response Tracking', 'SQL Query', 'sqlite3 job_search.db "SELECT a.id, j.title, a.status FROM applications a JOIN jobs j ON a.job_id=j.id;"', '☐', 'Application status'],

    ['=== TECH STACK ===', '', '', '', ''],
    ['Python', 'Version', '3.9+ (google-env virtualenv)', '☐', 'Core language'],
    ['Framework', 'Backend', 'FastAPI', '☐', 'Async API framework'],
    ['Database', 'ORM + DB', 'SQLAlchemy + SQLite', '☐', 'Async database'],
    ['NLP', 'Language Model', 'spaCy 3.8.7 + en_core_web_sm', '☐', 'Keyword extraction'],
    ['PDF', 'Document Gen', 'reportlab 4.0.0', '☐', 'PDF creation'],
    ['Documents', 'Word Processing', 'python-docx 1.1.0', '☐', 'DOCX handling'],

    ['=== FUTURE VISION ===', '', '', '', ''],
    ['Email Automation', 'Activate at 25 apps', 'Daily email scan + response tracking', '☐', 'OAuth re-enable required'],
    ['Analytics Dashboard', 'Data insights', 'Response rate patterns, salary correlation', '☐', 'At MVD threshold (25 apps)'],
    ['A/B Testing', 'Template optimization', 'Template A vs B performance tracking', '☐', 'Track in template_performance table'],
    ['Follow-up System', '7-day intervals', 'Automated follow-up detection', '☐', 'Manual send, auto-detect'],
    ['MCP Integration', 'Natural language', 'backend/experimental/mcp/ servers', '☐', 'Future enhancement'],
]

df_system = pd.DataFrame(system_ref_data[1:], columns=system_ref_data[0])

# TAB 3: VERSION CONTROL
print("Creating Version Control tab...")

# Git log data (parse from the output we got)
version_data = [
    ['Commit_Hash', 'Commit_Date', 'Commit_Message', 'Files_Changed', 'Insertions', 'Deletions', 'Key_Features'],
    ['8dda436', '2025-10-09 18:47', 'Waystar submission complete - transition to analytics', 15, 1833, 0, 'Cedar, Brown-Forman, Waystar apps submitted'],
    ['f2b881e', '2025-10-09 18:01', 'Final Waystar with credibility rationale', 13, 1340, 740, 'CREDIBILITY_RATIONALE.md, positioning documented'],
    ['5367219', '2025-10-09 02:46', 'AI governance career positioning strategy', 5, 633, 0, 'AI governance generator, interview strategy'],
    ['0e22006', '2025-10-09 02:22', 'Job verification utility with GEICO validation', 2, 81, 0, 'verify_job_status.py created'],
    ['cb0e81a', '2025-10-09 02:12', 'PDF converter and 4 AI applications ready', 11, 600, 0, 'convert_to_pdf.py, 4 AI apps generated'],
]

df_version = pd.DataFrame(version_data[1:], columns=version_data[0])

# Create Excel file with all 3 tabs
output_path = '/Users/matthewscott/Desktop/Resumes/Sentinel1_Master_Control_v1.xlsx'

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df_apps.to_excel(writer, sheet_name='Application_Pipeline', index=False)
    df_system.to_excel(writer, sheet_name='System_Reference_for_Claude', index=False)
    df_version.to_excel(writer, sheet_name='Version_Control', index=False)

print(f"\\nSentinel-1 Master Control Spreadsheet created:")
print(f"Location: {output_path}")
print(f"Tabs: Application_Pipeline (6 apps), System_Reference_for_Claude, Version_Control")
print("\\nReady for use in Excel/Numbers/Google Sheets")

conn.close()
