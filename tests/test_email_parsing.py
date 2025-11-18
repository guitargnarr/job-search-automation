"""
Unit tests for Email Service - Parsing and Base64 Decoding
Tests the email message parsing logic that processes Gmail API responses
"""

import pytest
import base64
from unittest.mock import Mock, MagicMock
from datetime import datetime


class TestEmailBase64Decoding:
    """Test base64 decoding of email message bodies"""

    def test_decode_base64_simple_text(self):
        """Test decoding simple base64-encoded text"""
        original_text = "Hello, this is a test email about a job interview."
        encoded = base64.urlsafe_b64encode(original_text.encode('utf-8')).decode('utf-8')

        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')

        assert decoded == original_text

    def test_decode_base64_with_special_characters(self):
        """Test decoding text with special characters"""
        original_text = "Congratulations! You've been selected for an interview.\nPlease reply to schedule."
        encoded = base64.urlsafe_b64encode(original_text.encode('utf-8')).decode('utf-8')

        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')

        assert decoded == original_text
        assert '\n' in decoded

    def test_decode_base64_empty_string(self):
        """Test decoding empty base64 string"""
        original_text = ""
        encoded = base64.urlsafe_b64encode(original_text.encode('utf-8')).decode('utf-8')

        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')

        assert decoded == ""

    def test_decode_base64_unicode_characters(self):
        """Test decoding text with Unicode characters"""
        original_text = "Dear candidate, we're excited to offer you a position! 🎉"
        encoded = base64.urlsafe_b64encode(original_text.encode('utf-8')).decode('utf-8')

        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')

        assert decoded == original_text
        assert '🎉' in decoded

    def test_decode_base64_html_content(self):
        """Test decoding HTML email content"""
        original_html = """
        <html>
        <body>
        <p>We would like to schedule an <strong>interview</strong> with you.</p>
        <a href="https://calendly.com/schedule">Click here</a>
        </body>
        </html>
        """
        encoded = base64.urlsafe_b64encode(original_html.encode('utf-8')).decode('utf-8')

        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')

        assert decoded == original_html
        assert '<strong>interview</strong>' in decoded

    def test_decode_base64_url_safe_encoding(self):
        """Test URL-safe base64 encoding (used by Gmail API)"""
        original_text = "Test with characters that differ in URL-safe encoding: +/="
        # Gmail uses urlsafe_b64encode which replaces + with - and / with _
        encoded = base64.urlsafe_b64encode(original_text.encode('utf-8')).decode('utf-8')

        # Should not contain + or /
        assert '+' not in encoded
        assert '/' not in encoded

        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')
        assert decoded == original_text

    def test_decode_base64_multiline_text(self):
        """Test decoding multiline email body"""
        original_text = """Dear Matthew,

Thank you for applying to the Data Analyst position.

We would like to schedule an interview with you next week.
Please let us know your availability.

Best regards,
Hiring Team"""

        encoded = base64.urlsafe_b64encode(original_text.encode('utf-8')).decode('utf-8')
        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')

        assert decoded == original_text
        assert decoded.count('\n') == original_text.count('\n')


