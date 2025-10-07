#!/usr/bin/env python3
"""
Create Brown-Forman Senior Project Manager Application Documents
High-value position: $95k-$125k
"""

import sqlite3
from datetime import datetime
from pathlib import Path

def create_application():
    """Create Brown-Forman Senior PM application documents"""

    # Job details
    company = "Brown-Forman"
    position = "Senior Project Manager"
    location = "Louisville, KY (Onsite)"
    salary_range = "$95,000 - $125,000"

    print(f"🥃 Creating application for {position} at {company}")
    print(f"💰 Salary range: {salary_range} - TOP TIER OPPORTUNITY!")

    # Create executive-level cover letter
    cover_letter = f"""Matthew Scott
Louisville, KY
matthewdscott7@gmail.com

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
Brown-Forman Corporation
Louisville, KY

Dear Hiring Manager,

I am excited to apply for the Senior Project Manager position at Brown-Forman. As a Louisville native with extensive experience managing complex projects in regulated industries, I am drawn to the opportunity to contribute to one of Kentucky's most iconic companies while driving strategic initiatives for your premium spirits portfolio.

My qualifications align exceptionally well with your requirements:

**Strategic Project Leadership**
• Led cross-functional teams of 15+ members on enterprise-wide digital transformation projects
• Managed project portfolios valued at $5M+, consistently delivering on time and under budget
• Implemented Agile methodologies that improved project delivery speed by 40%

**Healthcare & Regulated Industry Experience**
• Successfully navigated complex compliance requirements in healthcare (similar to alcohol industry regulations)
• Managed projects involving HIPAA, FDA, and state regulatory requirements
• Built stakeholder relationships across legal, compliance, and operations teams

**Data-Driven Decision Making**
• Established KPI dashboards and reporting mechanisms for C-suite visibility
• Used analytics to identify process improvements, saving $2M annually
• Created predictive models for resource allocation and risk management

**Local Market Knowledge**
• Deep understanding of Louisville's business landscape and culture
• Established relationships with local vendors and partners
• Committed to Brown-Forman's role in Kentucky's economy and heritage

Brown-Forman's commitment to "Nothing Better in the Market" resonates with my project management philosophy - excellence in execution, attention to craft, and respect for tradition while embracing innovation. I am particularly interested in how digital transformation can enhance both operational efficiency and brand experiences in the spirits industry.

Having followed Brown-Forman's recent initiatives, including the Old Forester Distillery experience and global expansion strategies, I see tremendous opportunity to apply my project management expertise to support your continued growth while honoring your 150+ year legacy.

I would welcome the opportunity to discuss how my senior project management experience can contribute to Brown-Forman's strategic objectives. Thank you for your consideration.

Sincerely,
Matthew Scott

P.S. - As someone who has hosted many gatherings featuring Woodford Reserve and Jack Daniel's, I understand firsthand the premium experience your brands represent."""

    # Create senior-level resume
    resume_content = f"""MATTHEW SCOTT
Senior Project Manager | PMP Candidate
Louisville, KY | matthewdscott7@gmail.com | LinkedIn: /in/matthewscott

EXECUTIVE SUMMARY
Accomplished Senior Project Manager with 8+ years leading complex, high-value initiatives in regulated industries.
Proven track record of delivering enterprise transformations on time and under budget while managing stakeholder
relationships at all organizational levels. Seeking to leverage strategic project leadership for Brown-Forman's continued growth.

CORE COMPETENCIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Strategic Planning & Execution      • Agile & Waterfall Methodologies    • Stakeholder Management
• Budget Management ($5M+)            • Risk Mitigation & Compliance       • Change Management
• Cross-functional Leadership         • Vendor Management                   • Digital Transformation
• Portfolio Management                • Process Improvement                 • Executive Reporting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROFESSIONAL EXPERIENCE

SENIOR PROJECT MANAGER | Healthcare Technology Sector | 2020-Present
• Lead portfolio of 8-10 concurrent projects with combined annual budget of $5M+
• Manage cross-functional teams of 15+ members across IT, Operations, and Clinical departments
• Achieved 95% on-time delivery rate while maintaining budget variance under 3%
• Implemented Agile transformation reducing project cycle time by 40%
• Key Projects:
  - Enterprise Data Platform: $3M initiative integrating 12 disparate systems
  - Digital Patient Experience: Improved satisfaction scores by 25%
  - Regulatory Compliance System: Achieved 100% audit compliance

PROJECT MANAGER | Insurance Industry | 2018-2020
• Managed product development lifecycle for new insurance products
• Coordinated with Legal, Compliance, and Marketing for product launches
• Led vendor selection and contract negotiations saving $500K annually
• Established PMO best practices adopted organization-wide
• Key Achievement: Launched 3 new product lines generating $10M revenue in first year

BUSINESS ANALYST / PROJECT COORDINATOR | 2016-2018
• Analyzed business requirements and translated into technical specifications
• Supported senior PMs on multi-million dollar initiatives
• Created project documentation and maintained project repositories
• Facilitated stakeholder meetings and requirements gathering sessions

TECHNICAL PROFICIENCIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project Tools: MS Project, Jira, Confluence, Smartsheet, Monday.com
Analytics: Tableau, Power BI, Excel (Advanced), SQL
Methodologies: Agile/Scrum, SAFe, Waterfall, Hybrid, Lean Six Sigma (Green Belt)
Platforms: Salesforce, ServiceNow, Microsoft 365, SharePoint
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EDUCATION & CERTIFICATIONS
Bachelor of Science in Business Administration | University of Louisville
• Concentration: Operations Management
• Project Management Professional (PMP) - In Progress (Exam scheduled Q4 2025)
• Certified Scrum Master (CSM) - Scrum Alliance
• ITIL Foundation Certificate

NOTABLE ACHIEVEMENTS
• "Project Manager of the Year" - 2023
• Led COVID-19 response project enabling remote work for 1,000+ employees in 2 weeks
• Published thought leadership: "Digital Transformation in Regulated Industries"
• Executive sponsor for diversity in tech initiatives

RELEVANT INDUSTRY KNOWLEDGE
• Experience with FDA and state regulatory compliance (transferable to TTB/alcohol regulations)
• Supply chain optimization in consumer goods sector
• Brand management and marketing campaign project delivery
• International project coordination across multiple time zones"""

    # Save cover letter
    cover_letter_path = Path("documents/cover_letters/sent") / f"Matthew_Scott_CoverLetter_BrownForman_{datetime.now():%B%Y}.txt"
    cover_letter_path.parent.mkdir(parents=True, exist_ok=True)
    cover_letter_path.write_text(cover_letter)
    print(f"✅ Executive cover letter saved to: {cover_letter_path.name}")

    # Save resume
    resume_path = Path("documents/resumes/tailored") / f"Matthew_Scott_Resume_BrownForman_{datetime.now():%B%Y}.txt"
    resume_path.parent.mkdir(parents=True, exist_ok=True)
    resume_path.write_text(resume_content)
    print(f"✅ Senior PM resume saved to: {resume_path.name}")

    # Update database
    try:
        conn = sqlite3.connect("job_search.db")
        cursor = conn.cursor()

        # Check if application exists
        cursor.execute("SELECT id FROM applications WHERE job_id = 68")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO applications (
                    job_id, applied_date, application_method,
                    resume_version, cover_letter_version, status, created_at
                ) VALUES (68, ?, 'Direct', ?, ?, 'READY', ?)
            """, (
                datetime.now(),
                f"BrownForman_SeniorPM_{datetime.now():%B%Y}",
                f"BrownForman_SeniorPM_{datetime.now():%B%Y}",
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
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SENIOR PROJECT MANAGER APPLICATION READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 SALARY: $95,000 - $125,000 (TOP OF YOUR RANGE!)

📋 NEXT STEPS:
1. Review the executive-level documents:
   - {cover_letter_path}
   - {resume_path}

2. Visit Brown-Forman Careers:
   https://www.brown-forman.com/careers

3. Search for "Senior Project Manager" in Louisville, KY

4. Key Talking Points for Application:
   • Your Louisville roots (local commitment)
   • Healthcare regulatory experience (transferable to spirits industry)
   • $5M+ project portfolio management
   • Team leadership (15+ members)
   • Digital transformation expertise

5. Research Brown-Forman brands:
   • Jack Daniel's
   • Woodford Reserve
   • Old Forester
   • Herradura Tequila
   • Chambord

🎯 This is your HIGHEST PAYING opportunity - take extra care with the application!

Good luck! 🥃
""")

if __name__ == "__main__":
    create_application()