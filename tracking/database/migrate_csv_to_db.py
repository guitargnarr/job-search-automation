#!/usr/bin/env python3
"""
CSV to SQLite Migration Script
Converts existing job tracking CSV files to SQLite database
"""

import sqlite3
import csv
import os
import re
from datetime import datetime
from pathlib import Path

class JobTrackerMigration:
    def __init__(self, db_path='job_tracker.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_schema(self):
        """Create database schema from SQL file"""
        schema_path = Path(__file__).parent / 'schema.sql'

        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                self.cursor.executescript(schema_sql)
                self.conn.commit()
                print("✅ Database schema created successfully")
        else:
            print("❌ Schema file not found")
            return False
        return True

    def parse_salary_range(self, salary_str):
        """Parse salary range string into min/max values"""
        if not salary_str or salary_str == 'TBD':
            return None, None, salary_str

        # Remove commas and dollar signs
        salary_str = salary_str.replace(',', '').replace('$', '')

        # Look for range pattern (e.g., "120-155k" or "120,000-155,000")
        range_match = re.search(r'(\d+)[\s-]+(\d+)', salary_str)
        if range_match:
            min_val = int(range_match.group(1))
            max_val = int(range_match.group(2))

            # Handle 'k' notation
            if 'k' in salary_str.lower():
                min_val *= 1000
                max_val *= 1000

            return min_val, max_val, salary_str

        # Single value
        single_match = re.search(r'(\d+)', salary_str)
        if single_match:
            value = int(single_match.group(1))
            if 'k' in salary_str.lower():
                value *= 1000

            # For hourly rates, estimate annual
            if '/hr' in salary_str or 'per hour' in salary_str.lower():
                # Assume 2000 hours/year for full-time
                value = value * 2000

            return value, value, salary_str

        return None, None, salary_str

    def import_csv(self, csv_path):
        """Import data from CSV file to database"""
        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found: {csv_path}")
            return False

        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            companies = {}  # Cache company IDs
            row_count = 0

            for row in reader:
                row_count += 1

                # Insert or get company
                company_name = row.get('Company', 'Unknown')
                if company_name not in companies:
                    self.cursor.execute('''
                        INSERT OR IGNORE INTO companies (name, industry, location)
                        VALUES (?, ?, ?)
                    ''', (company_name, row.get('Industry', ''), row.get('Location', '')))

                    self.cursor.execute('SELECT id FROM companies WHERE name = ?', (company_name,))
                    companies[company_name] = self.cursor.fetchone()[0]

                company_id = companies[company_name]

                # Parse salary
                salary_min, salary_max, salary_range = self.parse_salary_range(row.get('Salary Range', ''))

                # Parse skills match percentage
                skills_match_str = row.get('Skills Match %', '0%')
                # Extract numeric value from string
                skills_match = 0
                if skills_match_str and skills_match_str != 'N/A':
                    # Try to extract number from string
                    import re
                    match = re.search(r'(\d+)', skills_match_str)
                    if match:
                        skills_match = int(match.group(1))
                    else:
                        skills_match = 0

                # Map priority values
                priority_value = row.get('Priority', 'MEDIUM').upper()
                # Handle any non-standard values
                if priority_value not in ['HIGH', 'MEDIUM', 'LOW', 'SKIP']:
                    if priority_value in ['N/A', '', 'NONE']:
                        priority_value = 'SKIP'
                    else:
                        priority_value = 'MEDIUM'

                # Insert job
                self.cursor.execute('''
                    INSERT INTO jobs (
                        job_id, title, company_id, salary_min, salary_max, salary_range,
                        job_type, employment_type, location, post_date, job_url,
                        priority, skills_match_percent, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Job ID', f"CSV_{row_count}"),
                    row.get('Job Title', 'Unknown Title'),
                    company_id,
                    salary_min,
                    salary_max,
                    salary_range,
                    row.get('Job Type', ''),
                    row.get('Employment Type', ''),
                    row.get('Location', ''),
                    row.get('Post Date') if row.get('Post Date') != 'Active' else None,
                    row.get('Job URL', ''),
                    priority_value,
                    skills_match,
                    row.get('Source', 'CSV Import')
                ))

                job_id = self.cursor.lastrowid

                # Insert application record
                status_map = {
                    'Not Applied': 'Not Applied',
                    'CLOSED/FILLED': 'Closed',
                    'Applied': 'Applied',
                    'N/A': 'Not Applied'
                }

                status = status_map.get(row.get('Application Status', ''), 'Not Applied')

                self.cursor.execute('''
                    INSERT INTO applications (
                        job_id, status, application_date, resume_version,
                        cover_letter_tier, next_action, follow_up_date,
                        application_notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job_id,
                    status,
                    row.get('Application Date') if row.get('Application Date') not in ['', 'N/A'] else None,
                    row.get('Resume Version', ''),
                    row.get('Cover Letter Tier', ''),
                    row.get('Next Action', ''),
                    row.get('Follow-up Date', None),
                    row.get('Notes/Key Requirements', '')
                ))

                # Create reminder if follow-up date exists
                if row.get('Follow-up Date'):
                    app_id = self.cursor.lastrowid
                    self.cursor.execute('''
                        INSERT INTO reminders (
                            application_id, reminder_type, reminder_date
                        ) VALUES (?, ?, ?)
                    ''', (app_id, 'Follow Up', row.get('Follow-up Date')))

            self.conn.commit()
            print(f"✅ Imported {row_count} records from CSV")
            return True

    def create_sample_metrics(self):
        """Create initial metrics entries"""
        self.cursor.execute('''
            INSERT INTO metrics (date, metric_name, metric_value, category)
            SELECT
                DATE('now'),
                'Total Applications',
                COUNT(*),
                'Applications'
            FROM applications
            WHERE status = 'Applied'
        ''')

        self.cursor.execute('''
            INSERT INTO metrics (date, metric_name, metric_value, category)
            SELECT
                DATE('now'),
                'Response Rate',
                ROUND(COUNT(CASE WHEN status != 'Not Applied' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2),
                'Performance'
            FROM applications
        ''')

        self.conn.commit()
        print("✅ Created initial metrics")

    def print_summary(self):
        """Print database summary"""
        tables = ['companies', 'jobs', 'applications', 'contacts', 'reminders']

        print("\n📊 Database Summary:")
        print("-" * 40)

        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"  {table.capitalize()}: {count} records")

        # Show application status breakdown
        print("\n📈 Application Status Breakdown:")
        print("-" * 40)
        self.cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM applications
            GROUP BY status
            ORDER BY count DESC
        ''')

        for row in self.cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")

        # Show priority breakdown
        print("\n🎯 Priority Breakdown:")
        print("-" * 40)
        self.cursor.execute('''
            SELECT priority, COUNT(*) as count
            FROM jobs
            WHERE priority IS NOT NULL
            GROUP BY priority
            ORDER BY count DESC
        ''')

        for row in self.cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main migration function"""
    print("🚀 Starting CSV to Database Migration")
    print("=" * 40)

    # Initialize migration
    migrator = JobTrackerMigration('job_tracker.db')

    # Create schema
    if not migrator.create_schema():
        return

    # Find and import CSV files
    csv_dir = Path(__file__).parent.parent / 'exports'
    csv_files = list(csv_dir.glob('Louisville_Job_Tracker*.csv'))

    if csv_files:
        # Use the most recent expanded version
        csv_file = None
        for f in csv_files:
            if 'EXPANDED' in f.name:
                csv_file = f
                break

        if not csv_file and csv_files:
            csv_file = csv_files[0]

        print(f"\n📁 Importing from: {csv_file.name}")
        migrator.import_csv(csv_file)
    else:
        print("⚠️  No CSV files found in tracking/exports/")

    # Create initial metrics
    migrator.create_sample_metrics()

    # Print summary
    migrator.print_summary()

    # Close connection
    migrator.close()

    print("\n✨ Migration complete! Database created at: tracking/database/job_tracker.db")


if __name__ == "__main__":
    main()