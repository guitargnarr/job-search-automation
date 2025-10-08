"""
Comprehensive test suite for Email Automation Service
Tests the Tier 1 critical email classification and parsing functionality
"""

import pytest
import base64
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from backend.services.email_service import EmailAutomationService
from backend.models.models import ResponseType


class TestEmailClassification:
    """Test email classification logic - critical for automation accuracy"""

    def setup_method(self):
        """Set up test fixtures"""
        # Mock the Gmail service to avoid actual API calls
        with patch('backend.services.email_service.build'):
            with patch('backend.services.email_service.Credentials'):
                self.service = EmailAutomationService()

    def test_interview_classification_with_zoom_link(self):
        """
        Test Case 1: Interview Classification
        Verify that emails with interview keywords are correctly classified as INTERVIEW
        """
        # Arrange: Create mock email with clear interview indicators
        email_data = {
            'subject': 'Interview Invitation - Software Engineer Position',
            'body': '''
            Hi Matthew,

            Thank you for applying to our Software Engineer position. We would like to
            schedule an interview with you to discuss the opportunity further.

            Please let us know your availability for a Zoom call next week. We are
            looking forward to speaking with you about this exciting opportunity.

            Best regards,
            Hiring Team
            ''',
            'from': 'hiring@company.com',
            'to': 'matthewdscott7@gmail.com',
            'gmail_id': 'test123',
            'thread_id': 'thread123',
            'date': datetime.now()
        }

        # Act: Classify the email
        classification = self.service._classify_email(email_data)

        # Assert: Should be classified as INTERVIEW with high confidence
        assert classification['type'] == ResponseType.INTERVIEW, \
            "Email with 'interview', 'schedule', 'Zoom' should be classified as INTERVIEW"
        assert classification['confidence'] > 0.15, \
            f"Interview confidence {classification['confidence']} should be > 0.15"
        assert classification['action_required'] is True, \
            "Interview emails should require action"

    def test_rejection_classification_standard_language(self):
        """
        Test Case 2: Rejection Classification
        Verify that emails with rejection keywords are correctly classified as REJECTION
        """
        # Arrange: Create mock email with standard rejection language
        email_data = {
            'subject': 'Thank you for your application',
            'body': '''
            Dear Matthew,

            Thank you for your interest in the Data Analyst position at our company.
            After careful consideration, we have decided to move forward with other
            candidates whose qualifications more closely match our current needs.

            We appreciate the time you took to apply and wish you the best of luck
            in your job search. We will keep your resume on file for future opportunities.

            Best regards,
            HR Team
            ''',
            'from': 'noreply@company.com',
            'to': 'matthewdscott7@gmail.com',
            'gmail_id': 'test456',
            'thread_id': 'thread456',
            'date': datetime.now()
        }

        # Act: Classify the email
        classification = self.service._classify_email(email_data)

        # Assert: Should be classified as REJECTION
        assert classification['type'] == ResponseType.REJECTION, \
            "Email with 'other candidates', 'best of luck' should be classified as REJECTION"
        assert classification['confidence'] > 0.20, \
            f"Rejection confidence {classification['confidence']} should be > 0.20"
        assert classification['action_required'] is False, \
            "Rejection emails should not require action"

    def test_offer_classification_with_salary(self):
        """
        Test Case 3: Offer Classification
        Verify that emails with offer keywords are correctly classified as OFFER
        """
        # Arrange: Create mock email with offer language
        email_data = {
            'subject': 'Job Offer - Senior Data Analyst',
            'body': '''
            Congratulations Matthew!

            We are pleased to offer you the position of Senior Data Analyst at our company.
            Your starting salary will be $95,000 per year, with full benefits including
            health insurance, 401k matching, and 3 weeks paid vacation.

            Your start date is scheduled for November 1st, 2025. Please review the
            attached offer letter and let us know your decision by October 15th.

            Welcome to the team!
            ''',
            'from': 'hr@company.com',
            'to': 'matthewdscott7@gmail.com',
            'gmail_id': 'test789',
            'thread_id': 'thread789',
            'date': datetime.now()
        }

        # Act: Classify the email
        classification = self.service._classify_email(email_data)

        # Assert: Should be classified as OFFER
        assert classification['type'] == ResponseType.OFFER, \
            "Email with 'offer', 'salary', 'congratulations' should be classified as OFFER"
        assert classification['confidence'] > 0.20, \
            f"Offer confidence {classification['confidence']} should be > 0.20"
        assert classification['action_required'] is True, \
            "Offer emails should require action"

    def test_info_request_classification(self):
        """
        Test Case 4: Info Request Classification
        Verify that emails requesting additional information are correctly classified
        """
        # Arrange: Create mock email requesting additional info
        email_data = {
            'subject': 'Additional Information Needed - Application',
            'body': '''
            Hi Matthew,

            Thank you for your application. Before we can proceed, we need some
            additional information from you:

            1. Please provide references from your previous employers
            2. Could you send us your portfolio or work samples?
            3. We need verification of your degree

            Please send these materials at your earliest convenience.

            Thanks,
            HR Department
            ''',
            'from': 'hr@company.com',
            'to': 'matthewdscott7@gmail.com',
            'gmail_id': 'test101',
            'thread_id': 'thread101',
            'date': datetime.now()
        }

        # Act: Classify the email
        classification = self.service._classify_email(email_data)

        # Assert: Should be classified as INFO_REQUEST
        assert classification['type'] == ResponseType.INFO_REQUEST, \
            "Email with 'additional information', 'please provide' should be classified as INFO_REQUEST"
        assert classification['action_required'] is True, \
            "Info request emails should require action"


