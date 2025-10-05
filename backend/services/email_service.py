"""
Gmail Integration Service - Real email automation
This actually reads your emails and updates the database automatically
"""

import os
import base64
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import asyncio
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.models import (
    EmailTracking, Application, Job, Company,
    ApplicationStatus, ResponseType
)

logger = get_logger(__name__)

class EmailAutomationService:
    """Automates email tracking and response detection"""

    def __init__(self):
        self.service = None
        self.credentials = None
        self._initialize_gmail()

    def _initialize_gmail(self):
        """Initialize Gmail API connection"""
        creds = None

        # Token file stores the user's access and refresh tokens
        token_path = Path(settings.GMAIL_TOKEN_FILE)

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(token_path),
                settings.GMAIL_SCOPES
            )

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not Path(settings.GMAIL_CREDENTIALS_FILE).exists():
                    logger.error(f"Gmail credentials file not found: {settings.GMAIL_CREDENTIALS_FILE}")
                    logger.info("Please set up Gmail API credentials first")
                    return

                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GMAIL_CREDENTIALS_FILE,
                    settings.GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.credentials = creds
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API initialized successfully")

    async def scan_for_job_responses(self, db: AsyncSession,
                                    days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Scan inbox for job application responses and automatically update database
        This is the core automation that eliminates manual email checking
        """
        if not self.service:
            logger.error("Gmail service not initialized")
            return []

        try:
            # Build search query for job-related emails
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f'after:{after_date} AND ('
            query += 'from:workday.com OR from:greenhouse.io OR from:lever.co OR '
            query += 'from:taleo.net OR from:icims.com OR from:myworkdayjobs.com OR '
            query += 'subject:"application" OR subject:"interview" OR subject:"opportunity" OR '
            query += 'subject:"position" OR subject:"role" OR subject:"thank you for applying"'
            query += ')'

            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} potential job-related emails")

            processed_emails = []

            for msg in messages:
                try:
                    # Get full message
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()

                    # Extract email data
                    email_data = self._parse_message(message)

                    # Check if we've already processed this email
                    existing = await db.execute(
                        select(EmailTracking).where(
                            EmailTracking.gmail_id == email_data['gmail_id']
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    # Classify the email
                    classification = self._classify_email(email_data)

                    # Try to match to an application
                    application = await self._match_to_application(db, email_data)

                    # Create email tracking record
                    email_tracking = EmailTracking(
                        gmail_id=email_data['gmail_id'],
                        thread_id=email_data['thread_id'],
                        from_address=email_data['from'],
                        to_address=email_data['to'],
                        subject=email_data['subject'],
                        body=email_data['body'][:5000],  # Truncate long emails
                        received_date=email_data['date'],
                        classification=classification['type'],
                        confidence_score=classification['confidence'],
                        application_id=application.id if application else None,
                        processed=True,
                        action_required=classification['action_required']
                    )

                    db.add(email_tracking)

                    # Update application status if matched
                    if application:
                        await self._update_application_status(
                            db, application, classification, email_data
                        )

                    processed_emails.append({
                        'subject': email_data['subject'],
                        'from': email_data['from'],
                        'classification': classification['type'].value,
                        'matched_application': application.id if application else None
                    })

                    logger.info(f"Processed email: {email_data['subject']}")

                except Exception as e:
                    logger.error(f"Error processing message {msg['id']}: {str(e)}")
                    continue

            await db.commit()
            logger.info(f"Successfully processed {len(processed_emails)} new emails")
            return processed_emails

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []

    def _parse_message(self, message: Dict) -> Dict[str, Any]:
        """Extract relevant data from Gmail message"""
        email_data = {
            'gmail_id': message['id'],
            'thread_id': message['threadId'],
            'from': '',
            'to': '',
            'subject': '',
            'body': '',
            'date': None
        }

        # Parse headers
        headers = message['payload'].get('headers', [])
        for header in headers:
            name = header['name'].lower()
            if name == 'from':
                email_data['from'] = header['value']
            elif name == 'to':
                email_data['to'] = header['value']
            elif name == 'subject':
                email_data['subject'] = header['value']
            elif name == 'date':
                # Parse date
                date_str = header['value']
                # Remove timezone info for simplicity
                date_str = re.sub(r'\s*\([^)]*\)', '', date_str)
                try:
                    email_data['date'] = datetime.strptime(
                        date_str, '%a, %d %b %Y %H:%M:%S %z'
                    )
                except:
                    try:
                        email_data['date'] = datetime.strptime(
                            date_str, '%a, %d %b %Y %H:%M:%S'
                        )
                    except:
                        email_data['date'] = datetime.now()

        # Extract body
        email_data['body'] = self._get_message_body(message['payload'])

        return email_data

    def _get_message_body(self, payload: Dict) -> str:
        """Extract body from email payload"""
        body = ''

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif 'parts' in part:
                    # Nested parts
                    body += self._get_message_body(part)
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8', errors='ignore')

        return body

    def _classify_email(self, email_data: Dict) -> Dict[str, Any]:
        """
        Classify email as interview, rejection, info request, etc.
        This is where the intelligence happens
        """
        subject = email_data['subject'].lower()
        body = email_data['body'].lower()
        combined_text = subject + ' ' + body

        classification = {
            'type': ResponseType.OTHER,
            'confidence': 0.0,
            'action_required': False,
            'keywords_found': []
        }

        # Interview indicators
        interview_keywords = [
            'interview', 'phone screen', 'video call', 'meet with',
            'schedule', 'availability', 'calendar', 'zoom', 'teams',
            'next steps', 'speak with you', 'conversation', 'discuss'
        ]

        # Rejection indicators
        rejection_keywords = [
            'unfortunately', 'not selected', 'other candidates',
            'not moving forward', 'pursue other', 'decided to go',
            'position has been filled', 'no longer available',
            'thank you for your interest', 'best of luck', 'future opportunities'
        ]

        # Info request indicators
        info_keywords = [
            'additional information', 'please provide', 'could you send',
            'need more details', 'clarification', 'confirm', 'verify'
        ]

        # Offer indicators
        offer_keywords = [
            'offer', 'compensation', 'salary', 'benefits', 'start date',
            'pleased to offer', 'congratulations', 'welcome to'
        ]

        # Score each category
        scores = {}

        # Interview scoring
        interview_score = sum(1 for kw in interview_keywords if kw in combined_text)
        scores['interview'] = interview_score / len(interview_keywords)

        # Rejection scoring
        rejection_score = sum(1 for kw in rejection_keywords if kw in combined_text)
        scores['rejection'] = rejection_score / len(rejection_keywords)

        # Info request scoring
        info_score = sum(1 for kw in info_keywords if kw in combined_text)
        scores['info'] = info_score / len(info_keywords)

        # Offer scoring
        offer_score = sum(1 for kw in offer_keywords if kw in combined_text)
        scores['offer'] = offer_score / len(offer_keywords)

        # Determine classification based on highest score
        if scores['offer'] > 0.2:
            classification['type'] = ResponseType.OFFER
            classification['confidence'] = scores['offer']
            classification['action_required'] = True
        elif scores['interview'] > 0.15:
            classification['type'] = ResponseType.INTERVIEW
            classification['confidence'] = scores['interview']
            classification['action_required'] = True
        elif scores['rejection'] > 0.2:
            classification['type'] = ResponseType.REJECTION
            classification['confidence'] = scores['rejection']
            classification['action_required'] = False
        elif scores['info'] > 0.15:
            classification['type'] = ResponseType.INFO_REQUEST
            classification['confidence'] = scores['info']
            classification['action_required'] = True

        return classification

    async def _match_to_application(self, db: AsyncSession,
                                   email_data: Dict) -> Optional[Application]:
        """
        Match email to an existing application
        This connects emails to specific job applications automatically
        """
        # Extract company name from email
        from_domain = email_data['from'].split('@')[-1].split('.')[0]

        # Common ATS domain mappings
        ats_company_mappings = {
            'workday': None,  # Need to parse company from email
            'greenhouse': None,
            'lever': None,
            'taleo': None,
            'icims': None
        }

        # Try to extract company name from subject or body
        company_name = self._extract_company_name(email_data)

        if not company_name:
            # Try to match by email domain
            result = await db.execute(
                select(Application).join(Job).join(Company).where(
                    and_(
                        Application.status.in_([
                            ApplicationStatus.APPLIED,
                            ApplicationStatus.RESPONDED,
                            ApplicationStatus.INTERVIEWING
                        ]),
                        Company.website.like(f'%{from_domain}%')
                    )
                ).order_by(Application.applied_date.desc())
            )
            return result.scalar_one_or_none()

        # Try to match by company name
        result = await db.execute(
            select(Application).join(Job).join(Company).where(
                and_(
                    Application.status.in_([
                        ApplicationStatus.APPLIED,
                        ApplicationStatus.RESPONDED,
                        ApplicationStatus.INTERVIEWING
                    ]),
                    Company.name.ilike(f'%{company_name}%')
                )
            ).order_by(Application.applied_date.desc())
        )

        return result.scalar_one_or_none()

    def _extract_company_name(self, email_data: Dict) -> Optional[str]:
        """Extract company name from email content"""
        # Look for common patterns in subject and body
        patterns = [
            r'at\s+([A-Z][A-Za-z\s&]+)',  # "position at Company"
            r'with\s+([A-Z][A-Za-z\s&]+)',  # "interview with Company"
            r'from\s+([A-Z][A-Za-z\s&]+)',  # "opportunity from Company"
            r'(?:position|role|opportunity)\s+at\s+([A-Z][A-Za-z\s&]+)',
        ]

        text = email_data['subject'] + ' ' + email_data['body'][:500]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                company = match.group(1).strip()
                # Clean up common suffixes
                company = re.sub(r'\s+(Inc|LLC|Corp|Corporation|Company|Co)\.?$', '', company)
                return company

        return None

    async def _update_application_status(self, db: AsyncSession,
                                        application: Application,
                                        classification: Dict,
                                        email_data: Dict):
        """Update application status based on email classification"""

        # Update response tracking
        application.response_received = True
        application.response_date = email_data['date']
        application.response_type = classification['type']
        application.response_content = email_data['body'][:2000]

        # Update status based on classification
        if classification['type'] == ResponseType.INTERVIEW:
            application.status = ApplicationStatus.INTERVIEWING
            # TODO: Parse interview details from email

        elif classification['type'] == ResponseType.REJECTION:
            application.status = ApplicationStatus.REJECTED

        elif classification['type'] == ResponseType.OFFER:
            application.status = ApplicationStatus.OFFERED

        elif classification['type'] == ResponseType.INFO_REQUEST:
            application.status = ApplicationStatus.RESPONDED

        logger.info(f"Updated application {application.id} status to {application.status.value}")

    async def send_follow_up(self, to_email: str, subject: str,
                            body: str, thread_id: Optional[str] = None) -> bool:
        """Send a follow-up email"""
        if not self.service:
            logger.error("Gmail service not initialized")
            return False

        try:
            message = {
                'raw': base64.urlsafe_b64encode(
                    f"To: {to_email}\n"
                    f"Subject: {subject}\n\n"
                    f"{body}".encode()
                ).decode()
            }

            if thread_id:
                message['threadId'] = thread_id

            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            logger.info(f"Sent follow-up email: {subject}")
            return True

        except HttpError as error:
            logger.error(f"Failed to send email: {error}")
            return False

# Singleton instance
email_service = EmailAutomationService()