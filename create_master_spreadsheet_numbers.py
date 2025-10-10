#!/usr/bin/env python3
"""
Create Sentinel-1 Master Control Spreadsheet - NUMBERS VERSION
Generates comprehensive tracking for Apple Numbers
"""

import pandas as pd
import sqlite3

# Database connection
conn = sqlite3.connect('job_search.db')

print("Creating Sentinel-1 Master Control for Apple Numbers...")

# TAB 1: APPLICATION PIPELINE
print("Tab 1: Application_Pipeline...")

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

# Update known data for completed applications
updates = {
    13: {
        'Workday_Job_Req_ID': 'R2787',
        'Resume_Path': '~/Desktop/Resumes/Waystar_Strategic_Solutions_FINAL_Resume.pdf',
        'CoverLetter_Path': '~/Desktop/Resumes/Waystar_Strategic_Solutions_FINAL_CoverLetter.pdf',
        'Generator_Used': 'create_waystar_strategic_solutions.py',
        'Notes': 'Verified active Oct 9. Strategic Solutions Analyst. Client Success role. $86-106k.',
        'Next_Action': 'Follow up Oct 16 if no response'
    },
    12: {
        'Workday_Job_Req_ID': 'JR-00009314',
        'Resume_Path': '~/Desktop/Resumes/BrownForman_Complete_Application_Final.pdf',
        'CoverLetter_Path': '~/Desktop/Resumes/BrownForman_Complete_Application_Final.pdf',
        'Generator_Used': 'create_brownforman_ea_application.py',
        'Notes': 'Chairman/Family Shareholders office. Executive support role.',
        'Next_Action': 'Follow up Oct 16'
    },
    9: {
        'Resume_Path': '~/Desktop/Resumes/Matthew_Scott_Resume_Cedar_TAM_2025.pdf',
        'CoverLetter_Path': '~/Desktop/Resumes/Matthew_Scott_CoverLetter_Cedar_TAM_2025.pdf',
        'Generator_Used': 'create_cedar_tam_application.py',
        'Notes': 'Technical Account Manager. Best salary match ($123-145k).',
        'Next_Action': 'Monitor for response'
    },
    10: {
        'Notes': 'RESPONDED - Expecting interview scheduling. Recruiter confirmed met qualifications.',
        'Next_Action': 'PREPARE FOR INTERVIEW - Review project management talking points'
    },
    11: {
        'Notes': 'LinkedIn recruiter outreach (Kathy Maxwell). IT ServiceDesk + Vulnerability.',
        'Next_Action': 'Follow up with Kathy Maxwell Oct 14'
    },
    4: {
        'Notes': 'REJECTED. Medicare compliance role. Applied with compliance-focused resume.',
        'Next_Action': 'Archive - rejected'
    }
}

for app_id, data in updates.items():
    for col, val in data.items():
        df_apps.loc[df_apps['App_ID'] == app_id, col] = val

# TAB 2: SYSTEM REFERENCE
print("Tab 2: System_Reference_for_Claude...")

system_data = {
    'Section': [],
    'Item': [],
    'Path_or_Command': [],
    'Checkbox': [],
    'Notes': []
}