class TestEmailParsing:
    """Test email parsing and base64 decoding functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch('backend.services.email_service.build'):
            with patch('backend.services.email_service.Credentials'):
                self.service = EmailAutomationService()

    def test_parse_message_with_headers(self):
        """
        Test Case 5: Base64 Decoding and Header Parsing
        Verify correct extraction of headers and email metadata
        """
        # Arrange: Create mock Gmail API message structure
        test_body_text = "This is a test email body with interview scheduling details."
        encoded_body = base64.urlsafe_b64encode(test_body_text.encode()).decode()

        mock_message = {
            'id': 'msg123456',
            'threadId': 'thread123456',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'recruiter@techcorp.com'},
                    {'name': 'To', 'value': 'matthewdscott7@gmail.com'},
                    {'name': 'Subject', 'value': 'Interview Invitation - Data Analyst'},
                    {'name': 'Date', 'value': 'Mon, 07 Oct 2025 14:30:00 -0400'}
                ],
                'body': {
                    'data': encoded_body
                }
            }
        }

        # Act: Parse the message
        email_data = self.service._parse_message(mock_message)

        # Assert: Verify all fields are correctly extracted
        assert email_data['gmail_id'] == 'msg123456', "Gmail ID should be extracted"
        assert email_data['thread_id'] == 'thread123456', "Thread ID should be extracted"
        assert email_data['from'] == 'recruiter@techcorp.com', "From address should be extracted"
        assert email_data['to'] == 'matthewdscott7@gmail.com', "To address should be extracted"
        assert email_data['subject'] == 'Interview Invitation - Data Analyst', "Subject should be extracted"
        assert email_data['body'] == test_body_text, "Body should be decoded from base64"
        assert email_data['date'] is not None, "Date should be parsed"

    def test_parse_message_with_multipart_body(self):
        """
        Test Case 6: Multipart Email Parsing
        Verify correct handling of multipart MIME emails (common in real-world)
        """
        # Arrange: Create mock multipart message
        text_part_1 = "First part of the email."
        text_part_2 = "Second part with interview details."

        encoded_part_1 = base64.urlsafe_b64encode(text_part_1.encode()).decode()
        encoded_part_2 = base64.urlsafe_b64encode(text_part_2.encode()).decode()

        mock_message = {
            'id': 'msg789',
            'threadId': 'thread789',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'hr@company.com'},
                    {'name': 'To', 'value': 'matthewdscott7@gmail.com'},
                    {'name': 'Subject', 'value': 'Application Update'},
                    {'name': 'Date', 'value': 'Tue, 08 Oct 2025 10:00:00 -0400'}
                ],
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {'data': encoded_part_1}
                    },
                    {
                        'mimeType': 'text/plain',
                        'body': {'data': encoded_part_2}
                    }
                ]
            }
        }

        # Act: Parse the multipart message
        email_data = self.service._parse_message(mock_message)

        # Assert: Both parts should be concatenated
        assert text_part_1 in email_data['body'], "First part should be in body"
        assert text_part_2 in email_data['body'], "Second part should be in body"
        assert email_data['from'] == 'hr@company.com', "From should be extracted from multipart"

    def test_get_message_body_simple(self):
        """
        Test Case 7: Simple Body Extraction
        Verify _get_message_body handles simple payloads correctly
        """
        # Arrange: Simple payload with base64 body
        test_text = "Simple email body text for testing."
        encoded = base64.urlsafe_b64encode(test_text.encode()).decode()

        payload = {
            'body': {
                'data': encoded
            }
        }

        # Act: Extract body
        body = self.service._get_message_body(payload)

        # Assert: Should match original text
        assert body == test_text, "Body should be correctly decoded"

    def test_get_message_body_empty(self):
        """
        Test Case 8: Empty Body Handling
        Verify graceful handling of empty email bodies
        """
        # Arrange: Payload with no body data
        payload = {
            'body': {}
        }

        # Act: Extract body
        body = self.service._get_message_body(payload)

        # Assert: Should return empty string, not crash
        assert body == '', "Empty body should return empty string"


class TestCompanyExtraction:
    """Test company name extraction from email content"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch('backend.services.email_service.build'):
            with patch('backend.services.email_service.Credentials'):
                self.service = EmailAutomationService()

    def test_extract_company_name_from_subject(self):
        """
        Test Case 9: Company Name Extraction
        Verify regex patterns correctly extract company names
        """
        # Arrange: Email with company name in subject
        email_data = {
            'subject': 'Interview opportunity at Google Inc',
            'body': 'We would like to interview you for a position.',
            'from': 'recruiter@google.com',
            'to': 'matthewdscott7@gmail.com'
        }

        # Act: Extract company name
        company_name = self.service._extract_company_name(email_data)

        # Assert: Should extract "Google" (without Inc suffix)
        assert company_name is not None, "Should extract company name"
        assert 'Google' in company_name, f"Should extract 'Google' from subject, got: {company_name}"

    def test_extract_company_name_from_body(self):
        """
        Test Case 10: Company Name from Body
        Verify extraction from email body when not in subject
        """
        # Arrange: Email with company in body
        email_data = {
            'subject': 'Application Update',
            'body': 'Thank you for applying to the position at Meta Corporation. We are reviewing your application.',
            'from': 'noreply@meta.com',
            'to': 'matthewdscott7@gmail.com'
        }

        # Act: Extract company name
        company_name = self.service._extract_company_name(email_data)

        # Assert: Should extract "Meta"
        assert company_name is not None, "Should extract company from body"
        assert 'Meta' in company_name, f"Should extract 'Meta' from body, got: {company_name}"


