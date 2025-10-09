#!/usr/bin/env python3
"""
AI Analyst Application Generator
Leverages 9 years Humana healthcare experience for AI-centered roles
Uses placeholders for manual company insertion
"""

import sqlite3
from datetime import datetime
from pathlib import Path

def create_ai_application(job_id):
    conn = sqlite3.connect('job_search.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT j.title, c.name, j.location, j.salary_min, j.salary_max, j.job_url
        FROM jobs j LEFT JOIN companies c ON j.company_id = c.id
        WHERE j.id = ?
    """, (job_id,))

    job = cursor.fetchone()
    title, company, location, sal_min, sal_max, url = job
    company = company or "[Company Name]"

    # Create output directory
    date_str = datetime.now().strftime('%Y-%m-%d')
    company_safe = company.replace('/', '_').replace(' ', '_')[:30]
    output_dir = Path(f"applications/{date_str}_{company_safe}_AI")
    output_dir.mkdir(parents=True, exist_ok=True)

    # COVER LETTER - Leverages Humana experience without naming target company
    cover_letter = f"""Matthew Scott
Louisville, KY
matthewdscott7@gmail.com

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
[COMPANY NAME]
{location}

Dear Hiring Manager,

I am writing to express my strong interest in the {title} position. With 9 years of progressive experience in healthcare data analytics, claims processing, and AI-driven quality improvement, I am excited to apply my domain expertise to [COMPANY NAME]'s AI initiatives.

HEALTHCARE AI DOMAIN EXPERTISE (9 Years):

At my previous role with a major health insurer (Medicare Advantage, 300,000+ members), I developed deep expertise that directly applies to AI/ML projects in healthcare:

• Claims Data Analysis: Analyzed millions of medical claims, diagnosis codes (ICD-10), procedure codes (CPT/HCPCS), and provider data - the exact data that powers healthcare AI models

• Regulatory Compliance & Quality Metrics: Managed CMS Star Ratings, HEDIS measures, and compliance reporting - understanding the regulatory context critical for healthcare AI deployment

• Clinical Data Understanding: Worked with clinical teams on quality improvement, medical necessity reviews, and care gap analysis - providing the clinical context needed for accurate AI model training

• Healthcare Workflows: Deep knowledge of claims adjudication, prior authorization, medical billing, and member services - the business processes AI seeks to optimize

AI-RELEVANT TECHNICAL SKILLS:

• Data Pipeline Experience: Built SQL queries processing millions of records, identifying patterns and anomalies - foundational skills for ML feature engineering

• Process Optimization: Led initiatives that automated manual processes and improved data quality - the mindset needed for AI implementation

• Cross-Functional Leadership: Collaborated with clinical, IT, compliance, and operations teams - essential for AI product development requiring diverse stakeholder input

• Analytical Problem-Solving: Identified $2M+ in compliance gaps through proactive data analysis - demonstrating the analytical rigor needed for AI model validation

WHY THIS ROLE:

I am specifically drawn to AI roles in healthcare because I understand the domain challenges:
- Medical data complexity (diagnosis coding, drug formularies, provider networks)
- Regulatory constraints (HIPAA, CMS requirements)
- Clinical accuracy requirements (patient safety implications)
- Healthcare stakeholder dynamics (providers, members, payers)

This domain knowledge, combined with my analytical background and eagerness to apply AI/ML technologies, positions me to contribute immediately to [COMPANY NAME]'s healthcare AI projects.

{f'My salary expectations align with the ${sal_min/1000:.0f}k-${sal_max/1000:.0f}k range for this role.' if sal_min and sal_max else ''}

I would welcome the opportunity to discuss how my 9 years of healthcare data experience can accelerate [COMPANY NAME]'s AI initiatives. I am committed to continuous learning and excited to deepen my technical AI/ML skills while leveraging my irreplaceable domain expertise.

Thank you for your consideration.

Sincerely,
Matthew Scott
"""

    # RESUME - AI-focused but leveraging healthcare experience
    resume = f"""MATTHEW SCOTT
Louisville, KY | matthewdscott7@gmail.com | LinkedIn: linkedin.com/in/matthewscott

{title.upper()}
Transitioning Healthcare Data Analyst to AI/ML Engineering

PROFESSIONAL SUMMARY
Healthcare data professional with 9 years of hands-on experience analyzing medical claims, diagnosis codes, and quality metrics for 300,000+ Medicare Advantage members. Seeking to leverage deep healthcare domain expertise to contribute to AI/ML projects in insurance, healthcare technology, or consulting. Strong analytical foundation with proven track record of data-driven problem solving and cross-functional collaboration.

CORE COMPETENCIES
• Healthcare Domain Expert (9 years)        • Claims & Medical Billing Data
• SQL & Data Analysis                       • Medicare/Medicaid Regulatory Knowledge
• Healthcare AI Use Cases Understanding     • Clinical Data & Diagnosis Codes (ICD-10)
• Data Quality & Process Improvement        • Cross-Functional Team Leadership
• CMS Star Ratings & HEDIS                  • Analytical Problem Solving
• Python (Learning - Personal Projects)     • Healthcare Stakeholder Management

PROFESSIONAL EXPERIENCE

Senior Healthcare Data Analyst | Major Health Insurer (Medicare Advantage) | 2016-2025
9 years of progressive experience working with the exact data that powers healthcare AI/ML models

HEALTHCARE DATA & AI-RELEVANT EXPERIENCE:
• Analyzed millions of medical claims containing diagnosis codes (ICD-10), procedure codes (CPT/HCPCS), drug data (NDC), and provider information - the foundational datasets for training healthcare AI models

• Led CMS Star Ratings compliance for 300,000+ Medicare members, requiring deep understanding of quality metrics, care gaps, and member outcomes - the exact business problems AI seeks to solve

• Collaborated with clinical teams on medical necessity reviews and care management - providing clinical context essential for accurate AI model development in healthcare

• Built complex SQL queries to identify patterns, anomalies, and trends across large healthcare datasets - experience directly applicable to ML feature engineering

• Managed regulatory deliverables (HEDIS, Stars, audit responses) with 100% on-time delivery over 9 years - understanding compliance constraints for AI deployment in regulated healthcare

• Identified $2M+ in potential compliance gaps through proactive data analysis - demonstrating analytical rigor needed for AI model validation and bias detection

PROCESS IMPROVEMENT & AUTOMATION:
• Led initiatives to automate manual reporting processes, improving efficiency by 40%
• Developed standardized data validation procedures reducing errors by 60%
• Created documentation for complex healthcare workflows and business requirements

CROSS-FUNCTIONAL LEADERSHIP:
• Collaborated with IT, clinical, operations, and compliance teams on enterprise initiatives
• Presented data insights to senior leadership to drive strategic decisions
• Trained team members on regulatory requirements and data analysis techniques

EDUCATION
Bachelor of Arts (BA) | Business Administration
Relevant coursework: Statistics, Data Analysis, Information Systems

TECHNICAL SKILLS
• Data Analysis: SQL (Expert), Excel (Advanced), Tableau, Power BI
• Healthcare Systems: Claims platforms, EHR systems, compliance databases
• Learning: Python (personal AI/ML projects), Machine Learning fundamentals
• Methodologies: Agile, Lean Six Sigma, Root Cause Analysis

HEALTHCARE DOMAIN KNOWLEDGE (Critical for AI Projects)
• Claims Processing: Medical, pharmacy, dental claims adjudication workflows
• Medical Coding: ICD-10 diagnosis codes, CPT procedure codes, DRG groupings
• Regulatory: CMS regulations, HEDIS specifications, Medicare Advantage rules
• Clinical: Care management, disease management, quality improvement programs
• Healthcare IT: Claims systems, provider networks, formularies, benefit design

ACHIEVEMENTS
• 9 years managing Medicare Advantage Star Ratings data affecting 300,000+ members
• 100% on-time delivery of all CMS regulatory submissions (9-year track record)
• Identified $2M+ in compliance gaps through proactive SQL-based data analysis
• Led cross-functional teams on quality improvement initiatives with measurable outcomes

WHY AI/ML:
Excited to transition technical healthcare expertise into AI/ML engineering. My 9 years of healthcare data experience provides irreplaceable domain knowledge for training accurate, compliant AI models. Committed to continuous learning in Python, ML frameworks, and AI technologies while contributing immediately through domain expertise.
"""

    # Write files with placeholders
    cover_path = output_dir / "Matthew_Scott_Cover_Letter.txt"
    resume_path = output_dir / "Matthew_Scott_Resume_AI_Healthcare.txt"
    notes_path = output_dir / "application_notes.md"

    with open(cover_path, 'w') as f:
        f.write(cover_letter)

    with open(resume_path, 'w') as f:
        f.write(resume)

    with open(notes_path, 'w') as f:
        f.write(f"""# AI Role Application

Job ID: {job_id}
Company: {company}
Title: {title}
Salary: ${sal_min/1000:.0f}k-${sal_max/1000:.0f}k
Location: {location}
URL: {url}

MANUAL STEPS BEFORE SUBMITTING:
1. Replace [COMPANY NAME] with actual company name in cover letter
2. Review resume - confirm 9 years Humana experience positioning is clear
3. Convert .txt to .docx if needed
4. Submit at: {url}
5. Run: python3 mark_applied.py {job_id}

KEY SELLING POINTS:
- 9 years healthcare claims data (perfect for healthcare AI training data)
- Regulatory knowledge (CMS, HEDIS) - critical for compliant AI deployment
- Clinical collaboration - provides clinical context for AI models
- Domain expert transitioning to AI/ML - brings irreplaceable healthcare knowledge
""")

    conn.close()

    print(f"\nAI Application Package Created: {output_dir}")
    print("Cover letter and resume leverage 9 years Humana experience")
    print("Placeholders: [COMPANY NAME] - replace before submitting")

    return output_dir

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 create_ai_analyst_application.py <job_id>")
        print("\nAI JOBS READY FOR APPLICATION:")
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT j.id, c.name, j.title, j.location
            FROM jobs j LEFT JOIN companies c ON j.company_id = c.id
            WHERE (j.title LIKE '%AI%' OR j.title LIKE '%ML%' OR j.title LIKE '%Data Scientist%')
            AND j.priority = 'HIGH'
            ORDER BY j.id DESC
        """)
        for jid, comp, tit, loc in cursor.fetchall():
            print(f"  #{jid}: {tit} at {comp or 'TBD'} ({loc})")
        conn.close()
        sys.exit(1)

    create_ai_application(int(sys.argv[1]))