sections = [
    ('=== CORE SYSTEM FILES ===', [
        ('Database', '/Users/matthewscott/Desktop/Job_Search/job_search.db', '☐', '79 jobs, 6 applications'),
        ('FastAPI Server', '/Users/matthewscott/Desktop/Job_Search/backend/main.py', '☐', '30 API endpoints'),
        ('Configuration', '/Users/matthewscott/Desktop/Job_Search/backend/core/config.py', '☐', 'OAuth disabled for security'),
        ('System README', '/Users/matthewscott/Desktop/Job_Search/README.md', '☐', 'Sentinel-1 overview'),
        ('Requirements', '/Users/matthewscott/Desktop/Job_Search/requirements.txt', '☐', 'Python dependencies'),
    ]),

    ('=== APPLICATION GENERATORS ===', [
        ('AI Governance', 'create_ai_governance_application.py', '☐', 'For AI compliance/risk roles ($120-180k)'),
        ('TAM/Client Success', 'create_waystar_strategic_solutions.py', '☐', 'USED for Waystar'),
        ('Executive Assistant', 'create_brownforman_ea_application.py', '☐', 'USED for Brown-Forman'),
        ('Cedar TAM', 'create_cedar_tam_application.py', '☐', 'USED for Cedar'),
        ('Generic Generator', 'generate_application.py', '☐', 'Fallback generator'),
    ]),

    ('=== UTILITY SCRIPTS ===', [
        ('Job Database Viewer', 'check_jobs_fixed.py', '☐', 'Shows all 79 jobs + application status'),
        ('Job Posting Verifier', 'verify_job_status.py', '☐', 'Checks if posting still active'),
        ('Quick Job Adder', 'add_job_temp.py', '☐', 'Add jobs to database'),
        ('Application Tracker', 'mark_applied.py', '☐', 'Update status after submission'),
        ('PDF Converter', 'convert_to_pdf.py', '☐', 'Convert text applications to PDF'),
    ]),

    ('=== KEY DOCUMENTATION ===', [
        ('Usage Guide', 'SENTINEL_USAGE.md', '☐', 'Complete E2E workflow'),
        ('Credibility Rationale', 'CREDIBILITY_RATIONALE.md', '☐', 'Resume positioning ethics + defense'),
        ('Workday Manual Process', 'MANUAL_WORKDAY_CONTEXT.md', '☐', 'Form filling guide'),
        ('Interview Strategy', 'INTERVIEW_STRATEGY_AI_GOVERNANCE.txt', '☐', 'AI governance talking points'),
        ('Changelog', 'CHANGELOG.md', '☐', '3 critical milestones documented'),
    ]),

    ('=== SERVER OPERATIONS ===', [
        ('START', 'unset DATABASE_URL; /Users/matthewscott/google-env/bin/python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8899', '☐', 'Launches on port 8899'),
        ('STOP', 'lsof -ti:8899 | xargs kill -9', '☐', 'Terminates server process'),
        ('HEALTH', 'curl http://localhost:8899/health', '☐', 'Returns JSON health status'),
        ('API DOCS', 'http://localhost:8899/docs', '☐', 'Swagger UI for all endpoints'),
        ('CURRENT STATUS', 'Running on port 8899', '☐', 'PID varies - check with lsof'),
    ]),

    ('=== DATABASE QUERIES ===', [
        ('View All Apps', 'sqlite3 job_search.db "SELECT * FROM applications ORDER BY applied_date DESC;"', '☐', 'Chronological application list'),
        ('High Priority Jobs', 'sqlite3 job_search.db "SELECT * FROM jobs WHERE priority=\'HIGH\';"', '☐', 'Filter high priority only'),
        ('Application Status', 'sqlite3 job_search.db "SELECT a.id, j.title, a.status FROM applications a JOIN jobs j ON a.job_id=j.id;"', '☐', 'Quick status check'),
        ('Jobs by Company', 'sqlite3 job_search.db "SELECT c.name, COUNT(j.id) FROM jobs j JOIN companies c ON j.company_id=c.id GROUP BY c.name;"', '☐', 'Company distribution'),
    ]),

    ('=== TECH STACK ===', [
        ('Python', '3.9+ (google-env virtualenv)', '☐', 'Core language environment'),
        ('FastAPI', 'Async web framework', '☐', 'API backend'),
        ('SQLAlchemy + SQLite', 'Database ORM', '☐', 'Async database operations'),
        ('spaCy 3.8.7', 'NLP library + en_core_web_sm model', '☐', 'Keyword extraction for ATS'),
        ('reportlab 4.0.0', 'PDF generation', '☐', 'Document creation'),
        ('python-docx 1.1.0', 'Word documents', '☐', 'DOCX processing'),
        ('pandas 2.1.0', 'Data analysis', '☐', 'Analytics and reporting'),
    ]),

    ('=== API ENDPOINTS (30 total) ===', [
        ('GET /health', 'Health check endpoint', '☐', 'Returns server status'),
        ('POST /api/v1/jobs/create', 'Add job to database', '☐', 'Job creation'),
        ('GET /api/v1/jobs/list', 'List all jobs', '☐', 'Retrieve jobs'),
        ('POST /api/v1/applications/create', 'Track application', '☐', 'Application logging'),
        ('GET /api/v1/applications/stats', 'Application metrics', '☐', 'Response rates'),
        ('POST /api/v1/email/scan', 'Scan Gmail inbox', '☐', 'Email monitoring (disabled)'),
        ('POST /api/v1/ats/analyze-job', 'Extract keywords', '☐', 'NLP job analysis'),
        ('POST /api/v1/ats/optimize-resume', 'Score resume', '☐', 'ATS compatibility score'),
        ('GET /api/v1/analytics/dashboard', 'Analytics data', '☐', 'Comprehensive metrics'),
    ]),

    ('=== FUTURE VISION (Activation Checkpoints) ===', [
        ('Email Automation', 'Activate at 25 applications', '☐', 'Daily inbox scanning for responses'),
        ('Analytics Dashboard', 'Use at MVD threshold (25 apps or 5 responses)', '☐', 'Pattern identification'),
        ('A/B Testing', 'Template A vs Template B comparison', '☐', 'Track in template_performance table'),
        ('Follow-up System', '7-day automated detection', '☐', 'Manual send, auto-detect need'),
        ('MCP Integration', 'Natural language control', '☐', 'backend/experimental/mcp/ servers'),
        ('ATS Optimizer', 'Pre-submission keyword analysis', '☐', 'Improve ATS pass rate'),
    ]),
]

