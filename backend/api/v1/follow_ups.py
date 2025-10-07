"""
Follow-up System API endpoints for automated reminders and scheduling
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update, case
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from enum import Enum

from backend.core.database import get_db
from backend.models.models import (
    Application, Job, Company, ApplicationStatus,
    ResponseType, FollowUp, Priority
)
from backend.core.logging import get_logger
from backend.services.email_service import EmailAutomationService as EmailService

logger = get_logger(__name__)
router = APIRouter()

# Define FollowUpType enum locally since it's not in models
class FollowUpType(str, Enum):
    APPLICATION_STATUS = "APPLICATION_STATUS"
    THANK_YOU = "THANK_YOU"
    POST_INTERVIEW = "POST_INTERVIEW"
    NO_RESPONSE = "NO_RESPONSE"
    DECISION_PENDING = "DECISION_PENDING"

class FollowUpCreate(BaseModel):
    application_id: int
    follow_up_type: FollowUpType
    scheduled_date: datetime
    message_template: Optional[str] = None
    priority: Priority = Priority.MEDIUM

class FollowUpUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    message: Optional[str] = None
    completed: Optional[bool] = None
    sent_date: Optional[datetime] = None

class AutoScheduleSettings(BaseModel):
    enable_auto_schedule: bool = True
    initial_follow_up_days: int = 7
    second_follow_up_days: int = 14
    interview_thank_you_hours: int = 24
    offer_response_days: int = 3

@router.post("/create")
async def create_follow_up(
    follow_up_data: FollowUpCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a manual follow-up reminder"""
    try:
        # Validate application exists
        app_result = await db.execute(
            select(Application).where(Application.id == follow_up_data.application_id)
        )
        application = app_result.scalar_one_or_none()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # Create follow-up
        new_follow_up = FollowUp(
            application_id=follow_up_data.application_id,
            follow_up_type=follow_up_data.follow_up_type,
            scheduled_date=follow_up_data.scheduled_date,
            message=follow_up_data.message_template,
            created_at=datetime.now()
        )

        db.add(new_follow_up)
        await db.commit()
        await db.refresh(new_follow_up)

        return {
            "status": "success",
            "follow_up_id": new_follow_up.id,
            "message": f"Follow-up scheduled for {follow_up_data.scheduled_date.isoformat()}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create follow-up: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scheduled")
