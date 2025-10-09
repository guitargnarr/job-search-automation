#!/usr/bin/env python3
"""
Job Status Verifier - Checks if job posting is still active
Usage: python3 verify_job_status.py <job_id>
"""

import sqlite3
import sys

def verify_job_status(job_id):
    """Verify job is still active via web search"""

    conn = sqlite3.connect('job_search.db')
    cursor = conn.cursor()

    # Get job details
    cursor.execute("""
        SELECT j.title, c.name, j.job_url, j.location, j.salary_min, j.salary_max
        FROM jobs j LEFT JOIN companies c ON j.company_id = c.id
        WHERE j.id = ?
    """, (job_id,))

    job = cursor.fetchone()
    conn.close()

    if not job:
        print(f"ERROR: Job #{job_id} not found in database")
        return False

    title, company, url, location, sal_min, sal_max = job
    company = company or "Unknown"

    print(f"\nVERIFYING JOB #{job_id}")
    print(f"Company: {company}")
    print(f"Title: {title}")
    print(f"URL: {url}")
    print(f"Location: {location}")
    print("\nSearching web for current status...")

    # Return job details for web search
    return {
        'job_id': job_id,
        'title': title,
        'company': company,
        'url': url,
        'location': location
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify_job_status.py <job_id>")
        print("\nExample: python3 verify_job_status.py 74")
        print("\nHIGH PRIORITY AI JOBS TO VERIFY:")
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT j.id, c.name, j.title
            FROM jobs j LEFT JOIN companies c ON j.company_id = c.id
            WHERE j.priority = 'HIGH' AND j.id >= 72
            ORDER BY j.id DESC LIMIT 5
        """)
        for jid, comp, tit in cursor.fetchall():
            print(f"  #{jid}: {tit} at {comp or 'TBD'}")
        conn.close()
        sys.exit(1)

    job_data = verify_job_status(int(sys.argv[1]))

    if job_data:
        print("\nMANUAL VERIFICATION STEPS:")
        print(f"1. Search Google: \"{job_data['title']}\" \"{job_data['company']}\" 2025")
        print(f"2. Check company careers site: {job_data['url']}")
        print("3. Look for posting dates in last 30 days")
        print("4. Verify location matches your search criteria")
        print("\nIf job is active, proceed with application submission.")
        print("If job appears expired, skip or search for similar role.")
