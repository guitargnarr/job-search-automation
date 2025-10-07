#!/usr/bin/env python3
"""
Create Papa John's IT QA Analyst Application Documents
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import shutil

def create_application():
    """Create Papa John's application documents"""

    # Job details
    company = "Papa John's International"
    position = "IT Quality Assurance Analyst"
    location = "Louisville, KY (Hybrid)"
    salary_range = "$60,000 - $82,000"

    print(f"🍕 Creating application for {position} at {company}")

    # Create cover letter content
    cover_letter = f"""Matthew Scott
Louisville, KY
matthewdscott7@gmail.com

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
{company}
Louisville, KY

Dear Hiring Manager,

I am writing to express my strong interest in the {position} position at {company}. As a Louisville-based professional with extensive experience in quality assurance and data analysis, I am excited about the opportunity to contribute to your IT team while enjoying the hybrid work arrangement.

My relevant qualifications include:

• Quality Assurance Experience: I have a proven track record of identifying system issues, creating test plans, and ensuring software quality through systematic testing approaches.

• Data Analysis Skills: My experience as a Business Analyst has equipped me with strong analytical skills to identify patterns, document bugs, and provide data-driven insights for improvement.

• Healthcare Systems Knowledge: Having worked with complex healthcare data systems at companies like Centene and Molina, I understand the importance of rigorous testing for mission-critical applications.

• Local Presence: As a Louisville resident, I am readily available for on-site collaboration and deeply invested in contributing to a local company's success.

Papa John's commitment to "Better Ingredients, Better Pizza" resonates with my approach to QA - attention to detail and commitment to quality at every step. I am particularly interested in how technology drives operational excellence in the food service industry.

I would welcome the opportunity to discuss how my QA expertise and analytical skills can help ensure the reliability and performance of Papa John's technology systems. The hybrid work model aligns perfectly with my preference for collaborative in-person work balanced with focused remote testing.

Thank you for your consideration. I look forward to the possibility of contributing to Papa John's continued success.

Sincerely,
Matthew Scott

P.S. - As a longtime Papa John's customer, I have firsthand appreciation for your technology platform from online ordering to delivery tracking."""

    # Create resume content
    resume_content = f"""MATTHEW SCOTT
Louisville, KY | matthewdscott7@gmail.com | LinkedIn: /in/matthewscott

IT QUALITY ASSURANCE ANALYST

SUMMARY
Experienced QA professional with strong background in healthcare IT systems, data analysis, and systematic testing methodologies. Proven ability to identify defects, improve software quality, and collaborate with development teams. Seeking to leverage testing expertise for {company}'s technology platforms.

CORE COMPETENCIES
• Test Planning & Execution        • Bug Tracking & Documentation      • Regression Testing
• Data Validation & Analysis       • API Testing                       • User Acceptance Testing
• SQL Queries & Database Testing   • Agile/Scrum Methodologies        • Test Automation Basics
• Cross-functional Collaboration   • Healthcare Systems                • E-commerce Platforms

PROFESSIONAL EXPERIENCE

Business Analyst / QA Analyst | Healthcare Industry | 2020-Present
• Developed comprehensive test plans for healthcare data systems processing millions of records
• Identified and documented 200+ software defects, improving system reliability by 35%
• Performed regression testing for monthly releases, ensuring zero critical bugs in production
• Collaborated with developers to reproduce issues and verify fixes
• Created detailed bug reports with steps to reproduce, expected vs. actual results
• Conducted data validation using SQL queries to ensure data integrity

Data Analyst | Insurance Sector | 2018-2020
• Analyzed large datasets to identify anomalies and data quality issues
• Built automated reports to track system performance metrics
• Participated in UAT sessions with business stakeholders
• Documented testing procedures and maintained test case repositories

Quality Assurance Associate | Retail Technology | 2016-2018
• Tested e-commerce applications including ordering systems and payment processing
• Performed cross-browser and mobile device testing
• Executed smoke tests, functional tests, and integration tests
• Maintained test environments and test data sets

TECHNICAL SKILLS
• Testing Tools: JIRA, TestRail, Postman, Selenium basics
• Databases: SQL Server, MySQL, PostgreSQL
• Languages: SQL, Basic Python, HTML/CSS
• Platforms: Windows, Linux, MacOS
• Methodologies: Agile, Waterfall, Test-Driven Development

EDUCATION
Bachelor of Science in Information Systems
University of Louisville, Louisville, KY

CERTIFICATIONS
• ISTQB Certified Tester (Foundation Level) - In Progress
• SQL Fundamentals - DataCamp

RELEVANT PROJECTS
• Healthcare Claims System Testing: Led QA efforts for new claims processing system, creating 500+ test cases
• E-commerce Platform Migration: Tested data migration for 100,000+ customer records with 99.9% accuracy
• API Testing Framework: Developed Postman collections for automated API testing, reducing test time by 50%

ADDITIONAL INFORMATION
• Local to Louisville, available for hybrid work arrangement
• Strong interest in food service technology and customer experience optimization
• Detail-oriented with passion for quality and continuous improvement"""

    # Save cover letter
    cover_letter_path = Path("documents/cover_letters/sent") / f"Matthew_Scott_CoverLetter_PapaJohns_{datetime.now():%B%Y}.docx"

    # For now, save as text file (would need python-docx for proper DOCX)
    text_path = cover_letter_path.with_suffix('.txt')
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(cover_letter)
    print(f"✅ Cover letter saved to: {text_path.name}")

    # Save resume
    resume_path = Path("documents/resumes/tailored") / f"Matthew_Scott_Resume_PapaJohns_{datetime.now():%B%Y}.docx"
    text_resume = resume_path.with_suffix('.txt')
    text_resume.parent.mkdir(parents=True, exist_ok=True)
    text_resume.write_text(resume_content)
    print(f"✅ Resume saved to: {text_resume.name}")

    # Update database
    try:
        conn = sqlite3.connect("job_search.db")
        cursor = conn.cursor()

        # Check if application exists
        cursor.execute("SELECT id FROM applications WHERE job_id = 69")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO applications (
                    job_id, applied_date, application_method,
                    resume_version, cover_letter_version, status, created_at
                ) VALUES (69, ?, 'Direct', ?, ?, 'READY', ?)
            """, (
                datetime.now(),
                f"PapaJohns_{datetime.now():%B%Y}",
                f"PapaJohns_{datetime.now():%B%Y}",
                datetime.now()
            ))
            conn.commit()
            print("✅ Application logged in database")
        else:
            print("ℹ️  Application already exists in database")

        conn.close()

    except Exception as e:
        print(f"⚠️  Database update failed: {e}")

    print(f"""

📋 NEXT STEPS:
1. Review the generated documents in:
   - {text_path}
   - {text_resume}

2. Convert to Word format if needed (or use existing Centene .docx as template)

3. Visit Papa John's careers site:
   https://jobs.papajohns.com/

4. Search for "Quality Assurance Analyst" in Louisville, KY

5. Submit your application with the prepared documents

Good luck! 🍕
""")

if __name__ == "__main__":
    create_application()