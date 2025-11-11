#!/usr/bin/env python3
"""
Job Search MCP Server
Exposes job discovery, tracking, and analytics capabilities to AI assistants
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

# Import existing services and models
from backend.core.database import get_session, engine, Base
from backend.models.models import (
    Job, Company, Application, EmailTracking,
    Priority, ApplicationStatus
)
from backend.services.ats_optimizer import ATSOptimizer
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Initialize MCP server
mcp = FastMCP("Job Search Automation")

# Initialize services
ats_optimizer = ATSOptimizer()


# ====================
# Resources (Data Access)
# ====================

@mcp.resource("jobs://list")
async def list_jobs() -> str:
    """Get all tracked jobs with their current status"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(Job).order_by(Job.created_at.desc())
            )
            jobs = result.scalars().all()

            jobs_data = []
            for job in jobs:
                jobs_data.append({
                    "id": job.id,
                    "company": job.company_name,
                    "title": job.title,
                    "location": job.location,
                    "remote_type": job.remote_type,
                    "salary_range": f"${job.salary_min:,}-${job.salary_max:,}" if job.salary_min else "Not specified",
                    "priority": job.priority.value if job.priority else "MEDIUM",
                    "applied": job.applied,
                    "status": job.status,
                    "url": job.job_url,
                    "created": job.created_at.isoformat() if job.created_at else None
                })

            return json.dumps({
                "total_jobs": len(jobs_data),
                "jobs": jobs_data
            }, indent=2)
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.resource("jobs://analytics")
async def get_analytics() -> str:
    """Get real-time job search analytics and metrics"""
    try:
        async with get_session() as session:
            # Get job statistics
            jobs_result = await session.execute(select(Job))
            jobs = jobs_result.scalars().all()

            # Get application statistics
            apps_result = await session.execute(select(Application))
            applications = apps_result.scalars().all()

            # Calculate metrics
            total_jobs = len(jobs)
            applied_jobs = sum(1 for j in jobs if j.applied)
            high_priority = sum(1 for j in jobs if j.priority == Priority.HIGH)

            # Application status breakdown
            status_counts = {}
            for app in applications:
                status = app.status.value if app.status else "UNKNOWN"
                status_counts[status] = status_counts.get(status, 0) + 1

            # Response rate calculation
            responded = sum(1 for app in applications if app.status in [
                ApplicationStatus.RESPONDED,
                ApplicationStatus.INTERVIEWING,
                ApplicationStatus.OFFERED
            ])
            response_rate = (responded / len(applications) * 100) if applications else 0

            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_apps = sum(1 for app in applications if app.created_at and app.created_at > week_ago)

            return json.dumps({
                "overview": {
                    "total_jobs_tracked": total_jobs,
                    "jobs_applied": applied_jobs,
                    "high_priority_jobs": high_priority,
                    "total_applications": len(applications),
                    "response_rate": f"{response_rate:.1f}%"
                },
                "application_pipeline": status_counts,
                "recent_activity": {
                    "applications_this_week": recent_apps,
                    "pending_follow_ups": 0  # TODO: Implement follow-up tracking
                }
            }, indent=2)
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.resource("companies://research")
async def get_company_research(company_name: str) -> str:
    """Get research data for a specific company"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(Company).where(Company.name.ilike(f"%{company_name}%"))
            )
            company = result.scalar_one_or_none()

            if not company:
                return json.dumps({"error": f"Company '{company_name}' not found"})

            return json.dumps({
                "name": company.name,
                "website": company.website,
                "industry": company.industry,
                "size": company.size_range,
                "glassdoor_rating": company.glassdoor_rating,
                "tech_stack": company.tech_stack or [],
                "culture_notes": company.culture_notes,
                "recent_news": company.recent_news or [],
                "interview_process": company.interview_process or {}
            }, indent=2)
    except Exception as e:
        logger.error(f"Error researching company: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.resource("applications://status")
async def get_application_status() -> str:
    """Get current status of all job applications"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(Application).order_by(Application.created_at.desc())
            )
            applications = result.scalars().all()

            apps_data = []
            for app in applications:
                # Get associated job details
                job_result = await session.execute(
                    select(Job).where(Job.id == app.job_id)
                )
                job = job_result.scalar_one_or_none()

                apps_data.append({
                    "id": app.id,
                    "job_title": job.title if job else "Unknown",
                    "company": job.company_name if job else "Unknown",
                    "status": app.status.value if app.status else "UNKNOWN",
                    "applied_date": app.applied_date.isoformat() if app.applied_date else None,
                    "last_contact": app.last_contact_date.isoformat() if app.last_contact_date else None,
                    "interview_dates": app.interview_dates or [],
                    "notes": app.notes
                })

            return json.dumps({
                "total_applications": len(apps_data),
                "applications": apps_data
            }, indent=2)
    except Exception as e:
        logger.error(f"Error getting application status: {str(e)}")
        return json.dumps({"error": str(e)})


