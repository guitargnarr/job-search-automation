#!/usr/bin/env python3
"""
AI Application Generator - CORRECTED VERSION
Uses ACTUAL Humana experience: Medicare Compliance Business Analyst
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import sys

def create_ai_application(job_id):
    conn = sqlite3.connect('job_search.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT j.title, c.name, j.location, j.salary_min, j.salary_max, j.job_url
        FROM jobs j LEFT JOIN companies c ON j.company_id = c.id
        WHERE j.id = ?
    """, (job_id,))

    job = cursor.fetchone()
    if not job:
        print(f"Job #{job_id} not found")
        return False

    title, company, location, sal_min, sal_max, url = job
    company = company or "[COMPANY NAME]"

    # Create output directory
    date_str = datetime.now().strftime('%Y-%m-%d')
    company_safe = company.replace('/', '_').replace(' ', '_').replace('(','').replace(')','')[:30]
    output_dir = Path(f"applications/{date_str}_{company_safe}_AI")
    output_dir.mkdir(parents=True, exist_ok=True)

    # COVER LETTER using REAL Humana experience
    cover_letter = f"""Matthew David Scott
Louisville, KY
502-345-0525 | matthewdscott7@gmail.com

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
[COMPANY NAME]
{location}

Dear Hiring Manager,

I am writing to express my strong interest in the {title} position at [COMPANY NAME]. With 9 years as a Medicare Compliance Business Analyst at Humana, I bring a unique combination of healthcare domain expertise, data analytics skills, and proven project leadership that positions me to contribute immediately to your AI/ML initiatives.

HEALTHCARE DOMAIN EXPERTISE FOR AI PROJECTS:

At Humana (Fortune 50, serving millions of Medicare members), I developed deep expertise in the healthcare ecosystem that is critical for building accurate, compliant AI systems:

• Medicare Regulatory Knowledge: 9 years navigating CMS regulations, reviewing 400+ page Final Rule guidance annually, and ensuring compliance across enterprise platforms - understanding the regulatory constraints essential for deploying AI in healthcare

• Quality Assurance & Testing: Led data validation and testing methodologies for e-Commerce Acceleration and Data Modernization projects with ZERO critical defects - the systematic rigor needed for AI model validation and bias detection

• Healthcare Data Analysis: Used SQL to validate data integrity, identify patterns, and perform trend analysis on Medicare platform data - foundational skills for ML feature engineering and data pipeline development

• Cross-Functional Project Leadership: Coordinated Annual Enrollment Period (AEP) web marketing - Humana's highest-revenue period - managing stakeholders across IT, Legal, Compliance, and Operations at Fortune 50 scale

• Analytics-Based Testing: Developed testing methodology targeting highest-impact customer segments through data-driven experiment design - directly applicable to ML model testing and validation

TECHNICAL SKILLS & AI TRANSITION:

• SQL & Data Validation: Expert-level SQL querying for data analysis and quality assurance
• Tools: JIRA, SharePoint, Oracle, Braze, Firebase, Splunk, Power Apps/Automate
• Learning: Python for AI/ML (personal projects), machine learning fundamentals
• Methodology: Agile/SDLC, sprint planning, user stories, UAT

PROVEN TRACK RECORD:

• 100% on-time delivery for 100+ time-sensitive deliverables over 3 consecutive years as directly responsible individual (DRI)
• Led enterprise projects (e-Commerce Acceleration, Data Modernization) with zero critical defects through rigorous testing
• Built executive scorecards and analytics reporting for senior leadership decision-making
• Managed third-party audits and cross-functional coordination at scale

WHY AI/ML:

I'm excited to transition my healthcare domain expertise and analytical skills into AI/ML engineering. My 9 years at Humana provide irreplaceable knowledge of Medicare regulations, healthcare data governance, and enterprise-scale quality assurance - exactly what's needed to build compliant, accurate AI systems in healthcare. I bring immediate value through domain expertise while committed to rapidly developing technical ML/AI skills.

{f'My salary expectations align with the ${int(sal_min/1000)}k-${int(sal_max/1000)}k range.' if sal_min else ''}

I would welcome the opportunity to discuss how my Medicare compliance and data validation background can accelerate [COMPANY NAME]'s AI initiatives in healthcare.

Thank you for your consideration.

Sincerely,
Matthew David Scott
"""

    # RESUME using REAL experience
    resume = f"""MATTHEW DAVID SCOTT
Louisville, KY | 502-345-0525 | matthewdscott7@gmail.com | linkedin.com/in/mscott77/

{title.upper()}
Business Analyst Transitioning to AI/ML Engineering

PROFESSIONAL SUMMARY
Healthcare business analyst with 9 years at Humana (Fortune 50) specializing in Medicare compliance, quality assurance, and data validation. Proven track record leading enterprise projects with zero defects, performing SQL-based data analysis, and coordinating cross-functional teams. Seeking to leverage healthcare domain expertise and analytical skills for AI/ML roles. Strong foundation in testing methodologies, regulatory compliance, and data-driven decision making.

CORE COMPETENCIES
• Healthcare Domain Expert (9 years Medicare)     • SQL & Data Validation
• Quality Assurance & Testing                     • CMS Regulatory Compliance
• Cross-Functional Project Leadership             • Data Analysis & Reporting
• Analytics-Based Testing Methodology             • Enterprise Stakeholder Management
• Agile/SDLC Methodologies                        • Process Improvement
• Python (Learning - AI/ML Projects)              • Technical Documentation

PROFESSIONAL EXPERIENCE

Senior Risk Management Professional II (Business Analyst)
HUMANA, INC. | Louisville, KY | November 2022 - August 2025

Medicare Compliance & Quality Assurance Business Analyst leading regulatory compliance, data validation, and stakeholder coordination for Humana's Medicare platform serving millions of members. Subject matter expert (SME) for CMS regulations with responsibility for cross-functional project leadership and executive reporting.

KEY ACHIEVEMENTS RELEVANT TO AI/ML:

Data Validation & Quality Assurance:
• Led e-Commerce Acceleration and Data Modernization projects achieving ZERO critical or high defects through systematic testing and data validation methodologies
• Developed analytics-based testing approach targeting highest-impact customer segments through data-driven experiment design - directly applicable to ML model testing
• Used SQL extensively for data integrity validation, pattern identification, and trend analysis across Medicare platform data

Medicare Regulatory & Domain Expertise:
• Reviewed 400+ page CMS Final Rule guidance annually, identifying compliance risks and translating complex regulations into actionable business strategies
• Achieved 100% on-time delivery for 100+ time-sensitive Medicare Member Annual Communications (MAC) as directly responsible individual (DRI) for 3 consecutive years
• Deep understanding of Medicare/CMS ecosystem essential for building compliant healthcare AI systems

Project Leadership & Coordination:
• Orchestrated Annual Enrollment Period (AEP) web marketing - Humana's highest-revenue period - ensuring seamless launch through rigorous testing and cross-functional coordination
• Managed stakeholder relationships across IT, Legal, Regulatory & Compliance, and business units at Fortune 50 enterprise scale
• Built executive scorecards tracking performance metrics and trends, enabling data-informed strategic decisions

Analytics & Technical Skills:
• SQL querying for data analysis, validation, and reporting (expert level)
• Experience with enterprise tools: JIRA, Oracle, Braze, Firebase, Splunk, SharePoint, Power Apps/Automate
• Analytics-based methodology development for testing and quality assurance
• Created detailed documentation for complex processes and technical workflows

Risk Management Professional (Progressive Roles)
HUMANA, INC. | Louisville, KY | January 2016 - October 2022

9+ years of progressive experience in Medicare compliance, quality assurance, and business analysis.

Key Accomplishments:
• Built and maintained testing protocols ensuring consistent quality across all deliverables
• Performed SQL-based data validation to identify discrepancies and ensure data integrity
• Created standard operating procedures and knowledge repositories
• Handled escalated issues requiring immediate analytical resolution
• Participated in Agile ceremonies, sprint planning, and UAT coordination

Account Executive
MIGHTILY | Louisville, KY | July 2015 - December 2016

Digital marketing account manager coordinating project delivery across technical and creative teams.

• Managed 10+ digital marketing retainer accounts ($40k monthly revenue)
• Led Google AdWords campaigns using A/B testing to optimize ROI
• Created analytics reporting for clients on campaign performance
• Coordinated cross-functional teams (design, development, content)

EDUCATION & CERTIFICATIONS

Bachelor of Science in Communication | University of Louisville | Expected 2025
• Dean's List, Fall 2013
• Relevant Coursework: Data Analysis, Technical Writing, Project Management

Professional Development:
• Google Ads Certified (technical platform proficiency)
• Annual compliance and security training (2016-2025)
• Self-directed learning: Python, Machine Learning fundamentals

TECHNICAL SKILLS

Data & Analytics: SQL (MS SQL Server, MySQL, Expert), Data Validation, Trend Analysis, Executive Reporting
Tools & Platforms: JIRA, SharePoint, Oracle, Braze, Firebase, Splunk, Power Apps/Automate
Learning/Developing: Python, Machine Learning, AI/ML Frameworks
Methodologies: Agile/SDLC, Sprint Planning, UAT, Analytics-Based Testing, Root Cause Analysis

HEALTHCARE DOMAIN KNOWLEDGE (Critical for AI)
• Medicare/CMS Regulations: 9 years regulatory compliance expertise
• Healthcare Data Governance: Data validation, quality assurance, audit processes
• Healthcare IT Systems: Enterprise platforms, integration points, testing environments
• Stakeholder Management: IT, Clinical, Legal, Compliance, Operations coordination
• Quality Metrics: Performance tracking, executive reporting, trend analysis

WHY AI/ML TRANSITION:

Seeking to apply 9 years of healthcare domain expertise, data validation skills, and analytical problem-solving to AI/ML engineering. My Medicare compliance background provides critical regulatory knowledge for deploying compliant AI in healthcare. Proven ability to master complex technical systems (CMS regulations, enterprise platforms, SQL analytics) demonstrates capacity to rapidly develop ML/AI technical skills while contributing immediately through irreplaceable domain expertise.

KEY STRENGTHS:
• 9 years Medicare/healthcare domain knowledge (essential for healthcare AI)
• Proven data analysis and SQL expertise (foundation for ML work)
• Zero-defect track record through systematic testing (critical for AI validation)
• Cross-functional leadership at Fortune 50 scale
• Self-directed learner committed to continuous technical development
"""

    # Write files
    cover_path = output_dir / "Matthew_Scott_Cover_Letter.txt"
    resume_path = output_dir / "Matthew_Scott_Resume_AI_Transition.txt"
    notes_path = output_dir / "SUBMIT_INSTRUCTIONS.md"

    with open(cover_path, 'w') as f:
        f.write(cover_letter)

    with open(resume_path, 'w') as f:
        f.write(resume)

    sal_str = f"${int(sal_min/1000)}k-${int(sal_max/1000)}k" if sal_min else "TBD"

    with open(notes_path, 'w') as f:
        f.write(f"""# SUBMIT INSTRUCTIONS - Job #{job_id}

Company: {company}
Title: {title}
Salary: {sal_str}
Location: {location}
URL: {url}

BEFORE SUBMITTING:
1. Open Matthew_Scott_Cover_Letter.txt
2. Replace ALL instances of [COMPANY NAME] with "{company}"
3. Review resume Matthew_Scott_Resume_AI_Transition.txt - confirm accuracy
4. Convert .txt files to .docx if application portal requires
5. Go to: {url}
6. Submit application

AFTER SUBMITTING:
Run: python3 mark_applied.py {job_id}

KEY POSITIONING:
- 9 years Medicare Compliance Business Analyst at Humana
- Led e-Commerce Acceleration and Data Modernization projects (ZERO defects)
- SQL data validation expert
- Analytics-based testing methodology
- Cross-functional leadership at Fortune 50 scale
- Transitioning domain expertise to AI/ML

SELLING POINTS:
- Healthcare regulatory knowledge (CMS compliance)
- Data validation and quality assurance
- Project leadership with measurable results
- Technical learning ability (Google Ads Certified, self-learning Python/ML)
""")

    conn.close()

    print(f"\nCORRECTED APPLICATION GENERATED:")
    print(f"Location: {output_dir}")
    print(f"Company: {company}")
    print(f"Title: {title}")
    print(f"Salary: {sal_str}")
    print(f"\nExperience used: Medicare Compliance Business Analyst (NOT claims processing)")
    print(f"Projects: e-Commerce Acceleration, Data Modernization, AEP coordination")
    print(f"Skills: SQL data validation, analytics-based testing, regulatory compliance")
    print(f"\nNEXT: Review files, replace [COMPANY NAME], submit application")

    return str(output_dir)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 create_ai_app_CORRECTED.py <job_id>")
        print("\nHIGH PRIORITY AI JOBS:")
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT j.id, c.name, j.title, j.salary_min, j.salary_max
            FROM jobs j LEFT JOIN companies c ON j.company_id = c.id
            WHERE j.priority = 'HIGH' AND j.id >= 72
            ORDER BY j.id DESC
        """)
        for jid, comp, tit, smin, smax in cursor.fetchall():
            sal = f"${int(smin/1000)}k-${int(smax/1000)}k" if smin else "TBD"
            print(f"  #{jid}: {tit} at {comp or 'TBD'} ({sal})")
        conn.close()
        sys.exit(1)

    create_ai_application(int(sys.argv[1]))