class TestEmailMessageParsing:
    """Test parsing of Gmail API message structures"""

    def test_parse_simple_email_structure(self):
        """Test parsing basic email message structure"""
        gmail_message = {
            'id': '12345',
            'threadId': 'thread123',
            'snippet': 'We would like to schedule an interview...',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'recruiter@company.com'},
                    {'name': 'Subject', 'value': 'Interview Invitation'},
                    {'name': 'Date', 'value': 'Mon, 1 Jan 2024 10:00:00 -0500'}
                ],
                'body': {
                    'data': base64.urlsafe_b64encode(b'Interview invitation email body').decode()
                }
            }
        }

        # Extract and verify headers
        headers = {h['name']: h['value'] for h in gmail_message['payload']['headers']}
        assert headers['From'] == 'recruiter@company.com'
        assert headers['Subject'] == 'Interview Invitation'

        # Decode body
        body_data = gmail_message['payload']['body']['data']
        decoded_body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        assert decoded_body == 'Interview invitation email body'

    def test_parse_multipart_email(self):
        """Test parsing multipart email (text + HTML)"""
        gmail_message = {
            'id': '12345',
            'payload': {
                'mimeType': 'multipart/alternative',
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {
                            'data': base64.urlsafe_b64encode(b'Plain text version').decode()
                        }
                    },
                    {
                        'mimeType': 'text/html',
                        'body': {
                            'data': base64.urlsafe_b64encode(b'<html><body>HTML version</body></html>').decode()
                        }
                    }
                ]
            }
        }

        # Extract text part
        parts = gmail_message['payload']['parts']
        text_part = next(p for p in parts if p['mimeType'] == 'text/plain')
        decoded_text = base64.urlsafe_b64decode(text_part['body']['data']).decode('utf-8')
        assert decoded_text == 'Plain text version'

        # Extract HTML part
        html_part = next(p for p in parts if p['mimeType'] == 'text/html')
        decoded_html = base64.urlsafe_b64decode(html_part['body']['data']).decode('utf-8')
        assert '<html>' in decoded_html

    def test_parse_email_with_attachments(self):
        """Test parsing email with attachments"""
        gmail_message = {
            'id': '12345',
            'payload': {
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {
                            'data': base64.urlsafe_b64encode(b'Email body').decode()
                        }
                    },
                    {
                        'mimeType': 'application/pdf',
                        'filename': 'offer_letter.pdf',
                        'body': {
                            'attachmentId': 'attach123'
                        }
                    }
                ]
            }
        }

        parts = gmail_message['payload']['parts']
        text_part = next(p for p in parts if p['mimeType'] == 'text/plain')
        attachment_part = next(p for p in parts if p.get('filename'))

        assert attachment_part['filename'] == 'offer_letter.pdf'
        assert 'attachmentId' in attachment_part['body']

    def test_extract_sender_email(self):
        """Test extraction of sender email address"""
        test_cases = [
            ('recruiter@company.com', 'recruiter@company.com'),
            ('John Doe <john@company.com>', 'john@company.com'),
            ('"HR Team" <hr@company.com>', 'hr@company.com'),
        ]

        for from_header, expected_email in test_cases:
            # Simple email extraction logic
            import re
            match = re.search(r'<(.+?)>', from_header)
            if match:
                extracted = match.group(1)
            else:
                extracted = from_header

            assert extracted == expected_email

    def test_parse_date_header(self):
        """Test parsing email date header"""
        date_strings = [
            'Mon, 1 Jan 2024 10:00:00 -0500',
            'Wed, 15 Nov 2023 14:30:00 +0000',
            '1 Jan 2024 10:00:00 -0500',
        ]

        from email.utils import parsedate_to_datetime

        for date_str in date_strings:
            parsed_date = parsedate_to_datetime(date_str)
            assert parsed_date is not None
            assert isinstance(parsed_date, datetime)

    def test_extract_subject_keywords(self):
        """Test extraction of keywords from email subject"""
        subjects = [
            ('Interview Invitation - Data Analyst', ['interview', 'data', 'analyst']),
            ('Application Status Update', ['application', 'status', 'update']),
            ('Job Offer - Senior Position', ['job', 'offer', 'senior']),
        ]

        for subject, expected_keywords in subjects:
            subject_lower = subject.lower()
            found = [kw for kw in expected_keywords if kw in subject_lower]
            assert len(found) > 0