class TestClassificationEdgeCases:
    """Test edge cases and boundary conditions in classification logic"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch('backend.services.email_service.build'):
            with patch('backend.services.email_service.Credentials'):
                self.service = EmailAutomationService()

    def test_classification_case_insensitive(self):
        """
        Test Case 11: Case Insensitivity
        Verify classification works regardless of text case
        """
        # Arrange: Email with UPPERCASE keywords
        email_data = {
            'subject': 'INTERVIEW INVITATION',
            'body': 'WE WOULD LIKE TO SCHEDULE A VIDEO CALL WITH YOU',
            'from': 'HR@COMPANY.COM',
            'to': 'test@test.com',
            'gmail_id': 'test',
            'thread_id': 'thread',
            'date': datetime.now()
        }

        # Act: Classify
        classification = self.service._classify_email(email_data)

        # Assert: Should still detect as interview
        assert classification['type'] == ResponseType.INTERVIEW, \
            "Classification should be case-insensitive"

    def test_classification_with_mixed_signals(self):
        """
        Test Case 12: Mixed Signals
        Verify that emails with multiple signal types use highest score
        """
        # Arrange: Email with both interview and rejection keywords
        email_data = {
            'subject': 'Update on your application',
            'body': '''
            Unfortunately, we are not moving forward with your application at this time.
            However, we would like to schedule a brief call to discuss other opportunities
            that may be a better fit. Please let us know your availability for a quick chat.
            ''',
            'from': 'hr@company.com',
            'to': 'test@test.com',
            'gmail_id': 'test',
            'thread_id': 'thread',
            'date': datetime.now()
        }

        # Act: Classify
        classification = self.service._classify_email(email_data)

        # Assert: Should choose highest confidence classification
        # This email has both rejection and interview signals
        # The system should pick whichever scores higher
        assert classification['type'] in [ResponseType.REJECTION, ResponseType.INTERVIEW], \
            "Should classify as either rejection or interview based on keyword density"
        assert classification['confidence'] > 0.0, "Should have non-zero confidence"


# Pytest fixtures for database mocking (if needed for integration tests)
@pytest.fixture
def mock_db_session():
    """Mock async database session"""
    session = MagicMock()
    session.execute = MagicMock()
    session.commit = MagicMock()
    session.add = MagicMock()
    return session


# Test configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
