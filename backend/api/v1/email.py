"""
Email API endpoints - Real email automation
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from datetime import datetime, timedelta

from backend.core.database import get_db
from backend.services.email_service import email_service
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/scan")
async def scan_emails(
    background_tasks: BackgroundTasks,
    days_back: int = 30,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Scan inbox for job application responses
    This endpoint triggers the email automation that eliminates manual checking
    """
    try:
        # Run scan in background for better performance
        results = await email_service.scan_for_job_responses(db, days_back)

        return {
            "status": "success",
            "emails_processed": len(results),
            "results": results,
            "message": "Email scan completed. Database updated automatically."
        }

    except Exception as e:
        logger.error(f"Email scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/responses")
async def get_recent_responses(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get recent email responses from applications"""
    from backend.models.models import EmailTracking, ResponseType
    from sqlalchemy import select

    query = select(EmailTracking).where(
        EmailTracking.received_date >= datetime.now() - timedelta(days=days)
    ).order_by(EmailTracking.received_date.desc())

    result = await db.execute(query)
    emails = result.scalars().all()

    return [
        {
            "id": email.id,
            "from": email.from_address,
            "subject": email.subject,
            "date": email.received_date.isoformat() if email.received_date else None,
            "classification": email.classification.value if email.classification else None,
            "confidence": email.confidence_score,
            "application_id": email.application_id,
            "action_required": email.action_required
        }
        for email in emails
    ]

@router.get("/stats")
async def get_email_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get email tracking statistics"""
    from backend.models.models import EmailTracking, ResponseType
    from sqlalchemy import select, func

    # Total emails tracked
    total_query = select(func.count(EmailTracking.id))
    total_result = await db.execute(total_query)
    total_emails = total_result.scalar()

    # Emails by classification
    classification_query = select(
        EmailTracking.classification,
        func.count(EmailTracking.id)
    ).group_by(EmailTracking.classification)

    classification_result = await db.execute(classification_query)
    classifications = {
        str(row[0].value if row[0] else 'unknown'): row[1]
        for row in classification_result
    }

    # Action required count
    action_query = select(func.count(EmailTracking.id)).where(
        EmailTracking.action_required == True
    )
    action_result = await db.execute(action_query)
    action_required = action_result.scalar()

    return {
        "total_emails": total_emails,
        "classifications": classifications,
        "action_required": action_required,
        "message": "Email automation is working and tracking responses"
    }

@router.post("/setup-gmail")
async def setup_gmail_auth():
    """
    Setup Gmail API authentication
    This initiates the OAuth flow for Gmail access
    """
    try:
        # This will open browser for authentication
        email_service._initialize_gmail()

        if email_service.service:
            return {
                "status": "success",
                "message": "Gmail API authenticated successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Gmail authentication failed. Check credentials file."
            }

    except Exception as e:
        logger.error(f"Gmail setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))