for section_name, items in sections:
    system_data['Section'].append(section_name)
    system_data['Item'].append('')
    system_data['Path_or_Command'].append('')
    system_data['Checkbox'].append('')
    system_data['Notes'].append('')

    for item_name, path, checkbox, notes in items:
        system_data['Section'].append('')
        system_data['Item'].append(item_name)
        system_data['Path_or_Command'].append(path)
        system_data['Checkbox'].append(checkbox)
        system_data['Notes'].append(notes)

df_system = pd.DataFrame(system_data)

# TAB 3: VERSION CONTROL
print("Tab 3: Version_Control...")

version_data = {
    'Commit_Hash': ['8dda436', 'f2b881e', '5367219', '0e22006', 'cb0e81a', '7dd78a0', '4bd7388', 'c28f150', '49da024'],
    'Commit_Date': ['2025-10-09 18:47', '2025-10-09 18:01', '2025-10-09 02:46', '2025-10-09 02:22', '2025-10-09 02:12', '2025-10-09 01:57', '2025-10-09 01:09', '2025-10-09 00:58', '2025-10-09 00:55'],
    'Commit_Message': [
        'Waystar submission complete - transition to analytics',
        'Final Waystar with credibility rationale and manual context',
        'AI governance career positioning strategy',
        'Job verification utility with GEICO validation',
        'PDF converter and 4 AI applications ready',
        'Correct AI applications with accurate Humana experience',
        'Universal job addition and application generation scripts',
        'AI job pivot with GEICO and PwC additions',
        'Disable OAuth configs and add working job checker'
    ],
    'Files_Changed': [15, 13, 5, 2, 11, 7, 5, 7, 1],
    'Insertions': [1833, 1340, 633, 81, 600, 660, 389, 464, 60],
    'Deletions': [0, 740, 0, 0, 0, 0, 0, 22, 0],
    'Key_Features_Added': [
        'Cedar TAM, Brown-Forman EA, Waystar apps submitted',
        'CREDIBILITY_RATIONALE.md, positioning documented',
        'AI governance generator, interview strategy created',
        'verify_job_status.py for job posting validation',
        'convert_to_pdf.py, 4 AI applications generated',
        'Fixed claims→compliance error in all apps',
        'Universal generate_application.py, add_job_temp.py',
        'GEICO and PwC AI jobs added to database',
        'OAuth security cleanup, check_jobs_fixed.py'
    ]
}

df_version = pd.DataFrame(version_data)

# Create Excel file optimized for Numbers
output_path = '/Users/matthewscott/Desktop/Resumes/Sentinel1_Numbers_MasterControl.xlsx'

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df_apps.to_excel(writer, sheet_name='Application_Pipeline', index=False)
    df_system.to_excel(writer, sheet_name='System_Reference_for_Claude', index=False)
    df_version.to_excel(writer, sheet_name='Version_Control', index=False)

    # Get workbook and apply Numbers-friendly formatting
    workbook = writer.book

    # Application Pipeline sheet
    ws_apps = workbook['Application_Pipeline']
    ws_apps.column_dimensions['C'].width = 30  # Company Name
    ws_apps.column_dimensions['D'].width = 40  # Job Title
    ws_apps.column_dimensions['K'].width = 60  # Resume Path
    ws_apps.column_dimensions['L'].width = 60  # Cover Letter Path
    ws_apps.column_dimensions['R'].width = 60  # Notes

    # System Reference sheet
    ws_system = workbook['System_Reference_for_Claude']
    ws_system.column_dimensions['C'].width = 80  # Path/Command
    ws_system.column_dimensions['E'].width = 50  # Notes

print(f"\\nNumbers-optimized spreadsheet created:")
print(f"Location: {output_path}")
print(f"Format: .xlsx (opens natively in Apple Numbers)")
print(f"Tabs: 3 (Application_Pipeline, System_Reference_for_Claude, Version_Control)")
print(f"Column widths: Optimized for Numbers display")
print("\\nReady to open in Numbers app")

conn.close()
