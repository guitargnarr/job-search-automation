#!/usr/bin/env python3
"""
CSV to Database Import Script
Imports Louisville_Job_Tracker_EXPANDED.csv into the job search automation database
"""

import csv
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.database import AsyncSessionLocal
from backend.models.models import Company, Job
from backend.core.logging import get_logger

logger = get_logger(__name__)

# CSV file path
CSV_FILE = "tracking/exports/Louisville_Job_Tracker_EXPANDED.csv"


def parse_salary_range(salary_str: str) -> tuple[Optional[int], Optional[int]]:
    """
    Parse salary range from various formats:
    - "$75-95k" -> (75000, 95000)
    - "$120-155k" -> (120000, 155000)
    - "TBD" -> (None, None)
    - "$25/hr (~$36k/yr)" -> (36000, 36000)
    """
    if not salary_str or salary_str.upper() in ['TBD', 'N/A', '']:
        return None, None

    # Remove $ and spaces
    salary_str = salary_str.replace('$', '').replace(',', '').strip()

    # Handle hourly with annual estimate
    if '/hr' in salary_str and '~' in salary_str:
        # Extract the annual amount: "$25/hr (~$36k/yr)" -> "36k/yr"
        annual_part = salary_str.split('~')[1]
        annual_part = annual_part.replace('$', '').replace('/yr', '').strip()
        if 'k' in annual_part:
            amount = int(float(annual_part.replace('k', '')) * 1000)
            return amount, amount

    # Handle range: "75-95k" or "120-155k"
    if '-' in salary_str and 'k' in salary_str:
        parts = salary_str.replace('k', '').split('-')
        if len(parts) == 2:
            try:
                min_sal = int(float(parts[0].strip()) * 1000)
                max_sal = int(float(parts[1].strip()) * 1000)
                return min_sal, max_sal
            except ValueError:
                pass

    # Handle "Director" or descriptive ranges
    if 'Director' in salary_str or 'est' in salary_str:
        # Try to extract numbers
        import re
        numbers = re.findall(r'\d+', salary_str)
        if len(numbers) >= 2:
            try:
                min_sal = int(numbers[0]) * 1000
                max_sal = int(numbers[1]) * 1000
                return min_sal, max_sal
            except:
                pass

    return None, None


def map_priority(priority_str: str) -> str:
    """Map CSV priority to database priority"""
    if not priority_str:
        return "MEDIUM"

    priority_upper = priority_str.upper()
    if priority_upper in ["HIGH", "MEDIUM", "LOW", "SKIP"]:
        return priority_upper
    return "MEDIUM"


def map_status(app_status: str) -> str:
    """Map CSV application status to database status"""
    if not app_status:
        return "new"

    status_map = {
        "Not Applied": "new",
        "Applied": "applied",
        "CLOSED/FILLED": "closed",
        "N/A": "closed",
    }

    return status_map.get(app_status, "new")


def map_remote_type(job_type: str, employment_type: str) -> str:
    """Determine if job is remote, hybrid, or onsite"""
    combined = f"{job_type} {employment_type}".lower()

    if "remote" in combined:
        return "remote"
    elif "hybrid" in combined:
        return "hybrid"
    else:
        return "onsite"


def parse_skills_match(match_str: str) -> Optional[int]:
    """Parse '85%' -> 85"""
    if not match_str or match_str == 'N/A':
        return None

    try:
        return int(match_str.replace('%', '').strip())
    except:
        return None


async def create_or_get_company(session, company_name: str, industry: str = None) -> Company:
    """Create company if doesn't exist, return existing if it does"""
    from sqlalchemy import select

    # Check if company exists
    result = await session.execute(
        select(Company).where(Company.name == company_name)
    )
    company = result.scalar_one_or_none()

    if company:
        return company

    # Create new company
    company = Company(
        name=company_name,
        industry=industry or "Unknown",
        size_range="Unknown"
    )
    session.add(company)
    await session.flush()  # Get the ID
    logger.info(f"Created company: {company_name}")
    return company


