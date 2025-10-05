#!/usr/bin/env python3
"""
Initialize the Job Search Automation database
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.database import engine, Base
from backend.models.models import Company, Job, Application
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from backend.models.models import Priority, ApplicationStatus

async def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Database tables created")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

async def add_sample_data():
    """Add sample data for testing"""
    async with AsyncSession(engine) as session:
        # Check if data already exists
        from sqlalchemy import select
        result = await session.execute(select(Company))
        if result.first():
            print("ℹ Sample data already exists")
            return

        print("Adding sample data...")

        # Add sample companies
        companies = [
            Company(
                name="Google",
                industry="Technology",
                size_range="10000+",
                website="https://google.com",
                linkedin_url="https://linkedin.com/company/google",
                glassdoor_rating=4.5
            ),
            Company(
                name="Meta",
                industry="Technology",
                size_range="10000+",
                website="https://meta.com",
                linkedin_url="https://linkedin.com/company/meta",
                glassdoor_rating=4.2
            ),
            Company(
                name="Startup Inc",
                industry="Technology",
                size_range="50-100",
                website="https://startupinc.example.com",
                glassdoor_rating=4.0
            )
        ]

        for company in companies:
            session.add(company)

        await session.flush()

        # Add sample jobs
        jobs = [
            Job(
                company_id=companies[0].id,
                title="Senior Software Engineer",
                job_description="We're looking for a senior software engineer with expertise in Python, FastAPI, and cloud technologies. Experience with automation and AI/ML is a plus.",
                location="Mountain View, CA",
                remote_type="hybrid",
                salary_min=150000,
                salary_max=250000,
                priority=Priority.HIGH,
                job_url="https://careers.google.com/example",
                source="company_site",
                posted_date=(datetime.now() - timedelta(days=3)).date(),
                status="new",
                requirements=["Python", "FastAPI", "Cloud", "AI/ML"],
                ats_score=85,
                fit_score=90,
                keywords=["python", "fastapi", "cloud", "automation", "ai", "ml"]
            ),
            Job(
                company_id=companies[1].id,
                title="Full Stack Developer",
                job_description="Join our team to build next-generation social platforms. Required: React, Node.js, Python. Nice to have: GraphQL, Kubernetes.",
                location="Menlo Park, CA",
                remote_type="remote",
                salary_min=130000,
                salary_max=220000,
                priority=Priority.HIGH,
                job_url="https://careers.meta.com/example",
                source="company_site",
                posted_date=(datetime.now() - timedelta(days=5)).date(),
                status="new",
                requirements=["React", "Node.js", "Python", "GraphQL", "Kubernetes"],
                ats_score=80,
                fit_score=85,
                keywords=["react", "nodejs", "python", "fullstack", "graphql", "kubernetes"]
            ),
            Job(
                company_id=companies[2].id,
                title="Backend Engineer",
                job_description="Fast-growing startup seeks backend engineer. Python, FastAPI, PostgreSQL required. Stock options included.",
                location="San Francisco, CA",
                remote_type="onsite",
                salary_min=120000,
                salary_max=180000,
                priority=Priority.MEDIUM,
                job_url="https://startupinc.example.com/careers",
                source="company_site",
                posted_date=(datetime.now() - timedelta(days=1)).date(),
                status="new",
                requirements=["Python", "FastAPI", "PostgreSQL"],
                ats_score=75,
                fit_score=70,
                keywords=["python", "fastapi", "postgresql", "backend", "startup"]
            )
        ]

        for job in jobs:
            session.add(job)

        await session.flush()

        # Add sample applications
        applications = [
            Application(
                job_id=jobs[0].id,
                applied_date=datetime.now() - timedelta(days=2),
                status=ApplicationStatus.APPLIED,
                resume_version="resume_v3_google.pdf",
                cover_letter_version="cover_google.pdf"
            ),
            Application(
                job_id=jobs[1].id,
                applied_date=datetime.now() - timedelta(days=4),
                status=ApplicationStatus.INTERVIEWING,
                resume_version="resume_v3_meta.pdf",
                cover_letter_version="cover_meta.pdf",
                response_received=True,
                response_date=datetime.now() - timedelta(days=2),
                interview_scheduled=datetime.now() + timedelta(days=3)
            )
        ]

        for app in applications:
            session.add(app)

        await session.commit()
        print("✓ Sample data added successfully")
        print("  - 3 companies")
        print("  - 3 jobs")
        print("  - 2 applications")

async def main():
    """Initialize database and add sample data"""
    print("Starting database initialization...")
    try:
        await init_db()
        await add_sample_data()
        print("\n✅ Database initialization complete!")
        print("\nYou can now run: ./run.sh")
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("Running main...")
    asyncio.run(main())