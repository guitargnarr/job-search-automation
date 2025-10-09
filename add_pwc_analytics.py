#!/usr/bin/env python3
import sqlite3
from datetime import datetime

conn = sqlite3.connect('job_search.db')
cursor = conn.cursor()

# Check/create PwC company
cursor.execute("SELECT id FROM companies WHERE name LIKE '%PwC%' OR name LIKE '%PricewaterhouseCoopers%'")
result = cursor.fetchone()
if result:
    company_id = result[0]
else:
    cursor.execute("INSERT INTO companies (name, industry, website, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                  ("PwC (PricewaterhouseCoopers)", "Consulting", "https://www.pwc.com/us/en/careers.html", datetime.now(), datetime.now()))
    company_id = cursor.lastrowid

# Add Data & Analytics Engineering role
cursor.execute("""
    INSERT INTO jobs (company_id, title, job_url, location, salary_min, salary_max,
                     remote_type, priority, status, job_description, discovered_at, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (company_id,
      "Data & Analytics Engineer - AI/ML",
      "https://www.pwc.com/us/en/careers.html",
      "Remote (Louisville office option)",
      100000,
      145000,
      "remote",
      "HIGH",
      "new",
      "Data/Analytics engineering with AI/ML focus. Big 4 consulting. Healthcare practice likely. Remote with Louisville office access. 9 years healthcare data experience positions well for healthcare consulting AI projects.",
      datetime.now(), datetime.now(), datetime.now()))

job_id = cursor.lastrowid
conn.commit()
conn.close()

print(f"PwC Data & Analytics Engineer added - Job ID: {job_id}")
print(f"Location: Remote (Louisville office available)")
print(f"Salary: $100-145k")
print(f"Priority: HIGH")
print(f"Focus: AI/ML, Big 4 consulting")
print(f"Domain fit: Healthcare practice")