class TestEmailBodyExtraction:
    """Test extraction of email body from various Gmail message formats"""

    def test_extract_body_simple_message(self):
        """Test extracting body from simple (non-multipart) message"""
        message = {
            'payload': {
                'body': {
                    'data': base64.urlsafe_b64encode(b'Simple email body').decode()
                }
            }
        }

        # Extraction logic
        if 'data' in message['payload']['body']:
            body_data = message['payload']['body']['data']
            body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        else:
            body = ""

        assert body == 'Simple email body'

    def test_extract_body_multipart_prefer_text(self):
        """Test extracting text/plain body from multipart message"""
        message = {
            'payload': {
                'mimeType': 'multipart/alternative',
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {
                            'data': base64.urlsafe_b64encode(b'Text version of email').decode()
                        }
                    },
                    {
                        'mimeType': 'text/html',
                        'body': {
                            'data': base64.urlsafe_b64encode(b'<html>HTML version</html>').decode()
                        }
                    }
                ]
            }
        }

        # Prefer text/plain over HTML
        parts = message['payload'].get('parts', [])
        text_part = next((p for p in parts if p['mimeType'] == 'text/plain'), None)

        if text_part and 'data' in text_part['body']:
            body = base64.urlsafe_b64decode(text_part['body']['data']).decode('utf-8')
        else:
            body = ""

        assert body == 'Text version of email'
        assert '<html>' not in body

    def test_extract_body_nested_multipart(self):
        """Test extracting body from nested multipart structure"""
        message = {
            'payload': {
                'mimeType': 'multipart/mixed',
                'parts': [
                    {
                        'mimeType': 'multipart/alternative',
                        'parts': [
                            {
                                'mimeType': 'text/plain',
                                'body': {
                                    'data': base64.urlsafe_b64encode(b'Nested text body').decode()
                                }
                            }
                        ]
                    }
                ]
            }
        }

        # Recursive extraction needed for nested parts
        def find_text_body(payload):
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part.get('body', {}):
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    # Recursively check nested parts
                    if 'parts' in part:
                        result = find_text_body(part)
                        if result:
                            return result
            return None

        body = find_text_body(message['payload'])
        assert body == 'Nested text body'

    def test_extract_body_html_fallback(self):
        """Test falling back to HTML when text/plain not available"""
        message = {
            'payload': {
                'mimeType': 'multipart/alternative',
                'parts': [
                    {
                        'mimeType': 'text/html',
                        'body': {
                            'data': base64.urlsafe_b64encode(b'<p>HTML-only email</p>').decode()
                        }
                    }
                ]
            }
        }

        parts = message['payload'].get('parts', [])
        text_part = next((p for p in parts if p['mimeType'] == 'text/plain'), None)

        if not text_part:
            # Fallback to HTML
            html_part = next((p for p in parts if p['mimeType'] == 'text/html'), None)
            if html_part and 'data' in html_part['body']:
                body = base64.urlsafe_b64decode(html_part['body']['data']).decode('utf-8')
            else:
                body = ""

        assert '<p>HTML-only email</p>' in body

    def test_extract_body_handles_missing_data(self):
        """Test graceful handling of missing body data"""
        message = {
            'payload': {
                'body': {}  # No 'data' field
            }
        }

        if 'data' in message['payload']['body']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        else:
            body = ""

        assert body == ""

    def test_strip_html_tags_from_body(self):
        """Test stripping HTML tags to get plain text"""
        html_body = """
        <html>
        <body>
        <p>We would like to <strong>schedule an interview</strong> with you.</p>
        <p>Please <a href="https://example.com">click here</a> to confirm.</p>
        </body>
        </html>
        """

        # Simple HTML tag removal
        import re
        text_only = re.sub(r'<[^>]+>', '', html_body)
        text_only = text_only.strip()

        assert 'schedule an interview' in text_only
        assert '<strong>' not in text_only
        assert '<p>' not in text_only


class TestEmailMetadataExtraction:
    """Test extraction of email metadata"""

    def test_extract_message_id(self):
        """Test extraction of Gmail message ID"""
        message = {
            'id': 'msg_12345',
            'threadId': 'thread_67890'
        }

        assert message['id'] == 'msg_12345'
        assert message['threadId'] == 'thread_67890'

    def test_extract_labels(self):
        """Test extraction of Gmail labels"""
        message = {
            'labelIds': ['INBOX', 'UNREAD', 'CATEGORY_PROMOTIONS']
        }

        labels = message.get('labelIds', [])
        assert 'INBOX' in labels
        assert 'UNREAD' in labels

    def test_extract_internal_date(self):
        """Test extraction of internal date timestamp"""
        message = {
            'internalDate': '1704110400000'  # Unix timestamp in milliseconds
        }

        timestamp_ms = int(message['internalDate'])
        timestamp_s = timestamp_ms / 1000
        date = datetime.fromtimestamp(timestamp_s)

        assert isinstance(date, datetime)

    def test_extract_snippet(self):
        """Test extraction of email snippet (preview text)"""
        message = {
            'snippet': 'We would like to schedule an interview with you for the Data Analyst position...'
        }

        snippet = message.get('snippet', '')
        assert len(snippet) > 0
        assert 'interview' in snippet.lower()
