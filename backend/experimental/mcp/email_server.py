#!/usr/bin/env python3
"""
Email Intelligence MCP Server
Automates email monitoring, classification, and response tracking
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
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

# Import existing services and models
from backend.core.database import get_session, engine, Base
from backend.models.models import (
    EmailTracking, Application, Job, Company,
    ApplicationStatus, ResponseType
)
from backend.services.email_service import EmailAutomationService
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Initialize MCP server
mcp = FastMCP("Email Intelligence")

# Initialize email service
email_service = EmailAutomationService()


# ====================
# Resources (Data Access)
# ====================

@mcp.resource("email://unread_responses")
async def get_unread_responses() -> str:
    """Get unread job application responses requiring action"""
    try:
        async with get_session() as session:
            # Get recent unread email responses
            result = await session.execute(
                select(EmailTracking)
                .where(
                    and_(
                        EmailTracking.is_read == False,
                        EmailTracking.response_type.in_([
                            ResponseType.INTERVIEW,
                            ResponseType.INFO_REQUEST,
                            ResponseType.OFFER
                        ])
                    )
                )
                .order_by(EmailTracking.received_date.desc())
            )
            emails = result.scalars().all()

            email_data = []
            for email in emails:
                # Get associated application if exists
                app = None
                if email.application_id:
                    app_result = await session.execute(
                        select(Application).where(Application.id == email.application_id)
                    )
                    app = app_result.scalar_one_or_none()

                email_data.append({
                    "id": email.id,
                    "subject": email.subject,
                    "sender": email.sender_email,
                    "company": email.company_name,
                    "response_type": email.response_type.value if email.response_type else "UNKNOWN",
                    "received_date": email.received_date.isoformat() if email.received_date else None,
                    "snippet": email.email_snippet[:200] if email.email_snippet else None,
                    "requires_action": True,
                    "application_id": email.application_id,
                    "job_title": app.job.title if app and hasattr(app, 'job') else None
                })

            return json.dumps({
                "unread_count": len(email_data),
                "emails": email_data
            }, indent=2)

    except Exception as e:
        logger.error(f"Error getting unread responses: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.resource("email://interview_invites")
async def get_interview_invites() -> str:
    """Get all detected interview invitations"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(EmailTracking)
                .where(EmailTracking.response_type == ResponseType.INTERVIEW)
                .order_by(EmailTracking.received_date.desc())
            )
            interviews = result.scalars().all()

            interview_data = []
            for email in interviews:
                interview_data.append({
                    "id": email.id,
                    "company": email.company_name,
                    "subject": email.subject,
                    "sender": email.sender_email,
                    "received_date": email.received_date.isoformat() if email.received_date else None,
                    "is_read": email.is_read,
                    "snippet": email.email_snippet[:300] if email.email_snippet else None,
                    "application_id": email.application_id
                })

            return json.dumps({
                "total_interviews": len(interview_data),
                "interviews": interview_data,
                "stats": {
                    "unread": sum(1 for i in interview_data if not i["is_read"]),
                    "this_week": sum(
                        1 for i in interview_data
                        if i["received_date"] and
                        datetime.fromisoformat(i["received_date"]) > datetime.utcnow() - timedelta(days=7)
                    )
                }
            }, indent=2)

    except Exception as e:
        logger.error(f"Error getting interview invites: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.resource("email://metrics")
async def get_email_metrics() -> str:
    """Get email campaign performance metrics"""
    try:
        async with get_session() as session:
            # Get all email tracking records
            result = await session.execute(select(EmailTracking))
            emails = result.scalars().all()

            # Calculate metrics
            total_responses = len(emails)
            response_types = {}
            companies = {}
            sources = {}

            for email in emails:
                # Count by response type
                rtype = email.response_type.value if email.response_type else "UNKNOWN"
                response_types[rtype] = response_types.get(rtype, 0) + 1

                # Count by company
                if email.company_name:
                    companies[email.company_name] = companies.get(email.company_name, 0) + 1

                # Count by source
                if email.source_portal:
                    sources[email.source_portal] = sources.get(email.source_portal, 0) + 1

            # Calculate response rate
            apps_result = await session.execute(select(Application))
            total_applications = len(apps_result.scalars().all())
            response_rate = (total_responses / total_applications * 100) if total_applications else 0

            # Time to response analysis
            time_to_response = []
            for email in emails:
                if email.application_id and email.received_date:
                    app_result = await session.execute(
                        select(Application).where(Application.id == email.application_id)
                    )
                    app = app_result.scalar_one_or_none()
                    if app and app.applied_date:
                        days = (email.received_date - app.applied_date).days
                        time_to_response.append(days)

            avg_response_time = sum(time_to_response) / len(time_to_response) if time_to_response else 0

            return json.dumps({
                "overview": {
                    "total_responses": total_responses,
                    "total_applications": total_applications,
                    "response_rate": f"{response_rate:.1f}%",
                    "avg_response_time_days": round(avg_response_time, 1)
                },
                "breakdown": {
                    "by_type": response_types,
                    "top_companies": dict(sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]),
                    "by_source": sources
                },
                "conversion": {
                    "interviews": response_types.get("INTERVIEW", 0),
                    "offers": response_types.get("OFFER", 0),
                    "rejections": response_types.get("REJECTION", 0)
                }
            }, indent=2)

    except Exception as e:
        logger.error(f"Error getting email metrics: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.resource("email://templates")
async def get_email_templates() -> str:
    """Get email templates for various scenarios"""
    templates = {
        "follow_up_after_application": {
            "subject": "Following up on my application for {job_title}",
            "body": """Dear Hiring Team,

I hope this email finds you well. I wanted to follow up on my application for the {job_title} position submitted on {date}.

I remain very interested in this opportunity and believe my experience in {relevant_experience} makes me a strong candidate for this role.

I would welcome the chance to discuss how I can contribute to {company_name}. Please let me know if you need any additional information from me.

Thank you for your time and consideration.

Best regards,
{your_name}"""
        },
        "thank_you_after_interview": {
            "subject": "Thank you - {job_title} Interview",
            "body": """Dear {interviewer_name},

Thank you for taking the time to meet with me today to discuss the {job_title} position at {company_name}.

I was particularly excited to learn about {specific_topic_discussed}. Our conversation reinforced my enthusiasm for this role and how my experience with {relevant_skill} could contribute to your team's goals.

I look forward to the next steps in the process. Please don't hesitate to reach out if you need any additional information.

Best regards,
{your_name}"""
        },
        "response_to_info_request": {
            "subject": "Re: {original_subject} - Additional Information",
            "body": """Dear {recruiter_name},

Thank you for your email regarding the {job_title} position.

{requested_information}

I've attached the requested documents for your review. Please let me know if you need anything else.

I look forward to hearing from you.

Best regards,
{your_name}"""
        }
    }

    return json.dumps(templates, indent=2)


# ====================
# Tools (Actions)
# ====================

@mcp.tool()
async def scan_inbox(
    days_back: int = 7,
    keywords: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Scan Gmail inbox for job application responses

    Args:
        days_back: Number of days to look back
        keywords: Optional keywords to filter emails

    Returns:
        Dictionary with scan results and new responses found
    """
    try:
        # Use the email service to scan inbox
        if not email_service.service:
            return {
                "success": False,
                "error": "Gmail service not initialized. Please set up OAuth credentials."
            }

        # Build query
        query_parts = [
            f'after:{(datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")}',
            'in:inbox'
        ]

        if keywords:
            keyword_query = " OR ".join([f'"{kw}"' for kw in keywords])
            query_parts.append(f'({keyword_query})')
        else:
            # Default job-related keywords
            query_parts.append('("application" OR "interview" OR "position" OR "opportunity" OR "candidate")')

        query = " ".join(query_parts)

        # Search emails
        results = email_service.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=50
        ).execute()

        messages = results.get('messages', [])
        new_responses = []

        async with get_session() as session:
            for msg_ref in messages:
                # Get full message
                msg = email_service.service.users().messages().get(
                    userId='me',
                    id=msg_ref['id']
                ).execute()

                # Parse message
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)

                # Get message body
                body = email_service._extract_email_body(msg['payload'])

                # Classify the email
                response_type = email_service._classify_response(subject, body)

                # Extract company name
                company_name = email_service._extract_company_name(sender, subject, body)

                # Check if already tracked
                existing = await session.execute(
                    select(EmailTracking).where(EmailTracking.email_id == msg_ref['id'])
                )
                if not existing.scalar_one_or_none():
                    # Create tracking record
                    email_track = EmailTracking(
                        email_id=msg_ref['id'],
                        subject=subject,
                        sender_email=sender,
                        company_name=company_name,
                        response_type=response_type,
                        received_date=datetime.utcnow(),  # Would parse date_str in production
                        email_snippet=body[:500] if body else None,
                        is_read=False,
                        created_at=datetime.utcnow()
                    )
                    session.add(email_track)
                    new_responses.append({
                        "subject": subject,
                        "company": company_name,
                        "type": response_type.value if response_type else "UNKNOWN"
                    })

            await session.commit()

        return {
            "success": True,
            "emails_scanned": len(messages),
            "new_responses": len(new_responses),
            "responses": new_responses,
            "query_used": query
        }

    except Exception as e:
        logger.error(f"Error scanning inbox: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def classify_response(
    email_id: str,
    override_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Classify or reclassify an email response

    Args:
        email_id: ID of the email to classify
        override_type: Optional manual classification (INTERVIEW, REJECTION, INFO_REQUEST, OFFER, OTHER)

    Returns:
        Dictionary with classification results
    """
    try:
        async with get_session() as session:
            result = await session.execute(
                select(EmailTracking).where(EmailTracking.id == email_id)
            )
            email = result.scalar_one_or_none()

            if not email:
                return {"success": False, "error": f"Email {email_id} not found"}

            if override_type:
                # Manual classification
                email.response_type = ResponseType[override_type.upper()]
                classification = override_type
            else:
                # Auto-classify based on content
                if email_service.service and email.email_id:
                    # Get full message from Gmail
                    msg = email_service.service.users().messages().get(
                        userId='me',
                        id=email.email_id
                    ).execute()
                    body = email_service._extract_email_body(msg['payload'])
                    classification = email_service._classify_response(email.subject, body)
                    email.response_type = classification
                else:
                    classification = email.response_type

            email.updated_at = datetime.utcnow()
            await session.commit()

            # Update associated application status if needed
            if email.application_id:
                app_result = await session.execute(
                    select(Application).where(Application.id == email.application_id)
                )
                app = app_result.scalar_one_or_none()
                if app:
                    if classification == ResponseType.INTERVIEW:
                        app.status = ApplicationStatus.INTERVIEWING
                    elif classification == ResponseType.REJECTION:
                        app.status = ApplicationStatus.REJECTED
                    elif classification == ResponseType.OFFER:
                        app.status = ApplicationStatus.OFFERED
                    await session.commit()

            return {
                "success": True,
                "email_id": email_id,
                "classification": classification.value if classification else "UNKNOWN",
                "company": email.company_name,
                "application_updated": bool(email.application_id)
            }

    except Exception as e:
        logger.error(f"Error classifying response: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def mark_email_read(
    email_id: str
) -> Dict[str, Any]:
    """
    Mark an email as read/processed

    Args:
        email_id: ID of the email to mark as read

    Returns:
        Dictionary with confirmation
    """
    try:
        async with get_session() as session:
            result = await session.execute(
                select(EmailTracking).where(EmailTracking.id == email_id)
            )
            email = result.scalar_one_or_none()

            if not email:
                return {"success": False, "error": f"Email {email_id} not found"}

            email.is_read = True
            email.updated_at = datetime.utcnow()
            await session.commit()

            return {
                "success": True,
                "email_id": email_id,
                "subject": email.subject,
                "company": email.company_name,
                "marked_read": True
            }

    except Exception as e:
        logger.error(f"Error marking email as read: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def link_email_to_application(
    email_id: str,
    application_id: int
) -> Dict[str, Any]:
    """
    Link an email response to a job application

    Args:
        email_id: ID of the email
        application_id: ID of the application to link to

    Returns:
        Dictionary with linking confirmation
    """
    try:
        async with get_session() as session:
            # Get email
            email_result = await session.execute(
                select(EmailTracking).where(EmailTracking.id == email_id)
            )
            email = email_result.scalar_one_or_none()

            if not email:
                return {"success": False, "error": f"Email {email_id} not found"}

            # Get application
            app_result = await session.execute(
                select(Application).where(Application.id == application_id)
            )
            app = app_result.scalar_one_or_none()

            if not app:
                return {"success": False, "error": f"Application {application_id} not found"}

            # Link them
            email.application_id = application_id
            email.updated_at = datetime.utcnow()

            # Update application status based on email type
            if email.response_type == ResponseType.INTERVIEW:
                app.status = ApplicationStatus.INTERVIEWING
                app.last_contact_date = email.received_date
            elif email.response_type == ResponseType.REJECTION:
                app.status = ApplicationStatus.REJECTED
            elif email.response_type == ResponseType.OFFER:
                app.status = ApplicationStatus.OFFERED

            await session.commit()

            return {
                "success": True,
                "email_id": email_id,
                "application_id": application_id,
                "email_subject": email.subject,
                "application_status": app.status.value if app.status else None
            }

    except Exception as e:
        logger.error(f"Error linking email to application: {str(e)}")
        return {"success": False, "error": str(e)}


# ====================
# Prompts (Templates)
# ====================

@mcp.prompt("email_daily_check")
async def email_daily_check_prompt() -> str:
    """Daily email monitoring workflow"""
    return """Perform daily email check for job applications:

1. Scan inbox for new responses (last 7 days)
2. Classify each response:
   - Interview invitations → Mark as INTERVIEW
   - Rejections → Mark as REJECTION
   - Information requests → Mark as INFO_REQUEST
   - Offers → Mark as OFFER

3. For each response:
   - Link to corresponding application if found
   - Update application status
   - Mark high-priority items for action

4. For interview invitations:
   - Extract date, time, and format (phone/video/in-person)
   - Add to calendar
   - Prepare interview prep checklist

5. Generate summary:
   - New responses by type
   - Actions required
   - Follow-ups needed
   - Response rate metrics"""


@mcp.prompt("follow_up_campaign")
async def follow_up_campaign_prompt() -> str:
    """Automated follow-up campaign"""
    return """Create follow-up campaign for applications:

1. Identify applications needing follow-up:
   - No response after 7-10 days
   - Post-interview follow-up (24-48 hours)
   - Status check after 2 weeks

2. For each application:
   - Use appropriate template
   - Personalize with company/role details
   - Reference original application date

3. Track follow-ups:
   - Record follow-up sent date
   - Set reminder for next follow-up
   - Monitor for responses

4. Analyze effectiveness:
   - Response rate after follow-up
   - Optimal timing analysis
   - Template performance"""


async def main():
    """Run the MCP server"""
    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Email Intelligence MCP Server starting...")
    await mcp.run()


if __name__ == "__main__":
    asyncio.run(main())