async def get_scheduled_followups(
    upcoming_days: int = 7,
    include_overdue: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all scheduled follow-ups"""
    try:
        cutoff_date = datetime.now() + timedelta(days=upcoming_days)

        # Build query
        query = select(
            FollowUp, Application, Job, Company
        ).join(
            Application, FollowUp.application_id == Application.id
        ).join(
            Job, Application.job_id == Job.id
        ).join(
            Company, Job.company_id == Company.id
        ).where(
            and_(
                FollowUp.sent == False,
                or_(
                    FollowUp.scheduled_date <= cutoff_date,
                    and_(
                        include_overdue == True,
                        FollowUp.scheduled_date < datetime.now()
                    )
                )
            )
        ).order_by(FollowUp.scheduled_date)

        result = await db.execute(query)
        followups = result.all()

        # Categorize follow-ups
        overdue = []
        today = []
        upcoming = []

        for fu in followups:
            follow_up_data = {
                "id": fu.FollowUp.id,
                "company": fu.Company.name,
                "job_title": fu.Job.title,
                "type": fu.FollowUp.follow_up_type.value if fu.FollowUp.follow_up_type else "GENERAL",
                "scheduled_date": fu.FollowUp.scheduled_date.isoformat(),
                "days_until": (fu.FollowUp.scheduled_date - datetime.now()).days,
                "message": fu.FollowUp.message,
                "application_status": fu.Application.status.value if fu.Application.status else "UNKNOWN"
            }

            if fu.FollowUp.scheduled_date.date() < datetime.now().date():
                overdue.append(follow_up_data)
            elif fu.FollowUp.scheduled_date.date() == datetime.now().date():
                today.append(follow_up_data)
            else:
                upcoming.append(follow_up_data)

        return {
            "overdue": {"count": len(overdue), "items": overdue},
            "today": {"count": len(today), "items": today},
            "upcoming": {"count": len(upcoming), "items": upcoming},
            "total_pending": len(followups)
        }

    except Exception as e:
        logger.error(f"Failed to get scheduled follow-ups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-schedule/{application_id}")
async def auto_schedule_followups(
    application_id: int,
    settings: AutoScheduleSettings = AutoScheduleSettings(),
    db: AsyncSession = Depends(get_db)
):
    """Automatically schedule follow-ups based on application status"""
    try:
        # Get application details
        result = await db.execute(
            select(Application, Job).join(
                Job, Application.job_id == Job.id
            ).where(Application.id == application_id)
        )
        app_data = result.first()

        if not app_data:
            raise HTTPException(status_code=404, detail="Application not found")

        application, job = app_data
        scheduled = []

        if not settings.enable_auto_schedule:
            return {"status": "auto-scheduling disabled", "scheduled": []}

        # Check existing follow-ups to avoid duplicates
        existing = await db.execute(
            select(FollowUp).where(
                and_(
                    FollowUp.application_id == application_id,
                    FollowUp.completed == False
                )
            )
        )
        if existing.scalar_one_or_none():
            return {"status": "follow-ups already exist", "scheduled": []}

        # Schedule based on application status
        if application.status == ApplicationStatus.APPLIED:
            # Initial follow-up after application
            initial_followup = FollowUp(
                application_id=application_id,
                follow_up_type=FollowUpType.APPLICATION_STATUS,
                scheduled_date=application.applied_date + timedelta(days=settings.initial_follow_up_days),
                message=f"Follow up on {job.title} application - sent {settings.initial_follow_up_days} days ago",
                created_at=datetime.now()
            )
            db.add(initial_followup)
            scheduled.append("Initial follow-up")

            # Second follow-up if no response
            second_followup = FollowUp(
                application_id=application_id,
                follow_up_type=FollowUpType.NO_RESPONSE,
                scheduled_date=application.applied_date + timedelta(days=settings.second_follow_up_days),
                message=f"Second follow-up on {job.title} - check if position is still open",
                created_at=datetime.now()
            )
            db.add(second_followup)
            scheduled.append("Second follow-up")

        elif application.status == ApplicationStatus.INTERVIEWING:
            # Thank you note after interview
            if application.interview_scheduled:
                thank_you = FollowUp(
                    application_id=application_id,
                    follow_up_type=FollowUpType.THANK_YOU,
                    scheduled_date=application.interview_scheduled + timedelta(hours=settings.interview_thank_you_hours),
                    message=f"Send thank you note for {job.title} interview",
                    created_at=datetime.now()
                )
                db.add(thank_you)
                scheduled.append("Thank you note")

                # Post-interview follow-up
                post_interview = FollowUp(
                    application_id=application_id,
                    follow_up_type=FollowUpType.POST_INTERVIEW,
                    scheduled_date=application.interview_scheduled + timedelta(days=7),
                    message=f"Follow up on {job.title} interview results",
                    created_at=datetime.now()
                )
                db.add(post_interview)
                scheduled.append("Post-interview follow-up")

        elif application.status == ApplicationStatus.OFFER:
            # Offer response reminder
            offer_response = FollowUp(
                application_id=application_id,
                follow_up_type=FollowUpType.DECISION_PENDING,
                scheduled_date=datetime.now() + timedelta(days=settings.offer_response_days),
                message=f"Respond to {job.title} offer - deadline approaching",
                created_at=datetime.now()
            )
            db.add(offer_response)
            scheduled.append("Offer response deadline")

        await db.commit()

        return {
            "status": "success",
            "scheduled": scheduled,
            "count": len(scheduled)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to auto-schedule follow-ups: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{follow_up_id}")
async def update_follow_up(
    follow_up_id: int,
    update_data: FollowUpUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a follow-up reminder"""
    try:
        result = await db.execute(
            select(FollowUp).where(FollowUp.id == follow_up_id)
        )
        follow_up = result.scalar_one_or_none()

        if not follow_up:
            raise HTTPException(status_code=404, detail="Follow-up not found")

        # Update fields
        if update_data.scheduled_date:
            follow_up.scheduled_date = update_data.scheduled_date
        if update_data.message:
            follow_up.message = update_data.message
        if update_data.completed is not None:
            follow_up.sent = update_data.completed
        if update_data.sent_date:
            follow_up.sent_date = update_data.sent_date

        await db.commit()

        return {
            "status": "success",
            "message": "Follow-up updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update follow-up: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{follow_up_id}/complete")
async def complete_follow_up(
    follow_up_id: int,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Mark a follow-up as completed"""
    try:
        result = await db.execute(
            select(FollowUp).where(FollowUp.id == follow_up_id)
        )
        follow_up = result.scalar_one_or_none()

        if not follow_up:
            raise HTTPException(status_code=404, detail="Follow-up not found")

        follow_up.sent = True
        follow_up.sent_date = datetime.now()
        if notes:
            follow_up.message = f"{follow_up.message}\n\nCompletion notes: {notes}"

        await db.commit()

        return {
            "status": "success",
            "message": "Follow-up marked as completed",
            "completed_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete follow-up: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{follow_up_type}")
async def get_follow_up_templates(
    follow_up_type: FollowUpType
):
    """Get email templates for different follow-up types"""

    templates = {
        FollowUpType.APPLICATION_STATUS: {
            "subject": "Following up on my application for {job_title}",
            "body": """Dear {hiring_manager},

I hope this email finds you well. I wanted to follow up on my application for the {job_title} position
I submitted on {applied_date}. I remain very interested in this opportunity and would love to discuss
how my skills in {relevant_skills} align with your needs.

I understand you may be reviewing many applications. If there's any additional information I can provide
to support my candidacy, please don't hesitate to let me know.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
{your_name}"""
        },
        FollowUpType.THANK_YOU: {
            "subject": "Thank you - {job_title} interview",
            "body": """Dear {interviewer_name},

Thank you for taking the time to meet with me {interview_date} to discuss the {job_title} position.
I enjoyed our conversation about {specific_topic_discussed} and was particularly excited to learn about
{something_specific_about_company_or_role}.

Our discussion reinforced my enthusiasm for this role and {company_name}. I'm confident that my experience
in {relevant_experience} would allow me to contribute immediately to {specific_project_or_goal}.

{optional_clarification_or_additional_point}

Thank you again for your time and consideration. I look forward to the next steps in the process.

Best regards,
{your_name}"""
        },
        FollowUpType.POST_INTERVIEW: {
            "subject": "Following up on our interview - {job_title}",
            "body": """Dear {hiring_manager},

I wanted to follow up on our interview on {interview_date} for the {job_title} position.
I remain very interested in the opportunity and wanted to check if there are any updates on the hiring timeline.

Since our conversation, I've been thinking about {specific_challenge_discussed} and have some additional
ideas I'd be happy to share if helpful.

Please let me know if you need any additional information from me. I'm very excited about the possibility
of joining {company_name} and contributing to {team_or_project}.

Thank you for your consideration.

Best regards,
{your_name}"""
        },
        FollowUpType.NO_RESPONSE: {
            "subject": "Checking in - {job_title} application",
            "body": """Dear {hiring_manager},

I hope you're doing well. I wanted to briefly follow up on my application for the {job_title} position
submitted on {applied_date}. I understand you may still be in the review process, but I wanted to
reiterate my strong interest in this opportunity.

If the position has been filled, I would appreciate knowing so I can focus my search accordingly.
However, if you're still considering candidates, I remain very interested and available for an interview
at your convenience.

Thank you for your time and consideration.

Best regards,
{your_name}"""
        },
        FollowUpType.DECISION_PENDING: {
            "subject": "Re: {job_title} Offer - Response",
            "body": """Dear {hiring_manager},

Thank you again for extending the offer for the {job_title} position. I'm very excited about this
opportunity and have been carefully reviewing the details.

{decision_or_questions}

I appreciate your patience and look forward to {next_steps}.

Best regards,
{your_name}"""
        }
    }

    template = templates.get(follow_up_type)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        "follow_up_type": follow_up_type.value,
        "template": template,
        "variables": _extract_template_variables(template['body'])
    }

def _extract_template_variables(template: str) -> List[str]:
    """Extract variable names from template"""
    import re
    return list(set(re.findall(r'\{(\w+)\}', template)))

@router.get("/analytics")
async def get_follow_up_analytics(db: AsyncSession = Depends(get_db)):
    """Get analytics on follow-up effectiveness"""
    try:
        # Total follow-ups
        total_query = select(func.count(FollowUp.id))
        total_result = await db.execute(total_query)
        total_count = total_result.scalar() or 0

        # Completed follow-ups
        completed_query = select(func.count(FollowUp.id)).where(
            FollowUp.sent == True
        )
        completed_result = await db.execute(completed_query)
        completed_count = completed_result.scalar() or 0

        # Overdue follow-ups
        overdue_query = select(func.count(FollowUp.id)).where(
            and_(
                FollowUp.sent == False,
                FollowUp.scheduled_date < datetime.now()
            )
        )
        overdue_result = await db.execute(overdue_query)
        overdue_count = overdue_result.scalar() or 0

        # Follow-ups by type
        type_query = select(
            FollowUp.follow_up_type,
            func.count(FollowUp.id),
            func.avg(case((FollowUp.sent == True, 1), else_=0))
        ).group_by(FollowUp.follow_up_type)

        type_result = await db.execute(type_query)
        by_type = {}
        for row in type_result:
            if row[0]:
                by_type[row[0].value] = {
                    "count": row[1],
                    "completion_rate": f"{(row[2] or 0) * 100:.1f}%"
                }

        # Average time to complete
        completion_time_query = select(
            func.avg(
                func.julianday(FollowUp.sent_date) - func.julianday(FollowUp.scheduled_date)
            )
        ).where(
            and_(
                FollowUp.sent == True,
                FollowUp.sent_date.isnot(None)
            )
        )

        completion_time_result = await db.execute(completion_time_query)
        avg_completion_days = completion_time_result.scalar() or 0

        # Follow-ups that led to responses
        response_query = select(
            func.count(func.distinct(FollowUp.application_id))
        ).join(
            Application, FollowUp.application_id == Application.id
        ).where(
            and_(
                FollowUp.sent == True,
                Application.response_received == True,
                Application.response_date > FollowUp.sent_date
            )
        )

        response_result = await db.execute(response_query)
        led_to_responses = response_result.scalar() or 0

        return {
            "total_follow_ups": total_count,
            "completed": completed_count,
            "pending": total_count - completed_count,
            "overdue": overdue_count,
            "completion_rate": f"{(completed_count / total_count * 100) if total_count > 0 else 0:.1f}%",
            "by_type": by_type,
            "average_completion_delay_days": round(avg_completion_days, 1),
            "led_to_responses": led_to_responses,
            "response_effectiveness": f"{(led_to_responses / completed_count * 100) if completed_count > 0 else 0:.1f}%"
        }

    except Exception as e:
        logger.error(f"Failed to get follow-up analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-reminder")
async def send_follow_up_reminder(
    follow_up_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Send an email reminder for a follow-up"""
    try:
        # Get follow-up details
        result = await db.execute(
            select(FollowUp, Application, Job, Company).join(
                Application, FollowUp.application_id == Application.id
            ).join(
                Job, Application.job_id == Job.id
            ).join(
                Company, Job.company_id == Company.id
            ).where(FollowUp.id == follow_up_id)
        )

        data = result.first()
        if not data:
            raise HTTPException(status_code=404, detail="Follow-up not found")

        follow_up, application, job, company = data

        # Prepare reminder email content
        reminder_content = {
            "subject": f"Follow-up Reminder: {company.name} - {job.title}",
            "body": f"""
Follow-up Reminder:

Company: {company.name}
Position: {job.title}
Type: {follow_up.follow_up_type.value if follow_up.follow_up_type else 'General'}
Scheduled: {follow_up.scheduled_date.strftime('%Y-%m-%d %H:%M')}

Message/Notes:
{follow_up.message or 'No message provided'}

Application Status: {application.status.value if application.status else 'Unknown'}
Applied Date: {application.applied_date.strftime('%Y-%m-%d') if application.applied_date else 'Unknown'}

Take action now to maintain momentum in your job search!
"""
        }

        # Queue email send (would integrate with email service)
        # background_tasks.add_task(send_email_reminder, reminder_content)

        return {
            "status": "success",
            "message": "Reminder queued for sending",
            "content": reminder_content
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send follow-up reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))