"""
Application management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.models import Application, Job, Company, ApplicationStatus, Priority
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

class ApplicationCreate(BaseModel):
    job_id: int
    resume_version: str
    cover_letter_version: str
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    interview_scheduled: Optional[datetime] = None
    offer_received: Optional[bool] = None
    offer_amount: Optional[int] = None
    notes: Optional[str] = None

@router.post("/create")
async def create_application(
    application: ApplicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new application record"""
    try:
        # Check if application already exists
        existing = await db.execute(
            select(Application).where(Application.job_id == application.job_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Application already exists for this job")

        # Create application
        new_app = Application(
            job_id=application.job_id,
            applied_date=datetime.now(),
            resume_version=application.resume_version,
            cover_letter_version=application.cover_letter_version,
            status=ApplicationStatus.READY,
            notes=application.notes
        )

        db.add(new_app)
        await db.commit()
        await db.refresh(new_app)

        return {
            "status": "success",
            "application_id": new_app.id,
            "message": "Application created successfully"
        }

    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_applications(
    status: Optional[ApplicationStatus] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List all applications with optional filtering"""
    try:
        query = select(Application, Job, Company).join(
            Job, Application.job_id == Job.id
        ).join(
            Company, Job.company_id == Company.id
        ).order_by(Application.applied_date.desc())

        if status:
            query = query.where(Application.status == status)

        query = query.limit(limit)
        result = await db.execute(query)
        applications = result.all()

        return {
            "count": len(applications),
            "applications": [
                {
                    "id": app.Application.id,
                    "job_title": app.Job.title,
                    "company": app.Company.name,
                    "applied_date": app.Application.applied_date.isoformat() if app.Application.applied_date else None,
                    "status": app.Application.status.value if app.Application.status else "DRAFT",
                    "response_received": app.Application.response_received,
                    "interview_scheduled": app.Application.interview_scheduled.isoformat() if app.Application.interview_scheduled else None,
                    "priority": app.Job.priority.value if app.Job.priority else "MEDIUM"
                }
                for app in applications
            ]
        }

    except Exception as e:
        logger.error(f"Failed to list applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_application_stats(db: AsyncSession = Depends(get_db)):
    """Get application statistics"""
    try:
        # Total applications
        total = await db.execute(select(func.count(Application.id)))
        total_count = total.scalar()

        # Applications by status
        status_query = select(
            Application.status,
            func.count(Application.id)
        ).group_by(Application.status)

        status_result = await db.execute(status_query)
        status_breakdown = {
            row[0].value if row[0] else 'DRAFT': row[1]
            for row in status_result
        }

        # Response rate
        responded = await db.execute(
            select(func.count(Application.id)).where(
                Application.response_received == True
            )
        )
        response_count = responded.scalar()
        response_rate = (response_count / total_count * 100) if total_count > 0 else 0

        # Interview conversion
        interviews = await db.execute(
            select(func.count(Application.id)).where(
                Application.interview_scheduled.isnot(None)
            )
        )
        interview_count = interviews.scalar()
        interview_rate = (interview_count / total_count * 100) if total_count > 0 else 0

        # Average time to response
        avg_response_query = select(
            func.avg(
                func.julianday(Application.response_date) -
                func.julianday(Application.applied_date)
            )
        ).where(
            Application.response_received == True
        )

        avg_response_result = await db.execute(avg_response_query)
        avg_response_days = avg_response_result.scalar() or 0

        return {
            "total_applications": total_count,
            "status_breakdown": status_breakdown,
            "response_rate": f"{response_rate:.1f}%",
            "interview_conversion_rate": f"{interview_rate:.1f}%",
            "average_response_time_days": round(avg_response_days, 1),
            "responses_received": response_count,
            "interviews_scheduled": interview_count
        }

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{application_id}")
async def update_application(
    application_id: int,
    update: ApplicationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an application"""
    try:
        # Get application
        result = await db.execute(
            select(Application).where(Application.id == application_id)
        )
        application = result.scalar_one_or_none()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # Update fields
        if update.status:
            application.status = update.status
        if update.interview_scheduled:
            application.interview_scheduled = update.interview_scheduled
        if update.offer_received is not None:
            application.offer_received = update.offer_received
        if update.offer_amount:
            application.offer_amount = update.offer_amount
        if update.notes:
            application.notes = update.notes

        application.updated_at = datetime.now()

        await db.commit()

        return {
            "status": "success",
            "message": "Application updated successfully"
        }

    except Exception as e:
        logger.error(f"Failed to update application: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/priority/{priority}")
async def get_priority_applications(
    priority: Priority,
    db: AsyncSession = Depends(get_db)
):
    """Get applications by priority level"""
    try:
        query = select(Application, Job, Company).join(
            Job, Application.job_id == Job.id
        ).join(
            Company, Job.company_id == Company.id
        ).where(
            Job.priority == priority
        ).order_by(Application.applied_date.desc())

        result = await db.execute(query)
        applications = result.all()

        return {
            "priority": priority.value,
            "count": len(applications),
            "applications": [
                {
                    "id": app.Application.id,
                    "job_title": app.Job.title,
                    "company": app.Company.name,
                    "status": app.Application.status.value if app.Application.status else "DRAFT",
                    "applied_date": app.Application.applied_date.isoformat() if app.Application.applied_date else None
                }
                for app in applications
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get priority applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))