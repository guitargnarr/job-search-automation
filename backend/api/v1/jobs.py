"""
Jobs API endpoints for managing job postings
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, HttpUrl

from backend.core.database import get_db
from backend.models.models import Job, Company, Application, Priority, ApplicationStatus
from backend.core.logging import get_logger
from backend.core.config import settings
from backend.services.ats_optimizer import ATSOptimizer

logger = get_logger(__name__)
router = APIRouter()
ats_optimizer = ATSOptimizer()

class JobCreate(BaseModel):
    company_name: str
    title: str
    job_description: str  # Fixed: matches model field name
    job_url: HttpUrl      # Fixed: matches model field name
    location: Optional[str] = None
    remote_type: Optional[str] = "remote"  # Fixed: matches model field name
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    priority: Priority = Priority.MEDIUM
    auto_analyze: bool = True

class JobUpdate(BaseModel):
    title: Optional[str] = None
    job_description: Optional[str] = None  # Fixed: matches model
    location: Optional[str] = None
    remote_type: Optional[str] = None      # Fixed: matches model
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    priority: Optional[Priority] = None
    status: Optional[str] = None           # Fixed: model uses 'status' not 'active'

@router.post("/create")
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting with optional ATS analysis"""
    try:
        # Check or create company
        company_result = await db.execute(
            select(Company).where(Company.name == job_data.company_name)
        )
        company = company_result.scalar_one_or_none()

        if not company:
            company = Company(
                name=job_data.company_name,
                created_at=datetime.now()
            )
            db.add(company)
            await db.flush()

        # Create job
        new_job = Job(
            company_id=company.id,
            title=job_data.title,
            job_description=job_data.job_description,  # Fixed
            job_url=str(job_data.job_url),             # Fixed
            location=job_data.location,
            remote_type=job_data.remote_type,          # Fixed
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            priority=job_data.priority,
            posted_date=datetime.now().date(),
            status="new"                                # Fixed: use status
        )

        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)

        # Auto-analyze job description if requested
        analysis = None
        if job_data.auto_analyze:
            try:
                analysis = ats_optimizer.analyze_job_description(job_data.job_description)  # Fixed
                # Store keywords in job record
                if analysis.get('keywords'):
                    new_job.keywords = analysis['keywords'][:10]  # Store as list
                    await db.commit()
            except Exception as e:
                logger.warning(f"ATS analysis failed: {e}")

        return {
            "status": "success",
            "job_id": new_job.id,
            "company": company.name,
            "message": "Job created successfully",
            "ats_analysis": analysis
        }

    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_jobs(
    active_only: bool = True,
    priority: Optional[Priority] = None,
    company_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, le=100, description="Max 100 items per page"),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List jobs with filtering and search (max 100 per page)"""
    try:
        # Enforce maximum page size
        limit = min(limit, settings.MAX_API_PAGE_SIZE)
        query = select(Job, Company, func.count(Application.id)).join(
            Company, Job.company_id == Company.id
        ).outerjoin(
            Application, Job.id == Application.job_id
        ).group_by(Job.id, Company.id)

        # Apply filters
        if active_only:
            query = query.where(Job.status.in_(["new", "researching", "ready"]))

        if priority:
            query = query.where(Job.priority == priority)

        if company_id:
            query = query.where(Job.company_id == company_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Job.title.ilike(search_pattern),
                    Job.job_description.ilike(search_pattern),
                    Company.name.ilike(search_pattern)
                )
            )

        # Order by posted date
        query = query.order_by(Job.posted_date.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        jobs = result.all()

        # Get total count
        count_query = select(func.count(Job.id))
        if active_only:
            count_query = count_query.where(Job.status.in_(["new", "researching", "ready"]))
        total_result = await db.execute(count_query)
        total_count = total_result.scalar()

        return {
            "total": total_count,
            "count": len(jobs),
            "offset": offset,
            "jobs": [
                {
                    "id": job.Job.id,
                    "company": job.Company.name,
                    "title": job.Job.title,
                    "location": job.Job.location,
                    "remote_type": job.Job.remote_type,
                    "salary_range": f"${job.Job.salary_min or 0}-${job.Job.salary_max or 0}" if job.Job.salary_min or job.Job.salary_max else None,
                    "priority": job.Job.priority.value if job.Job.priority else "MEDIUM",
                    "url": job.Job.job_url,
                    "posted_date": job.Job.posted_date.isoformat() if job.Job.posted_date else None,
                    "application_count": job[2],
                    "status": job.Job.status
                }
                for job in jobs
            ]
        }

    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}")
async def get_job_details(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed job information including ATS analysis"""
    try:
        result = await db.execute(
            select(Job, Company).join(
                Company, Job.company_id == Company.id
            ).where(Job.id == job_id)
        )
        job_data = result.first()

        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")

        job, company = job_data

        # Check if applied
        app_result = await db.execute(
            select(Application).where(Application.job_id == job_id)
        )
        application = app_result.scalar_one_or_none()

        # Run ATS analysis
        ats_analysis = None
        if job.job_description:
            try:
                ats_analysis = ats_optimizer.analyze_job_description(job.job_description)
            except Exception as e:
                logger.warning(f"ATS analysis failed: {e}")

        return {
            "id": job.id,
            "company": {
                "id": company.id,
                "name": company.name,
                "website": company.website,
                "linkedin_url": company.linkedin_url
            },
            "title": job.title,
            "job_description": job.job_description,
            "location": job.location,
            "remote_type": job.remote_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "priority": job.priority.value if job.priority else "MEDIUM",
            "url": job.job_url,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "status": job.status,
            "applied": application is not None,
            "application_status": application.status.value if application and application.status else None,
            "ats_analysis": ats_analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{job_id}")
async def update_job(
    job_id: int,
    update_data: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update job information"""
    try:
        result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Update fields
        if update_data.title:
            job.title = update_data.title
        if update_data.job_description:
            job.job_description = update_data.job_description
        if update_data.location:
            job.location = update_data.location
        if update_data.remote_type is not None:
            job.remote_type = update_data.remote_type
        if update_data.salary_min:
            job.salary_min = update_data.salary_min
        if update_data.salary_max:
            job.salary_max = update_data.salary_max
        if update_data.priority:
            job.priority = update_data.priority
        if update_data.status is not None:
            job.status = update_data.status

        job.updated_at = datetime.now()

        await db.commit()

        return {
            "status": "success",
            "message": "Job updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update job: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete or deactivate a job"""
    try:
        # Check if job has applications
        app_result = await db.execute(
            select(func.count(Application.id)).where(Application.job_id == job_id)
        )
        app_count = app_result.scalar()

        if app_count > 0:
            # Deactivate instead of delete if has applications
            result = await db.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                raise HTTPException(status_code=404, detail="Job not found")

            job.status = "closed"
            job.updated_at = datetime.now()
            await db.commit()

            return {
                "status": "success",
                "message": "Job closed (has applications)",
                "applications_count": app_count
            }
        else:
            # Actually delete if no applications
            result = await db.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                raise HTTPException(status_code=404, detail="Job not found")

            await db.delete(job)
            await db.commit()

            return {
                "status": "success",
                "message": "Job deleted successfully"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_job_stats(db: AsyncSession = Depends(get_db)):
    """Get job posting statistics"""
    try:
        # Total active jobs
        active_result = await db.execute(
            select(func.count(Job.id)).where(Job.status.in_(["new", "researching", "ready"]))
        )
        active_count = active_result.scalar()

        # Jobs by priority
        priority_query = select(
            Job.priority,
            func.count(Job.id)
        ).where(Job.status.in_(["new", "researching", "ready"])).group_by(Job.priority)

        priority_result = await db.execute(priority_query)
        priority_breakdown = {
            row[0].value if row[0] else 'MEDIUM': row[1]
            for row in priority_result
        }

        # Jobs with applications
        applied_result = await db.execute(
            select(func.count(func.distinct(Application.job_id)))
        )
        applied_count = applied_result.scalar()

        # Recent jobs (last 7 days)
        recent_date = datetime.now().date() - timedelta(days=7)
        recent_result = await db.execute(
            select(func.count(Job.id)).where(
                and_(
                    Job.posted_date >= recent_date,
                    Job.status.in_(["new", "researching", "ready"])
                )
            )
        )
        recent_count = recent_result.scalar()

        # Top companies
        top_companies_query = select(
            Company.name,
            func.count(Job.id).label('job_count')
        ).join(
            Job, Company.id == Job.company_id
        ).where(
            Job.status.in_(["new", "researching", "ready"])
        ).group_by(Company.name).order_by(
            func.count(Job.id).desc()
        ).limit(5)

        top_companies_result = await db.execute(top_companies_query)
        top_companies = [
            {"name": row[0], "count": row[1]}
            for row in top_companies_result
        ]

        return {
            "active_jobs": active_count,
            "jobs_applied_to": applied_count,
            "recent_jobs_7d": recent_count,
            "priority_breakdown": priority_breakdown,
            "top_companies": top_companies,
            "application_rate": f"{(applied_count / active_count * 100) if active_count > 0 else 0:.1f}%"
        }

    except Exception as e:
        logger.error(f"Failed to get job stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))