# ====================
# Tools (Actions)
# ====================

@mcp.tool()
async def search_jobs(
    keywords: str,
    location: str = "Remote",
    exclude_companies: Optional[List[str]] = None,
    remote_only: bool = False
) -> Dict[str, Any]:
    """
    Search for jobs matching criteria using web search

    Args:
        keywords: Job title or keywords to search for
        location: Job location (e.g., "Louisville, KY" or "Remote")
        exclude_companies: List of companies to exclude (e.g., ["Humana"])
        remote_only: Whether to only search for remote positions

    Returns:
        Dictionary with search results and statistics
    """
    try:
        # Build search query
        query_parts = [keywords]

        if remote_only or location.lower() == "remote":
            query_parts.extend(["remote", "work from home", "WFH"])
        else:
            query_parts.append(location)

        # Add exclusions
        if exclude_companies:
            for company in exclude_companies:
                query_parts.append(f"-{company}")

        search_query = " ".join(query_parts)

        # Log the search
        logger.info(f"Searching for jobs: {search_query}")

        # In a real implementation, this would call a web search API
        # For now, return a structured response
        return {
            "success": True,
            "query": search_query,
            "message": f"Search initiated for: {keywords} in {location}",
            "instructions": "Use WebSearch tool to execute the actual search, then use add_job to save results"
        }

    except Exception as e:
        logger.error(f"Error searching jobs: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def add_job(
    company_name: str,
    title: str,
    job_url: str,
    location: str = "Remote",
    job_description: Optional[str] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    remote_type: str = "remote",
    priority: str = "MEDIUM",
    auto_analyze: bool = True
) -> Dict[str, Any]:
    """
    Add a new job to the tracking system

    Args:
        company_name: Name of the company
        title: Job title
        job_url: URL to the job posting
        location: Job location
        job_description: Full job description text
        salary_min: Minimum salary (annual)
        salary_max: Maximum salary (annual)
        remote_type: Type of remote work (remote, hybrid, onsite)
        priority: Priority level (HIGH, MEDIUM, LOW)
        auto_analyze: Whether to automatically analyze with ATS optimizer

    Returns:
        Dictionary with job ID and analysis results
    """
    try:
        async with get_session() as session:
            # Check if company exists, create if not
            company_result = await session.execute(
                select(Company).where(Company.name == company_name)
            )
            company = company_result.scalar_one_or_none()

            if not company:
                company = Company(
                    name=company_name,
                    created_at=datetime.utcnow()
                )
                session.add(company)
                await session.flush()

            # Create the job
            job = Job(
                company_id=company.id,
                company_name=company_name,
                title=title,
                job_description=job_description or f"{title} at {company_name}",
                job_url=job_url,
                location=location,
                remote_type=remote_type,
                salary_min=salary_min,
                salary_max=salary_max,
                priority=Priority[priority.upper()],
                status="new",
                applied=False,
                created_at=datetime.utcnow()
            )
            session.add(job)
            await session.commit()

            result = {
                "success": True,
                "job_id": job.id,
                "message": f"Added: {title} at {company_name}"
            }

            # Run ATS analysis if requested
            if auto_analyze and job_description:
                ats_score = ats_optimizer.calculate_ats_score(
                    "", # Would need actual resume here
                    job_description
                )
                keywords = ats_optimizer.extract_keywords(job_description)

                result["ats_analysis"] = {
                    "score": ats_score,
                    "top_keywords": keywords[:10]
                }

            return result

    except Exception as e:
        logger.error(f"Error adding job: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def optimize_resume_for_job(
    job_id: int,
    base_resume_path: str
) -> Dict[str, Any]:
    """
    Generate an ATS-optimized resume for a specific job

    Args:
        job_id: ID of the job to optimize for
        base_resume_path: Path to the base resume file

    Returns:
        Dictionary with optimization results and new resume path
    """
    try:
        async with get_session() as session:
            # Get job details
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                return {"success": False, "error": f"Job {job_id} not found"}

            if not job.job_description:
                return {"success": False, "error": "Job has no description to optimize against"}

            # Optimize resume
            optimization = ats_optimizer.optimize_resume(
                base_resume_path,
                job.job_description,
                job.title
            )

            # Save optimized version
            output_dir = Path("documents/resumes/tailored")
            output_dir.mkdir(parents=True, exist_ok=True)

            company_safe = job.company_name.replace(" ", "_").replace("/", "_")
            output_path = output_dir / f"resume_{company_safe}_{job.id}.docx"

            # In real implementation, would save the optimized document

            return {
                "success": True,
                "job_id": job_id,
                "company": job.company_name,
                "title": job.title,
                "ats_score": optimization["ats_score"],
                "keywords_matched": optimization["keywords_matched"],
                "missing_keywords": optimization["missing_keywords"][:10],
                "optimized_resume_path": str(output_path)
            }

    except Exception as e:
        logger.error(f"Error optimizing resume: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def update_job_status(
    job_id: int,
    applied: Optional[bool] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update the status of a tracked job

    Args:
        job_id: ID of the job to update
        applied: Whether you've applied to this job
        status: New status (new, reviewing, applied, rejected, etc.)
        priority: New priority (HIGH, MEDIUM, LOW, SKIP)
        notes: Additional notes about the job

    Returns:
        Dictionary with update confirmation
    """
    try:
        async with get_session() as session:
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                return {"success": False, "error": f"Job {job_id} not found"}

            # Update fields
            if applied is not None:
                job.applied = applied
            if status is not None:
                job.status = status
            if priority is not None:
                job.priority = Priority[priority.upper()]
            if notes is not None:
                existing_notes = job.notes or ""
                job.notes = f"{existing_notes}\n{datetime.utcnow().isoformat()}: {notes}".strip()

            job.updated_at = datetime.utcnow()
            await session.commit()

            return {
                "success": True,
                "job_id": job_id,
                "message": f"Updated job: {job.title} at {job.company_name}",
                "current_status": {
                    "applied": job.applied,
                    "status": job.status,
                    "priority": job.priority.value if job.priority else None
                }
            }

    except Exception as e:
        logger.error(f"Error updating job: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def create_application(
    job_id: int,
    cover_letter_path: Optional[str] = None,
    resume_version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a job application record

    Args:
        job_id: ID of the job being applied to
        cover_letter_path: Path to the cover letter used
        resume_version: Path or identifier of resume version used

    Returns:
        Dictionary with application details
    """
    try:
        async with get_session() as session:
            # Get job details
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                return {"success": False, "error": f"Job {job_id} not found"}

            # Check if application already exists
            app_result = await session.execute(
                select(Application).where(Application.job_id == job_id)
            )
            existing_app = app_result.scalar_one_or_none()

            if existing_app:
                return {
                    "success": False,
                    "error": f"Application already exists for job {job_id}",
                    "application_id": existing_app.id
                }

            # Create application
            application = Application(
                job_id=job_id,
                company_id=job.company_id,
                status=ApplicationStatus.APPLIED,
                applied_date=datetime.utcnow(),
                resume_version=resume_version,
                cover_letter_version=cover_letter_path,
                created_at=datetime.utcnow()
            )
            session.add(application)

            # Update job status
            job.applied = True
            job.status = "applied"

            await session.commit()

            return {
                "success": True,
                "application_id": application.id,
                "job_id": job_id,
                "company": job.company_name,
                "title": job.title,
                "message": f"Application created for {job.title} at {job.company_name}"
            }

    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        return {"success": False, "error": str(e)}


# ====================
# Prompts (Templates)
# ====================

@mcp.prompt("daily_job_search")
async def daily_job_search_prompt() -> str:
    """Daily job search workflow template"""
    return """Execute my daily job search routine:

1. Search for new positions:
   - Keywords: Business Analyst, Data Analyst, Healthcare Analyst
   - Locations: Louisville, KY (any type) OR Remote only
   - Exclude: Humana

2. For each promising job found:
   - Add to tracking system with appropriate priority
   - Extract key requirements and skills

3. For HIGH priority jobs:
   - Generate optimized resume
   - Create tailored cover letter
   - Prepare application materials

4. Review application pipeline:
   - Check for any responses in email
   - Update statuses accordingly
   - Schedule follow-ups as needed

5. Provide summary report:
   - New opportunities found
   - Applications ready to submit
   - Pending responses
   - Next actions required"""


@mcp.prompt("interview_prep")
async def interview_prep_prompt() -> str:
    """Interview preparation template"""
    return """Help me prepare for an interview:

1. Research the company:
   - Recent news and developments
   - Company culture and values
   - Common interview questions
   - Typical interview process

2. Analyze the job description:
   - Key requirements and skills
   - Potential technical questions
   - Behavioral scenarios to prepare

3. Prepare STAR stories:
   - Match experiences to job requirements
   - Quantify achievements
   - Prepare 5-7 strong examples

4. Generate questions to ask:
   - About the role and team
   - Company direction and growth
   - Success metrics for the position

5. Create interview checklist:
   - Documents to bring
   - Research notes summary
   - Key talking points
   - Post-interview follow-up plan"""


async def main():
    """Run the MCP server"""
    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Job Search MCP Server starting...")
    await mcp.run()


if __name__ == "__main__":
    asyncio.run(main())