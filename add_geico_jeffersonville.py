#!/usr/bin/env python3
import sqlite3
from datetime import datetime

conn = sqlite3.connect('job_search.db')
cursor = conn.cursor()

# Check/create GEICO company
cursor.execute("SELECT id FROM companies WHERE name LIKE '%GEICO%'")
result = cursor.fetchone()
if result:
    company_id = result[0]
else:
    cursor.execute("INSERT INTO companies (name, industry, website, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                  ("GEICO (Government Employees Insurance)", "Insurance/Technology", "https://www.geico.com/careers", datetime.now(), datetime.now()))
    company_id = cursor.lastrowid

# Add AI/ML NLP role
cursor.execute("""
    INSERT INTO jobs (company_id, title, job_url, location, salary_min, salary_max,
                     remote_type, priority, status, job_description, discovered_at, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (company_id,
      "AI/ML Engineer - NLP & Generative AI",
      "https://www.geico.com/careers",
      "Jeffersonville, IN",
      95000,  # Estimated based on role
      135000,
      "onsite",  # Jeffersonville location
      "HIGH",
      "new",
      "AI/ML role requiring NLP, Generative AI, LLM experience. Located in Jeffersonville, IN (adjacent to Louisville). Healthcare/insurance domain knowledge valuable. 9 years Humana claims experience directly applicable to GEICO insurance AI projects.",
      datetime.now(), datetime.now(), datetime.now()))

job_id = cursor.lastrowid
conn.commit()
conn.close()

print(f"GEICO AI/ML Engineer added - Job ID: {job_id}")
print(f"Location: Jeffersonville, IN (5 min from Louisville)")
print(f"Salary: $95-135k")
print(f"Priority: HIGH")
print(f"AI focus: NLP, Generative AI, LLMs")
print(f"Domain fit: Insurance (9 yrs Humana transfers)")
