#!/usr/bin/env python3
"""
Validate All Existing Jobs - IMMEDIATE UTILITY
Uses YOUR existing pattern: direct SQLite access (like check_jobs.py)

This script:
1. Connects to job_search.db directly (no async complexity)
2. Fetches all jobs with URLs
3. Validates each URL using JobValidator
4. Updates database with verification results
5. Prints summary of REAL vs FAKE jobs

Run this TODAY to check your 81 existing jobs.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.job_validator import job_validator  # noqa: E402


def validate_all_jobs():
    """Main validation function using YOUR sqlite3 pattern"""

    # Connect to database (YOUR pattern from check_jobs.py)
    conn = sqlite3.connect('job_search.db')
    cursor = conn.cursor()

    print("\n" + "=" * 100)
    print("🔍 JOB VALIDATION: Checking All Existing Jobs")
    print("=" * 100 + "\n")

    # First, add columns if they don't exist (safe migration)
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN verified_status TEXT")
        cursor.execute("ALTER TABLE jobs ADD COLUMN last_verified TEXT")
        conn.commit()
        print("✅ Added verification columns to database\n")
    except sqlite3.OperationalError:
        # Columns already exist
        pass

    # Fetch all jobs with URLs
    cursor.execute("""
        SELECT j.id, c.name, j.title, j.job_url, j.location, j.salary_min, j.salary_max,
               j.verified_status, j.status, j.priority
        FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.id
        WHERE j.job_url IS NOT NULL AND j.job_url != ''
        ORDER BY j.id DESC
    """)

    jobs = cursor.fetchall()

    if not jobs:
        print("⚠️  No jobs with URLs found in database")
        conn.close()
        return

    print(f"Found {len(jobs)} jobs to validate\n")

    # Validation counters
    total_checked = 0
    open_count = 0
    closed_count = 0
    not_found_count = 0
    error_count = 0

    # Validate each job
    for job_data in jobs:
        job_id, company, title, job_url, location, sal_min, sal_max, current_verified, job_status, priority = job_data
        company = company or "Unknown"

        total_checked += 1

        # Call the validator
        validation = job_validator.validate_job_url(job_url)

        # Determine verification status
        if validation['exists'] and validation['appears_open']:
            verified_status = "OPEN"
            status_icon = "✅"
            open_count += 1
        elif validation['exists'] and not validation['appears_open']:
            verified_status = "CLOSED"
            status_icon = "❌"
            closed_count += 1
        elif validation['status_code'] == 404:
            verified_status = "NOT_FOUND"
            status_icon = "🚫"
            not_found_count += 1
        else:
            verified_status = "ERROR"
            status_icon = "⚠️ "
            error_count += 1

        # Update database with verification results
        cursor.execute("""
            UPDATE jobs
            SET verified_status = ?,
                last_verified = ?
            WHERE id = ?
        """, (verified_status, datetime.now().isoformat(), job_id))

        # Print result
        print(f"{status_icon} {verified_status:12s} | ID:{job_id:3d} | {company[:25]:25s} | {title[:40]:40s}")
        print(f"   └ Source: {validation['source']:30s} | Reason: {validation['reason']}")
        print(f"   └ URL: {job_url[:80]}")
        print()

    # Commit all updates
    conn.commit()

    # Summary
    print("=" * 100)
    print("📊 VALIDATION SUMMARY")
    print("=" * 100)
    print(f"Total Jobs Checked:     {total_checked}")
    print(f"  ✅ OPEN:              {open_count} ({open_count / total_checked * 100:.1f}%)")
    print(f"  ❌ CLOSED:            {closed_count} ({closed_count / total_checked * 100:.1f}%)")
    print(f"  🚫 NOT FOUND (404):   {not_found_count} ({not_found_count / total_checked * 100:.1f}%)")
    print(f"  ⚠️  ERRORS:            {error_count} ({error_count / total_checked * 100:.1f}%)")
    print()

    # Show which jobs you should focus on
    if open_count > 0:
        print("🎯 VERIFIED OPEN JOBS (Ready to Apply):")
        cursor.execute("""
            SELECT j.id, c.name, j.title, j.priority, j.salary_max
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.id
            WHERE j.verified_status = 'OPEN'
            ORDER BY
                CASE j.priority
                    WHEN 'HIGH' THEN 1
                    WHEN 'MEDIUM' THEN 2
                    WHEN 'LOW' THEN 3
                    ELSE 4
                END,
                j.salary_max DESC NULLS LAST
            LIMIT 10
        """)

        open_jobs = cursor.fetchall()
        for jid, comp, tit, pri, sal in open_jobs:
            priority_str = pri or "MEDIUM"
            salary_str = f"${sal:,}" if sal else "Unknown"
            print(f"  #{jid:3d} [{priority_str:6s}] {tit[:45]:45s} @ {comp or 'Unknown'} (Max: {salary_str})")

    # Show jobs that need to be removed
    if closed_count + not_found_count > 0:
        print(f"\n🗑️  JOBS TO REMOVE (Closed/Fake - {closed_count + not_found_count} total):")
        cursor.execute("""
            SELECT j.id, c.name, j.title, j.verified_status
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.id
            WHERE j.verified_status IN ('CLOSED', 'NOT_FOUND')
            ORDER BY j.id DESC
            LIMIT 10
        """)

        dead_jobs = cursor.fetchall()
        for jid, comp, tit, vstatus in dead_jobs:
            print(f"  #{jid:3d} [{vstatus:9s}] {tit[:45]:45s} @ {comp or 'Unknown'}")

    print("\n" + "=" * 100)
    print("✅ Validation complete. Database updated with verification results.")
    print("=" * 100 + "\n")

    conn.close()


if __name__ == "__main__":
    try:
        validate_all_jobs()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
