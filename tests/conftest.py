"""
Test configuration and fixtures for Job Search Automation Platform
Provides mocked database sessions and prevents async/environment hangs
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# DATABASE MOCKING - Prevent async session hangs
# ============================================================================

@pytest.fixture
def mock_async_db_session():
    """
    Mock async database session for unit tests
    Prevents tests from trying to connect to actual database
    """
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.close = AsyncMock()

    return session


@pytest.fixture
def mock_sync_db_connection():
    """
    Mock synchronous database connection for simple tests
    """
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    conn.commit = MagicMock()
    conn.rollback = MagicMock()
    conn.close = MagicMock()

    return conn


# ============================================================================
# SERVICE MOCKING - Prevent external API calls
# ============================================================================

@pytest.fixture
def mock_gmail_service():
    """
    Mock Gmail API service to prevent actual OAuth/API calls
    """
    with patch('backend.services.email_service.build') as mock_build:
        with patch('backend.services.email_service.Credentials') as mock_creds:
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            yield mock_service


@pytest.fixture
def mock_spacy_nlp():
    """
    Mock spaCy NLP model to speed up tests
    """
    with patch('backend.services.ats_optimizer.spacy.load') as mock_load:
        mock_nlp = MagicMock()
        mock_load.return_value = mock_nlp
        yield mock_nlp


# ============================================================================
# ENVIRONMENT SETUP - Prevent configuration issues
# ============================================================================

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Automatically set up test environment for all tests
    Prevents environment variable conflicts
    """
    # Mock environment variables
    test_env = {
        'DATABASE_URL': 'sqlite+aiosqlite:///test_job_search.db',
        'GMAIL_CREDENTIALS_FILE': 'test_credentials.json',
        'GMAIL_TOKEN_FILE': 'test_token.json',
        'GMAIL_SCOPES': 'https://www.googleapis.com/auth/gmail.readonly',
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

    yield

    # Cleanup happens automatically with monkeypatch


# ============================================================================
# TEST DATA FACTORIES
# ============================================================================

@pytest.fixture
def sample_email_data():
    """
    Factory for creating sample email data for tests
    """
    def _create_email(subject, body, from_addr='test@company.com'):
        return {
            'gmail_id': 'test_msg_123',
            'thread_id': 'test_thread_123',
            'from': from_addr,
            'to': 'matthewdscott7@gmail.com',
            'subject': subject,
            'body': body,
            'date': '2025-10-08T10:00:00'
        }

    return _create_email


@pytest.fixture
def sample_application_data():
    """
    Factory for creating sample application data for tests
    """
    def _create_application(status='APPLIED', days_ago=10,
                          has_response=False, followup_sent=False):
        from datetime import datetime, timedelta

        return {
            'id': 1,
            'status': status,
            'applied_date': datetime.now() - timedelta(days=days_ago),
            'response_received': has_response,
            'followup_sent': followup_sent,
            'follow_ups_sent': 0
        }

    return _create_application


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """
    Configure pytest with custom markers and settings
    """
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (no database access)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires database)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (may take >1 second)"
    )


# ============================================================================
# TEST UTILITIES
# ============================================================================

def assert_email_classified_as(classification, expected_type):
    """
    Helper to assert email classification matches expected type
    """
    assert classification['type'] == expected_type, \
        f"Expected {expected_type}, got {classification['type']}"
    assert classification['confidence'] > 0, \
        "Confidence should be greater than 0"


# Export utilities for use in tests
__all__ = [
    'mock_async_db_session',
    'mock_sync_db_connection',
    'mock_gmail_service',
    'mock_spacy_nlp',
    'sample_email_data',
    'sample_application_data',
    'assert_email_classified_as',
]
