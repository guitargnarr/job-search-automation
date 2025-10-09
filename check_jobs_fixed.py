#!/usr/bin/env python3
"""Quick script to check current jobs in database - FIXED VERSION"""

import sqlite3

def check_jobs():
    conn = sqlite3.connect('job_search.db')
    cursor = conn.cursor()

    # Get jobs with company name via JOIN
    cursor.execute("""
        SELECT j.id, c.name as company, j.title, j.location,
               j.priority, j.salary_min, j.salary_max, j.status
        FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.id
        WHERE j.id > 4
        ORDER BY j.id DESC
        LIMIT 20
    """)
    jobs = cursor.fetchall()

    print("\n📊 REAL JOBS IN DATABASE (Last 20)\n" + "=" * 140)
    print(f"{'ID':<4} {'Company':<30} {'Title':<40} {'Location':<20} {'Priority':<10} {'Salary':<20}")
    print("-" * 140)

    for job in jobs:
        id, company, title, location, priority, sal_min, sal_max, status = job
        company = company or "Unknown"

        if sal_min and sal_max:
            salary = f"${sal_min/1000:.0f}k-${sal_max/1000:.0f}k"
        else:
            salary = "TBD"

        priority_str = priority.value if hasattr(priority, 'value') else str(priority) if priority else "MED"

        print(f"{id:<4} {company[:29]:<30} {title[:39]:<40} {location[:19]:<20} {priority_str:<10} {salary:<20}")

    # Check applications
    cursor.execute("""
        SELECT a.id, j.title, c.name, a.status, date(a.applied_date)
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        LEFT JOIN companies c ON j.company_id = c.id
    """)
    apps = cursor.fetchall()

    print("\n📝 APPLICATIONS SUBMITTED\n" + "=" * 100)
    for app in apps:
        app_id, title, company, status, applied = app
        company = company or "Unknown"
        status_str = status.value if hasattr(status, 'value') else str(status)
        print(f"  #{app_id}: {title[:50]} at {company} - {status_str} ({applied})")

    print(f"\n✅ Total: {len(apps)} applications")

    conn.close()

if __name__ == "__main__":
    check_jobs()
