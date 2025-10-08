"""
Follow-up Automation Service
Implements intelligent follow-up detection and scheduling logic
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.core.logging import get_logger
from backend.models.models import (
    Application, ApplicationStatus, Job, Company, FollowUp
)
from backend.core.config import settings

logger = get_logger(__name__)


# Email template for follow-ups
FOLLOWUP_EMAIL_TEMPLATE = """
Hi there,

I wanted to follow up on my application for the {job_title} position at {company_name} that I submitted on {applied_date}.

I remain very interested in this opportunity and would appreciate any update on the status of my application.

Thank you for your time and consideration.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
"""


class FollowUpService:
    """Manages automatic follow-up detection and scheduling"""

    # Configurable thresholds
    DEFAULT_FOLLOWUP_DAYS = 7  # Days after application before first follow-up
    RESPONSE_TIMEOUT_DAYS = 14  # Days to wait before second follow-up
    MAX_FOLLOW_UPS = 2  # Maximum automatic follow-ups per application

    def __init__(self, followup_days: int = None):
        """
        Initialize follow-up service

        Args:
            followup_days: Days to wait before scheduling follow-up (default: 7)
        """
        self.followup_days = followup_days or self.DEFAULT_FOLLOWUP_DAYS
        logger.info(f"FollowUpService initialized with {self.followup_days} day threshold")

    async def check_and_schedule_followup_emails(
        self,
        db: AsyncSession,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Check for applications needing follow-ups and schedule them

        This function identifies applications that:
        1. Have status APPLIED (waiting for response)
        2. Have applied_date older than configurable threshold (default: 7 days)
        3. Have followup_sent = False (haven't been flagged for follow-up yet)
        4. Haven't received a response
        5. Haven't exceeded max follow-ups

        Args:
            db: Async database session
            dry_run: If True, only logs what would be done (default: True for safety)

        Returns:
            Dictionary with results:
            {
                'applications_checked': int,
                'followups_needed': int,
                'applications_updated': list,
                'dry_run': bool
            }
        """
        logger.info("Starting follow-up check...")

        # Calculate cutoff date (applications older than this need follow-up)
        cutoff_date = datetime.now() - timedelta(days=self.followup_days)

        # Build query for applications needing follow-up
        query = select(Application).join(Job).join(Company).where(
            and_(
                # Status criteria: waiting for response
                Application.status.in_([
                    ApplicationStatus.APPLIED,
                    ApplicationStatus.READY  # Include ready if they were essentially applied
                ]),
                # Time criteria: older than threshold
                Application.applied_date < cutoff_date,
                Application.applied_date.is_not(None),  # Must have an application date
                # Follow-up criteria
                Application.followup_sent == False,  # Haven't been flagged yet
                Application.response_received == False,  # No response received
                # Safety: don't exceed max follow-ups
                Application.follow_ups_sent < self.MAX_FOLLOW_UPS
            )
        )

        result = await db.execute(query)
        applications = result.scalars().all()

        logger.info(f"Found {len(applications)} applications needing follow-up")

        # Prepare results
        results = {
            'applications_checked': len(applications),
            'followups_needed': 0,
            'applications_updated': [],
            'dry_run': dry_run
        }

        for app in applications:
            # Load related job and company for context
            await db.refresh(app, ['job'])
            await db.refresh(app.job, ['company'])

            days_since_application = (datetime.now() - app.applied_date).days

            app_info = {
                'application_id': app.id,
                'job_title': app.job.title,
                'company_name': app.job.company.name if app.job.company else 'Unknown',
                'applied_date': app.applied_date.strftime('%Y-%m-%d'),
                'days_since_application': days_since_application,
                'current_followups_sent': app.follow_ups_sent,
                'status': app.status.value
            }

            if dry_run:
                # Dry run: just log what would happen
                logger.info(
                    f"[DRY RUN] Would schedule follow-up for: "
                    f"{app_info['company_name']} - {app_info['job_title']} "
                    f"(Applied {days_since_application} days ago)"
                )
            else:
                # Actually update the database
                app.followup_sent = True
                app.next_follow_up_scheduled = datetime.now() + timedelta(days=1)
                # Note: We're not incrementing follow_ups_sent yet because we haven't
                # actually sent the follow-up, just flagged it for scheduling

                logger.info(
                    f"Scheduled follow-up for: {app_info['company_name']} - "
                    f"{app_info['job_title']} (Applied {days_since_application} days ago)"
                )

            results['followups_needed'] += 1
            results['applications_updated'].append(app_info)

        if not dry_run:
            await db.commit()
            logger.info(f"Updated {len(results['applications_updated'])} applications with follow-up flag")
        else:
            logger.info("[DRY RUN] No database changes made")

        return results

    async def get_pending_followups(
        self,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Get list of applications that have been flagged for follow-up but not yet sent

        Returns:
            List of application details ready for follow-up
        """
        query = select(Application).join(Job).join(Company).where(
            and_(
                Application.followup_sent == True,
                Application.follow_ups_sent < self.MAX_FOLLOW_UPS,
                # Could add: Application.next_follow_up_scheduled <= datetime.now()
            )
        )

        result = await db.execute(query)
        applications = result.scalars().all()

        pending_followups = []
        for app in applications:
            await db.refresh(app, ['job'])
            await db.refresh(app.job, ['company'])

            pending_followups.append({
                'application_id': app.id,
                'job_title': app.job.title,
                'company_name': app.job.company.name if app.job.company else 'Unknown',
                'company_id': app.job.company_id,
                'applied_date': app.applied_date.strftime('%Y-%m-%d') if app.applied_date else None,
                'days_since_application': (
                    (datetime.now() - app.applied_date).days
                    if app.applied_date else None
                ),
                'status': app.status.value,
                'follow_ups_sent': app.follow_ups_sent,
                'next_follow_up_scheduled': (
                    app.next_follow_up_scheduled.strftime('%Y-%m-%d %H:%M')
                    if app.next_follow_up_scheduled else None
                )
            })

        logger.info(f"Found {len(pending_followups)} pending follow-ups")
        return pending_followups

    async def mark_followup_sent(
        self,
        db: AsyncSession,
        application_id: int
    ) -> bool:
        """
        Mark a follow-up as sent for an application

        Args:
            db: Async database session
            application_id: ID of the application

        Returns:
            True if successful, False otherwise
        """
        try:
            query = select(Application).where(Application.id == application_id)
            result = await db.execute(query)
            app = result.scalar_one_or_none()

            if not app:
                logger.error(f"Application {application_id} not found")
                return False

            # Update follow-up tracking
            app.follow_ups_sent += 1
            app.last_follow_up = datetime.now()
            app.followup_sent = False  # Reset flag since we've handled this one

            # Schedule next follow-up if under limit
            if app.follow_ups_sent < self.MAX_FOLLOW_UPS:
                app.next_follow_up_scheduled = datetime.now() + timedelta(
                    days=self.RESPONSE_TIMEOUT_DAYS
                )

            await db.commit()
            logger.info(
                f"Marked follow-up sent for application {application_id} "
                f"(Total: {app.follow_ups_sent})"
            )
            return True

        except Exception as e:
            logger.error(f"Error marking follow-up sent: {e}")
            await db.rollback()
            return False

    async def create_followup_record(
        self,
        db: AsyncSession,
        application_id: int,
        scheduled_date: datetime,
        subject: str,
        message: str,
        recipient: str = None,
        channel: str = "email"
    ) -> Optional[int]:
        """
        Create a FollowUp record in the database

        Args:
            db: Async database session
            application_id: Application to follow up on
            scheduled_date: When to send the follow-up
            subject: Email subject
            message: Email body
            recipient: Recipient email (optional)
            channel: Communication channel (default: email)

        Returns:
            FollowUp ID if created, None otherwise
        """
        try:
            followup = FollowUp(
                application_id=application_id,
                scheduled_date=scheduled_date,
                channel=channel,
                recipient=recipient,
                subject=subject,
                message=message,
                sent=False
            )

            db.add(followup)
            await db.commit()
            await db.refresh(followup)

            logger.info(f"Created follow-up record {followup.id} for application {application_id}")
            return followup.id

        except Exception as e:
            logger.error(f"Error creating follow-up record: {e}")
            await db.rollback()
            return None


    async def send_followup_email_safe(
        self,
        db: AsyncSession,
        application_id: int,
        email_service
    ) -> Dict[str, Any]:
        """
        Send follow-up email with safety override

        Uses TEST_RECIPIENT_OVERRIDE to send all emails to the test address
        Only sends if LIVE_SEND_MODE is True

        Args:
            db: Async database session
            application_id: Application to follow up on
            email_service: EmailAutomationService instance

        Returns:
            Result dictionary with send status
        """
        try:
            # Get application with related data
            query = select(Application).where(Application.id == application_id)
            result = await db.execute(query)
            app = result.scalar_one_or_none()

            if not app:
                return {'success': False, 'error': 'Application not found'}

            # Load related job and company
            await db.refresh(app, ['job'])
            await db.refresh(app.job, ['company'])

            # Safety check: Only send if LIVE_SEND_MODE is enabled
            if not settings.LIVE_SEND_MODE:
                logger.warning(
                    f"[SAFETY] Email sending disabled (LIVE_SEND_MODE=False). "
                    f"Would have sent to: {settings.TEST_RECIPIENT_OVERRIDE}"
                )
                return {
                    'success': False,
                    'dry_run': True,
                    'message': 'LIVE_SEND_MODE is False - no email sent (safety)'
                }

            # Prepare email content
            subject = f"Following up on {app.job.title} application"
            body = FOLLOWUP_EMAIL_TEMPLATE.format(
                job_title=app.job.title,
                company_name=app.job.company.name if app.job.company else "your company",
                applied_date=app.applied_date.strftime('%B %d, %Y') if app.applied_date else "recently"
            )

            # SAFETY: Always use TEST_RECIPIENT_OVERRIDE
            recipient = settings.TEST_RECIPIENT_OVERRIDE
            logger.info(
                f"[SAFETY OVERRIDE] Sending follow-up to TEST address: {recipient} "
                f"(Application #{application_id}: {app.job.company.name if app.job.company else 'Unknown'})"
            )

            # Send the email
            success = await email_service.send_follow_up(
                to_email=recipient,
                subject=subject,
                body=body
            )

            if success:
                # Mark as sent in database
                await self.mark_followup_sent(db, application_id)

                return {
                    'success': True,
                    'application_id': application_id,
                    'recipient': recipient,
                    'timestamp': datetime.now().isoformat(),
                    'job_title': app.job.title,
                    'company': app.job.company.name if app.job.company else 'Unknown'
                }
            else:
                return {
                    'success': False,
                    'error': 'Email send failed (check email_service logs)'
                }

        except Exception as e:
            logger.error(f"Error sending follow-up email: {e}")
            return {'success': False, 'error': str(e)}


# Singleton instance
followup_service = FollowUpService()
