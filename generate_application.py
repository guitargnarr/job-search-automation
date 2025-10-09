#!/usr/bin/env python3
"""
Universal Application Generator
Generates tailored resume + cover letter for any job in database
Usage: python3 generate_application.py <job_id> <resume_template>
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path
import shutil

def generate_application(job_id, resume_template="Template5"):
    """Generate application package from database job"""

    # Connect to database
    conn = sqlite3.connect('job_search.db')
    cursor = conn.cursor()

    # Get job with company info
    cursor.execute("""
        SELECT j.id, j.title, c.name, j.location, j.salary_min, j.salary_max,
               j.remote_type, j.job_url, j.priority, j.job_description
        FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.id
        WHERE j.id = ?
    """, (job_id,))

    job = cursor.fetchone()

    if not job:
        print(f"ERROR: Job ID {job_id} not found in database")
        conn.close()
        return False

    job_id, title, company, location, sal_min, sal_max, remote_type, url, priority, description = job
    company = company or "Unknown Company"

    # Format salary
    if sal_min and sal_max:
        salary_range = f"${sal_min/1000:.0f}k-${sal_max/1000:.0f}k"
    else:
        salary_range = "TBD"

    print(f"\n📝 Generating application for Job #{job_id}")
    print(f"   Company: {company}")
    print(f"   Title: {title}")
    print(f"   Salary: {salary_range}")
    print(f"   Location: {location}")

    # Create output directory
    date_str = datetime.now().strftime('%Y-%m-%d')
    company_safe = company.replace('/', '_').replace(' ', '_').replace(',','')[:30]
    output_dir = Path(f"applications/{date_str}_{company_safe}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"   Output: {output_dir}")

    # Generate cover letter
    cover_letter = f"""Matthew Scott
Louisville, KY
matthewdscott7@gmail.com

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
{company}
{location}

Dear Hiring Manager,

I am writing to express my strong interest in the {title} position at {company}. With 9 years of experience in healthcare data analytics, claims processing, and regulatory compliance, I am confident I can contribute immediately to your team's success.

My relevant qualifications include:

HEALTHCARE DOMAIN EXPERTISE:
• 9 years working with Medicare Advantage, Star Ratings, HEDIS, and compliance data
• Deep understanding of claims processing, medical billing, and healthcare workflows
• Experience with CMS regulations, compliance reporting, and quality metrics

ANALYTICAL & TECHNICAL SKILLS:
• Advanced SQL, data analysis, and reporting
• Process improvement and workflow optimization
• Cross-functional collaboration with clinical, operations, and compliance teams

{f'COMPENSATION: My salary expectation aligns with the {salary_range} range for this role.' if sal_min else ''}

I am excited about the opportunity to leverage my healthcare domain expertise to contribute to {company}'s mission. I would welcome the chance to discuss how my background can support your team's objectives.

Thank you for your consideration.

Sincerely,
Matthew Scott
"""

    # Generate resume content (simplified - uses template approach)
    resume_content = f"""MATTHEW SCOTT
Louisville, KY | matthewdscott7@gmail.com

{title.upper()}

PROFESSIONAL SUMMARY
Healthcare analytics professional with 9 years of experience in Medicare Advantage, claims processing, regulatory compliance, and data analysis. Proven track record of delivering insights that drive operational improvements and ensure regulatory compliance. Strong technical skills in SQL, data visualization, and cross-functional collaboration.

CORE COMPETENCIES
• Healthcare Data Analysis (9 years)     • Medicare/Medicaid Programs          • Claims & Medical Billing
• Regulatory Compliance (CMS, HEDIS)     • SQL & Database Querying             • Process Improvement
• Star Ratings & Quality Metrics         • Cross-Functional Leadership         • Stakeholder Management
• Data Visualization & Reporting         • Problem Solving & Analytics         • Healthcare IT Systems

PROFESSIONAL EXPERIENCE

Senior Healthcare Analyst | Healthcare Insurance | 2016-Present
• Analyzed Medicare Advantage data for 300,000+ members, ensuring compliance with CMS Star Ratings
• Led compliance reporting initiatives with 100% on-time delivery of CMS submissions
• Collaborated with clinical, operations, and compliance teams on quality improvement projects
• Developed SQL queries and reports to identify trends, gaps, and improvement opportunities
• Managed regulatory deliverables including HEDIS, Stars, and audit responses

Business Analyst | Insurance & Healthcare | 2014-2016
• Supported implementation of new healthcare programs and system enhancements
• Analyzed claims data to identify processing errors and recommend corrections
• Created documentation for business processes and technical requirements
• Worked with IT teams on system testing and validation

EDUCATION
Bachelor of Arts (BA) | Business Administration
Relevant coursework in data analysis, statistics, and information systems

TECHNICAL SKILLS
• Tools: SQL, Excel, Tableau, Power BI, JIRA
• Healthcare Systems: Claims platforms, EHR systems, compliance tools
• Methodologies: Agile, Lean Six Sigma, Process Improvement

ACHIEVEMENTS
• 100% on-time CMS submissions over 9-year period
• Led Medicare compliance initiatives affecting 300,000+ members
• Identified $2M+ in potential compliance gaps through proactive data analysis
"""

    # Write files
    cover_letter_path = output_dir / "Matthew_Scott_Cover_Letter.txt"
    resume_path = output_dir / "Matthew_Scott_Resume_Tailored.txt"
    notes_path = output_dir / "application_notes.md"

    with open(cover_letter_path, 'w') as f:
        f.write(cover_letter)

    with open(resume_path, 'w') as f:
        f.write(resume_content)

    with open(notes_path, 'w') as f:
        f.write(f"""# Application Notes

**Job ID**: {job_id}
**Company**: {company}
**Title**: {title}
**Salary**: {salary_range}
**Location**: {location}
**URL**: {url}
**Priority**: {priority}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Next Steps:
1. Review resume and cover letter for accuracy
2. Convert to DOCX if needed
3. Submit application at: {url}
4. Run: python3 mark_applied.py {job_id}
""")

    print(f"\n✅ Application package created:")
    print(f"   Cover Letter: {cover_letter_path}")
    print(f"   Resume: {resume_path}")
    print(f"   Notes: {notes_path}")

    # Mark as READY in database
    cursor.execute("UPDATE jobs SET status = 'ready_to_apply' WHERE id = ?", (job_id,))

    # Create application record
    cursor.execute("""
        INSERT INTO applications (job_id, status, created_at, updated_at)
        VALUES (?, 'READY', ?, ?)
    """, (job_id, datetime.now(), datetime.now()))

    conn.commit()
    conn.close()

    print(f"\n✅ Job #{job_id} marked as READY in database")
    print(f"\nNEXT: Review files in {output_dir}/ then submit application")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_application.py <job_id> [resume_template]")
        print("\nExample: python3 generate_application.py 71 Template5")
        print("\nHIGH PRIORITY JOBS:")
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT j.id, c.name, j.title, j.salary_min, j.salary_max
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.id
            WHERE j.priority = 'HIGH'
            ORDER BY j.id DESC
            LIMIT 5
        """)
        for job in cursor.fetchall():
            jid, comp, tit, smin, smax = job
            comp = comp or "Unknown"
            sal = f"${smin/1000:.0f}k-${smax/1000:.0f}k" if smin and smax else "TBD"
            print(f"  #{jid}: {tit} at {comp} ({sal})")
        conn.close()
        sys.exit(1)

    job_id = int(sys.argv[1])
    template = sys.argv[2] if len(sys.argv) > 2 else "Template5"

    generate_application(job_id, template)
