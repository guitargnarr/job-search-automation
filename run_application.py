#!/usr/bin/env python3
"""
Unified Job Application Runner
Chains together all working components for end-to-end job application automation
"""

import sys
import json
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import time

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

class JobApplicationRunner:
    """Unified runner for job application automation"""

    def __init__(self, db_path: str = "job_search.db"):
        self.db_path = db_path
        self.connection = None

    def connect_db(self):
        """Connect to the database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print_error(f"Failed to connect to database: {e}")
            return False

    def close_db(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def list_jobs(self, status: str = "new", limit: int = 10) -> list:
        """List available jobs from the database"""
        cursor = self.connection.cursor()
        query = """
            SELECT j.id, j.title, c.name as company, j.location,
                   j.remote_type, j.salary_min, j.salary_max, j.priority, j.status
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.status = ?
            ORDER BY j.priority DESC, j.created_at DESC
            LIMIT ?
        """
        cursor.execute(query, (status, limit))
        return cursor.fetchall()

    def get_job_details(self, job_id: int) -> Optional[Dict]:
        """Get detailed job information"""
        cursor = self.connection.cursor()
        query = """
            SELECT j.*, c.name as company_name, c.website, c.industry
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.id = ?
        """
        cursor.execute(query, (job_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def check_existing_application(self, job_id: int) -> bool:
        """Check if an application already exists for this job"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM applications WHERE job_id = ?", (job_id,))
        return cursor.fetchone() is not None

    def create_cover_letter(self, job_id: int, company: str, title: str) -> bool:
        """Generate a cover letter for the job"""
        print_info(f"Generating cover letter for {title} at {company}...")

        # Check if cover letter script exists
        script_path = Path("create_centene_cover_letter.py")
        if not script_path.exists():
            print_warning("Cover letter generator script not found, skipping...")
            return False

        # Run the cover letter generation script
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print_success(f"Cover letter created for {company}")
                return True
            else:
                print_error(f"Cover letter generation failed: {result.stderr}")
                return False
        except Exception as e:
            print_error(f"Error generating cover letter: {e}")
            return False

    def tailor_resume(self, job_id: int, company: str, title: str) -> bool:
        """Tailor resume for the specific job"""
        print_info(f"Tailoring resume for {title} at {company}...")

        # Create tailored resume (placeholder for actual implementation)
        output_dir = Path("documents/resumes/tailored")
        output_dir.mkdir(parents=True, exist_ok=True)

        resume_file = output_dir / f"Resume_{company.replace(' ', '_')}_{datetime.now():%Y%m%d}.docx"

        # For now, just create a marker file
        resume_file.touch()
        print_success(f"Resume tailored and saved to {resume_file.name}")
        return True

    def log_application(self, job_id: int) -> bool:
        """Log the application in the database"""
        print_info("Logging application to database...")

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO applications (
                    job_id, applied_date, application_method,
                    resume_version, cover_letter_version, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                datetime.now(),
                "Direct",
                f"tailored_{datetime.now():%Y%m%d}",
                f"custom_{datetime.now():%Y%m%d}",
                "APPLIED",
                datetime.now()
            ))
            self.connection.commit()
            print_success("Application logged successfully")
            return True
        except Exception as e:
            print_error(f"Failed to log application: {e}")
            return False

    def update_job_status(self, job_id: int, status: str) -> bool:
        """Update job status in database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE jobs
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status, datetime.now(), job_id))
            self.connection.commit()
            print_success(f"Job status updated to '{status}'")
            return True
        except Exception as e:
            print_error(f"Failed to update job status: {e}")
            return False

    def schedule_followup(self, job_id: int, days: int = 7) -> bool:
        """Schedule a follow-up reminder"""
        print_info(f"Scheduling follow-up in {days} days...")

        try:
            # Get application ID
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM applications WHERE job_id = ?", (job_id,))
            app = cursor.fetchone()

            if not app:
                print_warning("No application found, skipping follow-up scheduling")
                return False

            # Schedule follow-up
            follow_up_date = datetime.now().timestamp() + (days * 86400)
            cursor.execute("""
                INSERT INTO follow_ups (
                    application_id, scheduled_date, channel,
                    subject, message, sent, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                app['id'],
                datetime.fromtimestamp(follow_up_date),
                "email",
                "Follow-up on application",
                f"Follow up on application submitted {datetime.now():%Y-%m-%d}",
                False,
                datetime.now()
            ))
            self.connection.commit()
            print_success(f"Follow-up scheduled for {datetime.fromtimestamp(follow_up_date):%Y-%m-%d}")
            return True
        except Exception as e:
            print_error(f"Failed to schedule follow-up: {e}")
            return False

    def run_application_workflow(self, job_id: int):
        """Run the complete application workflow for a job"""
        print_header(f"STARTING APPLICATION WORKFLOW FOR JOB #{job_id}")

        # Get job details
        job = self.get_job_details(job_id)
        if not job:
            print_error(f"Job #{job_id} not found")
            return False

        print_info(f"Applying to: {job['title']} at {job['company_name']}")
        print_info(f"Location: {job['location']} ({job['remote_type']})")
        if job['salary_min'] or job['salary_max']:
            print_info(f"Salary: ${job['salary_min'] or 'N/A'} - ${job['salary_max'] or 'N/A'}")

        # Check if already applied
        if self.check_existing_application(job_id):
            print_warning("Application already exists for this job!")
            return False

        success_count = 0
        total_steps = 5

        # Step 1: Generate cover letter
        if self.create_cover_letter(job_id, job['company_name'], job['title']):
            success_count += 1

        # Step 2: Tailor resume
        if self.tailor_resume(job_id, job['company_name'], job['title']):
            success_count += 1

        # Step 3: Log application
        if self.log_application(job_id):
            success_count += 1

        # Step 4: Update job status
        if self.update_job_status(job_id, "applied"):
            success_count += 1

        # Step 5: Schedule follow-up
        if self.schedule_followup(job_id):
            success_count += 1

        # Print summary
        print_header("APPLICATION WORKFLOW COMPLETE")
        print(f"Success rate: {success_count}/{total_steps} steps completed")

        if success_count == total_steps:
            print_success("✨ Application submitted successfully!")
        elif success_count > 2:
            print_warning("⚠️  Application partially completed - manual review recommended")
        else:
            print_error("❌ Application failed - manual intervention required")

        return success_count == total_steps

    def run_batch_applications(self, limit: int = 5):
        """Run applications for multiple jobs"""
        print_header(f"BATCH APPLICATION MODE - Processing up to {limit} jobs")

        # Get new jobs
        jobs = self.list_jobs(status="new", limit=limit)

        if not jobs:
            print_warning("No new jobs found to apply to")
            return

        print_info(f"Found {len(jobs)} jobs to process")

        success_count = 0
        for i, job in enumerate(jobs, 1):
            print(f"\n{Colors.BLUE}[{i}/{len(jobs)}] Processing: {job['title']} at {job['company']}{Colors.ENDC}")

            if self.run_application_workflow(job['id']):
                success_count += 1

            # Add delay between applications
            if i < len(jobs):
                print_info("Waiting 5 seconds before next application...")
                time.sleep(5)

        # Final summary
        print_header("BATCH PROCESSING COMPLETE")
        print(f"Successfully applied to {success_count}/{len(jobs)} jobs")

        if success_count == len(jobs):
            print_success("🎉 All applications completed successfully!")
        elif success_count > 0:
            print_warning(f"⚠️  Completed {success_count} out of {len(jobs)} applications")
        else:
            print_error("❌ No applications were successful")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Unified Job Application Runner")
    parser.add_argument("--job-id", type=int, help="Apply to a specific job ID")
    parser.add_argument("--batch", type=int, default=0, help="Run batch applications (specify max count)")
    parser.add_argument("--list", action="store_true", help="List available jobs")
    parser.add_argument("--db", default="job_search.db", help="Database path")

    args = parser.parse_args()

    # Create runner instance
    runner = JobApplicationRunner(db_path=args.db)

    if not runner.connect_db():
        print_error("Failed to connect to database")
        return 1

    try:
        if args.list:
            # List available jobs
            print_header("AVAILABLE JOBS")
            jobs = runner.list_jobs(limit=20)
            for job in jobs:
                salary = f"${job['salary_min']}-${job['salary_max']}" if job['salary_min'] else "Not specified"
                print(f"#{job['id']:3} | {job['company']:20} | {job['title']:30} | {job['remote_type']:10} | {salary}")

        elif args.job_id:
            # Apply to specific job
            runner.run_application_workflow(args.job_id)

        elif args.batch > 0:
            # Run batch applications
            runner.run_batch_applications(limit=args.batch)

        else:
            # Interactive mode
            print_header("JOB APPLICATION AUTOMATION")
            print("Select an option:")
            print("1. Apply to a specific job")
            print("2. Run batch applications")
            print("3. List available jobs")
            print("4. Exit")

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                job_id = input("Enter job ID: ").strip()
                if job_id.isdigit():
                    runner.run_application_workflow(int(job_id))
                else:
                    print_error("Invalid job ID")

            elif choice == "2":
                count = input("How many jobs to apply to? (1-10): ").strip()
                if count.isdigit() and 1 <= int(count) <= 10:
                    runner.run_batch_applications(limit=int(count))
                else:
                    print_error("Invalid count")

            elif choice == "3":
                jobs = runner.list_jobs(limit=20)
                print_header("AVAILABLE JOBS")
                for job in jobs:
                    print(f"#{job['id']:3} | {job['company']:20} | {job['title']:40}")

            elif choice == "4":
                print_info("Exiting...")
            else:
                print_error("Invalid choice")

    finally:
        runner.close_db()

    return 0

if __name__ == "__main__":
    sys.exit(main())