async def import_csv_jobs():
    """Main import function"""

    print("=" * 70)
    print("CSV to Database Import")
    print("=" * 70)
    print()

    csv_path = Path(CSV_FILE)
    if not csv_path.exists():
        print(f"❌ ERROR: CSV file not found at {csv_path}")
        return False

    print(f"📁 Reading CSV: {csv_path}")
    print()

    # Read CSV
    jobs_data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs_data.append(row)

    print(f"✅ Found {len(jobs_data)} jobs in CSV")
    print()

    # Create database session
    async with AsyncSessionLocal() as session:
        try:
            imported = 0
            skipped = 0
            errors = 0

            for idx, row in enumerate(jobs_data, 1):
                try:
                    # Extract data
                    job_id = row.get('Job ID', '')
                    title = row.get('Job Title', 'Untitled')
                    company_name = row.get('Company', 'Unknown Company')
                    salary_range = row.get('Salary Range', '')
                    job_type = row.get('Job Type', '')
                    employment_type = row.get('Employment Type', 'Full-time')
                    industry = row.get('Industry', '')
                    post_date = row.get('Post Date', '')
                    app_status = row.get('Application Status', '')
                    app_date = row.get('Application Date', '')
                    job_url = row.get('Job URL', '')
                    priority = row.get('Priority', 'MEDIUM')
                    resume_version = row.get('Resume Version', '')
                    cover_letter = row.get('Cover Letter Tier', '')
                    skills_match = row.get('Skills Match %', '')
                    next_action = row.get('Next Action', '')
                    notes = row.get('Notes/Key Requirements', '')
                    source = row.get('Source', '')

                    # Parse salary
                    salary_min, salary_max = parse_salary_range(salary_range)

                    # Get or create company
                    company = await create_or_get_company(session, company_name, industry)

                    # Parse skills match
                    fit_score = parse_skills_match(skills_match)

                    # Create job record
                    job = Job(
                        company_id=company.id,
                        title=title,
                        job_url=job_url if job_url else None,
                        source=source if source else "CSV Import",
                        job_description=f"{notes}\\n\\nNext Action: {next_action}\\n\\nResume: {resume_version}\\nCover Letter: {cover_letter}",
                        posted_date=None,  # Would need to parse date format
                        salary_min=salary_min,
                        salary_max=salary_max,
                        remote_type=map_remote_type(job_type, employment_type),
                        location=job_type,  # CSV "Job Type" contains location info
                        fit_score=fit_score,
                        priority=map_priority(priority),
                        status=map_status(app_status),
                    )

                    session.add(job)
                    imported += 1

                    # Progress indicator
                    if idx % 10 == 0:
                        print(f"Progress: {idx}/{len(jobs_data)} jobs processed...")

                except Exception as e:
                    logger.error(f"Error importing job {idx} ({title}): {e}")
                    errors += 1
                    continue

            # Commit all changes
            await session.commit()

            print()
            print("=" * 70)
            print("Import Complete!")
            print("=" * 70)
            print(f"✅ Imported: {imported} jobs")
            print(f"⏭️  Skipped: {skipped} jobs")
            print(f"❌ Errors: {errors} jobs")
            print()
            print("Next steps:")
            print("1. Verify import: curl http://localhost:8899/api/v1/jobs/stats")
            print("2. View jobs: curl http://localhost:8899/api/v1/jobs/list | jq")
            print("3. Start applying! See STRATEGIC_ROADMAP.md")
            print()

            return True

        except Exception as e:
            logger.error(f"Fatal error during import: {e}")
            await session.rollback()
            print()
            print(f"❌ FATAL ERROR: {e}")
            print()
            return False


def main():
    """Entry point"""
    try:
        result = asyncio.run(import_csv_jobs())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\\n\\n⚠️  Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
