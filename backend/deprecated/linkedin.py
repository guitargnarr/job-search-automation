"""
LinkedIn Automation API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.core.database import get_db
from backend.services.linkedin_service import linkedin_service
from backend.core.logging import get_logger
from backend.models.models import Job, Company

logger = get_logger(__name__)
router = APIRouter()

class LinkedInCampaignRequest(BaseModel):
    job_id: int
    max_connections: int = 10
    message_template: Optional[str] = None

class ConnectionRequest(BaseModel):
    profile_url: str
    message: str
    job_id: Optional[int] = None

@router.post("/initialize")
async def initialize_linkedin():
    """Initialize LinkedIn automation browser"""
    try:
        await linkedin_service.initialize()
        return {
            "status": "success",
            "message": "LinkedIn browser initialized"
        }
    except Exception as e:
        logger.error(f"LinkedIn initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login_to_linkedin(
    email: Optional[str] = None,
    password: Optional[str] = None
):
    """Login to LinkedIn"""
    try:
        if not linkedin_service.browser:
            await linkedin_service.initialize()

        success = await linkedin_service.login(email, password)

        if success:
            return {
                "status": "success",
                "message": "Successfully logged into LinkedIn"
            }
        else:
            return {
                "status": "error",
                "message": "LinkedIn login failed. Check credentials."
            }

    except Exception as e:
        logger.error(f"LinkedIn login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaign")
async def run_linkedin_campaign(
    request: LinkedInCampaignRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Run targeted LinkedIn campaign for a specific job
    This generates warm leads through systematic networking
    """
    try:
        # Initialize if needed
        if not linkedin_service.browser:
            await linkedin_service.initialize()

        if not linkedin_service.is_logged_in:
            await linkedin_service.login()

        # Run campaign
        results = await linkedin_service.execute_targeted_campaign(
            db,
            request.job_id,
            request.max_connections
        )

        return {
            "status": "success",
            "results": results,
            "message": f"Sent {results['connections_sent']} connection requests"
        }

    except Exception as e:
        logger.error(f"LinkedIn campaign failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-employees")
async def search_company_employees(
    company_name: str,
    target_titles: Optional[List[str]] = None,
    max_results: int = 20
):
    """Search for employees at a specific company"""
    try:
        if not linkedin_service.browser:
            await linkedin_service.initialize()

        if not linkedin_service.is_logged_in:
            await linkedin_service.login()

        employees = await linkedin_service.search_company_employees(
            company_name,
            target_titles,
            max_results
        )

        return {
            "status": "success",
            "employees": employees,
            "count": len(employees),
            "message": f"Found {len(employees)} employees at {company_name}"
        }

    except Exception as e:
        logger.error(f"Employee search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/connect")
async def send_connection_request(
    request: ConnectionRequest
):
    """Send a single connection request"""
    try:
        if not linkedin_service.browser:
            await linkedin_service.initialize()

        if not linkedin_service.is_logged_in:
            await linkedin_service.login()

        success = await linkedin_service.send_connection_request(
            request.profile_url,
            request.message,
            request.job_id
        )

        if success:
            return {
                "status": "success",
                "message": "Connection request sent"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to send connection request"
            }

    except Exception as e:
        logger.error(f"Connection request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/outreach/{job_id}")
async def get_job_outreach(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get LinkedIn outreach history for a job"""
    from backend.models.models import LinkedInOutreach
    from sqlalchemy import select

    query = select(LinkedInOutreach).where(
        LinkedInOutreach.application_id == job_id
    ).order_by(LinkedInOutreach.created_at.desc())

    result = await db.execute(query)
    outreach_records = result.scalars().all()

    return {
        "job_id": job_id,
        "outreach_count": len(outreach_records),
        "outreach": [
            {
                "id": record.id,
                "person_name": record.person_name,
                "person_title": record.person_title,
                "connection_status": record.connection_status,
                "connection_sent": record.connection_sent_date.isoformat() if record.connection_sent_date else None,
                "message_sent": record.message_sent,
                "response_received": record.response_received,
                "relationship_score": record.relationship_score
            }
            for record in outreach_records
        ]
    }

@router.post("/cleanup")
async def cleanup_browser():
    """Clean up browser resources"""
    try:
        await linkedin_service.cleanup()
        return {
            "status": "success",
            "message": "Browser resources cleaned up"
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))