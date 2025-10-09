#!/usr/bin/env python3
"""
Quick job addition script - accepts job details and adds to database
Usage: python3 add_job_temp.py
"""

import sqlite3
from datetime import datetime

def add_job(title, company, salary_min, salary_max, location, remote_type, job_url, priority="HIGH", notes=""):
    """Add job to database with company creation if needed"""

    conn = sqlite3.connect('job_search.db')
    cursor = conn.cursor()

    # Check if company exists
    cursor.execute("SELECT id FROM companies WHERE name = ?", (company,))
    result = cursor.fetchone()

    if result:
        company_id = result[0]
        print(f"Using existing company ID: {company_id}")
    else:
        # Create company
        cursor.execute("INSERT INTO companies (name, created_at, updated_at) VALUES (?, ?, ?)",
                      (company, datetime.now(), datetime.now()))
        company_id = cursor.lastrowid
        print(f"Created new company: {company} (ID: {company_id})")

    # Add job
    cursor.execute("""
        INSERT INTO jobs (company_id, title, job_url, location, salary_min, salary_max,
                         remote_type, priority, status, discovered_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?, ?)
    """, (company_id, title, job_url, location, salary_min, salary_max, remote_type,
          priority, datetime.now(), datetime.now(), datetime.now()))

    job_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f"\n✅ Job added successfully!")
    print(f"   Job ID: {job_id}")
    print(f"   Company: {company}")
    print(f"   Title: {title}")
    print(f"   Salary: ${salary_min:,}-${salary_max:,}" if salary_min and salary_max else "   Salary: TBD")
    print(f"   Location: {location}")
    print(f"   Priority: {priority}")

    return job_id

if __name__ == "__main__":
    # Example: Add Cedar Data Scientist III role
    add_job(
        title="Data Scientist III - ML Engineering (Healthcare)",
        company="Cedar (Healthcare Fintech)",
        salary_min=110000,
        salary_max=150000,
        location="Remote (US)",
        remote_type="remote",
        job_url="https://www.cedar.com/careers",
        priority="HIGH",
        notes="ML solutions for healthcare platform. 9 yrs healthcare exp applies."
    )

    # Example: Add AI Product Owner role
    add_job(
        title="AI Product Owner - Healthcare Claims/LLM",
        company="Healthcare Tech (TBD)",
        salary_min=100000,
        salary_max=140000,
        location="Remote (US)",
        remote_type="remote",
        job_url="https://www.indeed.com/",
        priority="HIGH",
        notes="AI-driven claims analysis, medical billing. Perfect for healthcare domain exp."
    )
