"""
Unit tests for Job Validator Service (V2.4)
Tests the direct HTTP verification of job URLs without web search theater
"""

import pytest
from unittest.mock import Mock, patch
from backend.services.job_validator import JobValidator


class TestJobValidator:
    """Test suite for JobValidator service"""

    @pytest.fixture
    def validator(self):
        """Create a JobValidator instance for testing"""
        return JobValidator()

    def test_extract_domain_standard_url(self, validator):
        """Test domain extraction from standard job URL"""
        url = "https://amazon.jobs/en/jobs/123456"
        domain = validator._extract_domain(url)
        assert domain == "amazon.jobs"

    def test_extract_domain_with_www(self, validator):
        """Test domain extraction removes www prefix"""
        url = "https://www.careers.google.com/jobs/results/123"
        domain = validator._extract_domain(url)
        assert domain == "careers.google.com"

    def test_extract_domain_greenhouse(self, validator):
        """Test domain extraction for Greenhouse URLs"""
        url = "https://boards.greenhouse.io/company/jobs/12345"
        domain = validator._extract_domain(url)
        assert domain == "boards.greenhouse.io"

    @patch('requests.get')
    def test_validate_job_url_success_open(self, mock_get, validator):
        """Test validation of an open job posting"""
        # Mock successful response with "Apply" button
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
        <h1>Data Analyst Position</h1>
        <button>Apply Now</button>
        <p>Submit your application today</p>
        </body></html>
        """
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://example.com/jobs/123")

        assert result['exists'] is True
        assert result['status_code'] == 200
        assert result['appears_open'] is True
        assert 'Apply button found' in result['reason'] or 'open' in result['reason'].lower()
        assert result['source'] == "example.com"

    @patch('requests.get')
    def test_validate_job_url_closed_position(self, mock_get, validator):
        """Test validation of a closed/filled position"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
        <h1>Data Analyst Position</h1>
        <p>This position has been filled. Applications are no longer accepting.</p>
        </body></html>
        """
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://example.com/jobs/123")

        assert result['exists'] is True
        assert result['status_code'] == 200
        assert result['appears_open'] is False
        assert 'closed' in result['reason'].lower() or 'filled' in result['reason'].lower()

    @patch('requests.get')
    def test_validate_job_url_404_not_found(self, mock_get, validator):
        """Test validation of non-existent job (404)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "<html><body><h1>404 Not Found</h1></body></html>"
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://example.com/jobs/999999")

        assert result['exists'] is False
        assert result['status_code'] == 404
        assert result['appears_open'] is False
        assert '404' in result['reason'] or 'not found' in result['reason'].lower()

    @patch('requests.get')
    def test_validate_job_url_403_forbidden(self, mock_get, validator):
        """Test validation when site blocks automation (403)"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "<html><body><h1>Access Denied</h1></body></html>"
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://indeed.com/jobs/123")

        assert result['exists'] is False
        assert result['status_code'] == 403
        assert result['appears_open'] is False
        assert '403' in result['reason'] or 'forbidden' in result['reason'].lower() or 'blocked' in result['reason'].lower()

    @patch('requests.get')
    def test_validate_job_url_timeout(self, mock_get, validator):
        """Test validation when request times out"""
        import requests
        mock_get.side_effect = requests.Timeout("Connection timeout")

        result = validator.validate_job_url("https://slow-site.com/jobs/123")

        assert result['exists'] is False
        assert result['status_code'] == 0
        assert result['appears_open'] is False
        assert 'timeout' in result['reason'].lower()

    @patch('requests.get')
    def test_validate_job_url_connection_error(self, mock_get, validator):
        """Test validation when connection fails"""
        import requests
        mock_get.side_effect = requests.ConnectionError("Failed to connect")

        result = validator.validate_job_url("https://down-site.com/jobs/123")

        assert result['exists'] is False
        assert result['status_code'] == 0
        assert result['appears_open'] is False
        assert 'error' in result['reason'].lower() or 'failed' in result['reason'].lower()

    def test_validate_job_url_empty_url(self, validator):
        """Test validation with empty URL"""
        result = validator.validate_job_url("")

        assert result['exists'] is False
        assert result['appears_open'] is False
        assert 'no url' in result['reason'].lower()

    def test_validate_job_url_none_url(self, validator):
        """Test validation with None URL"""
        result = validator.validate_job_url(None)

        assert result['exists'] is False
        assert result['appears_open'] is False

    @patch('requests.get')
    def test_validate_job_url_with_redirect(self, mock_get, validator):
        """Test validation follows redirects correctly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://newdomain.com/careers/123"  # After redirect
        mock_response.text = "<html><body><button>Apply</button></body></html>"
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://olddomain.com/jobs/redirect/123")

        assert result['exists'] is True
        assert result['appears_open'] is True
        mock_get.assert_called_once()
        # Verify allow_redirects=True was passed
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs['allow_redirects'] is True

    @patch('requests.get')
    def test_validate_job_url_case_insensitive_keywords(self, mock_get, validator):
        """Test keyword detection is case-insensitive"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
        <h1>JOB POSTING</h1>
        <button>APPLY NOW</button>
        </body></html>
        """
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://example.com/jobs/123")

        assert result['appears_open'] is True

    @patch('requests.get')
    def test_validate_job_url_easy_apply_detected(self, mock_get, validator):
        """Test detection of LinkedIn Easy Apply"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
        <div class="easy-apply-button">Easy Apply</div>
        </body></html>
        """
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://linkedin.com/jobs/123")

        assert result['appears_open'] is True

    @patch('requests.get')
    def test_validate_job_url_multiple_closed_keywords(self, mock_get, validator):
        """Test job with multiple 'closed' indicators"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
        <p>Applications closed. Position filled. Job archived.</p>
        </body></html>
        """
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://example.com/jobs/123")

        assert result['appears_open'] is False

    @patch('requests.get')
    def test_validate_job_url_has_validation_date(self, mock_get, validator):
        """Test result includes validation timestamp"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Apply</body></html>"
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://example.com/jobs/123")

        assert 'validation_date' in result
        assert result['validation_date'] is not None
        # Check it's a valid ISO format timestamp
        from datetime import datetime
        datetime.fromisoformat(result['validation_date'])  # Should not raise

    @patch('requests.get')
    def test_validate_job_url_user_agent_set(self, mock_get, validator):
        """Test that User-Agent header is set to avoid bot detection"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Apply</body></html>"
        mock_get.return_value = mock_response

        validator.validate_job_url("https://example.com/jobs/123")

        # Verify User-Agent was set in headers
        call_kwargs = mock_get.call_args[1]
        assert 'headers' in call_kwargs
        assert 'User-Agent' in call_kwargs['headers']
        assert 'Mozilla' in call_kwargs['headers']['User-Agent']

    @patch('requests.get')
    def test_validate_job_url_timeout_configured(self, mock_get, validator):
        """Test that request timeout is configured"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Apply</body></html>"
        mock_get.return_value = mock_response

        validator.validate_job_url("https://example.com/jobs/123")

        # Verify timeout was set
        call_kwargs = mock_get.call_args[1]
        assert 'timeout' in call_kwargs
        assert call_kwargs['timeout'] == validator.REQUEST_TIMEOUT


class TestJobValidatorRealWorldScenarios:
    """Test realistic scenarios based on V2.4 findings"""

    @pytest.fixture
    def validator(self):
        return JobValidator()

    @patch('requests.get')
    def test_indeed_aggregator_blocking(self, mock_get, validator):
        """
        Test Indeed blocking automation (58% of tracked jobs)
        Real-world scenario: Indeed returns 403 for automated requests
        """
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "<html><body>Forbidden</body></html>"
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://www.indeed.com/viewjob?jk=abc123")

        assert result['source'] == "indeed.com"
        assert result['exists'] is False
        assert result['status_code'] == 403
        assert result['appears_open'] is False

    @patch('requests.get')
    def test_company_career_page_success(self, mock_get, validator):
        """
        Test direct company career page (65.8% valid rate)
        Real-world scenario: amazon.jobs, careers.waystar.com work well
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><head><title>Data Analyst - Amazon Jobs</title></head>
        <body>
        <h1>Data Analyst</h1>
        <button class="apply-button">Apply Now</button>
        <p>Join our team and submit your application today.</p>
        </body></html>
        """
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://amazon.jobs/en/jobs/2472084")

        assert result['source'] == "amazon.jobs"
        assert result['exists'] is True
        assert result['appears_open'] is True

    @patch('requests.get')
    def test_greenhouse_ats_detection(self, mock_get, validator):
        """
        Test Greenhouse ATS platform detection
        Many companies use Greenhouse for their careers page
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html data-greenhouse="true">
        <body>
        <div id="application_form">
        <button id="apply_button">Submit Application</button>
        </div>
        </body></html>
        """
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://boards.greenhouse.io/company/jobs/123")

        assert result['exists'] is True
        assert result['appears_open'] is True

    @patch('requests.get')
    def test_expired_job_posting(self, mock_get, validator):
        """
        Test job posting that expired (9.2% of tracked jobs)
        Real-world scenario: Job was open but now closed
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
        <h1>Senior Data Analyst</h1>
        <p class="job-status">This job posting has expired and is no longer accepting applications.</p>
        <p>Please check our other open positions.</p>
        </body></html>
        """
        mock_get.return_value = mock_response

        result = validator.validate_job_url("https://example.com/jobs/old123")

        assert result['exists'] is True
        assert result['appears_open'] is False
        assert 'expired' in result['reason'].lower() or 'closed' in result['reason'].lower()
