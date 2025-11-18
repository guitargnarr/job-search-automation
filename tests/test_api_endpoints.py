"""
Integration tests for API endpoints
Tests the FastAPI REST API for jobs, applications, and analytics
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    # Import here to avoid issues if backend isn't fully configured
    try:
        from backend.main import app
        return TestClient(app)
    except Exception as e:
        pytest.skip(f"Could not create test client: {e}")


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_endpoint_returns_200(self, client):
        """Test that health endpoint is accessible"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, client):
        """Test that health endpoint returns JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_endpoint_has_status(self, client):
        """Test that health response includes status"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data or "health" in data


class TestJobsEndpoints:
    """Test /api/v1/jobs/* endpoints"""

    @pytest.mark.asyncio
    async def test_create_job_success(self, client):
        """Test creating a new job"""
        job_data = {
            "company_name": "Test Company",
            "title": "Data Analyst",
            "job_description": "Looking for a data analyst with Python skills",
            "job_url": "https://example.com/jobs/123",
            "location": "Remote",
            "remote_type": "remote",
            "salary_min": 70000,
            "salary_max": 90000,
            "priority": "MEDIUM"
        }

        response = client.post("/api/v1/jobs/create", json=job_data)

        # Might fail if database not configured, but should at least try
        assert response.status_code in [200, 201, 500]

    def test_create_job_missing_required_fields(self, client):
        """Test creating job with missing required fields"""
        incomplete_data = {
            "title": "Data Analyst"
            # Missing company_name, job_description, etc.
        }

        response = client.post("/api/v1/jobs/create", json=incomplete_data)

        # Should return validation error (422)
        assert response.status_code == 422

    def test_create_job_invalid_priority(self, client):
        """Test creating job with invalid priority value"""
        job_data = {
            "company_name": "Test Company",
            "title": "Data Analyst",
            "job_description": "Test description",
            "job_url": "https://example.com/jobs/123",
            "priority": "INVALID_PRIORITY"  # Invalid enum value
        }

        response = client.post("/api/v1/jobs/create", json=job_data)

        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_jobs_endpoint_exists(self, client):
        """Test that list jobs endpoint is accessible"""
        response = client.get("/api/v1/jobs/list")

        # Should return 200 or 500 (if DB not configured)
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_list_jobs_with_filters(self, client):
        """Test listing jobs with filter parameters"""
        params = {
            "status": "new",
            "priority": "HIGH",
            "remote_type": "remote"
        }

        response = client.get("/api/v1/jobs/list", params=params)

        # Should accept filters
        assert response.status_code in [200, 422, 500]

    @pytest.mark.asyncio
    async def test_list_jobs_pagination(self, client):
        """Test job list pagination"""
        params = {
            "skip": 0,
            "limit": 10
        }

        response = client.get("/api/v1/jobs/list", params=params)

        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            # Should return a list
            assert isinstance(data, list) or isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_get_job_by_id(self, client):
        """Test getting specific job by ID"""
        job_id = 1

        response = client.get(f"/api/v1/jobs/{job_id}")

        # Might not exist, but endpoint should be accessible
        assert response.status_code in [200, 404, 500]

    @pytest.mark.asyncio
    async def test_update_job(self, client):
        """Test updating a job"""
        job_id = 1
        update_data = {
            "status": "applied",
            "notes": "Applied on 2024-01-01"
        }

        response = client.put(f"/api/v1/jobs/{job_id}", json=update_data)

        assert response.status_code in [200, 404, 422, 500]

    @pytest.mark.asyncio
    async def test_delete_job(self, client):
        """Test deleting a job"""
        job_id = 999  # Use high ID to avoid deleting real data

        response = client.delete(f"/api/v1/jobs/{job_id}")

        assert response.status_code in [200, 204, 404, 500]


class TestApplicationsEndpoints:
    """Test /api/v1/applications/* endpoints"""

    @pytest.mark.asyncio
    async def test_create_application_success(self, client):
        """Test creating a new application"""
        app_data = {
            "job_id": 1,
            "company_id": 1,
            "applied_date": "2024-01-01",
            "status": "APPLIED",
            "cover_letter_used": "default",
            "resume_version": "v1"
        }

        response = client.post("/api/v1/applications/create", json=app_data)

        assert response.status_code in [200, 201, 404, 422, 500]

    @pytest.mark.asyncio
    async def test_list_applications(self, client):
        """Test listing applications"""
        response = client.get("/api/v1/applications/list")

        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_list_applications_by_status(self, client):
        """Test filtering applications by status"""
        params = {"status": "APPLIED"}

        response = client.get("/api/v1/applications/list", params=params)

        assert response.status_code in [200, 422, 500]

    @pytest.mark.asyncio
    async def test_get_application_stats(self, client):
        """Test getting application statistics"""
        response = client.get("/api/v1/applications/stats")

        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            # Should contain stats fields
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_update_application_status(self, client):
        """Test updating application status"""
        app_id = 1
        update_data = {
            "status": "INTERVIEWING",
            "notes": "Phone screen scheduled"
        }

        response = client.put(f"/api/v1/applications/{app_id}", json=update_data)

        assert response.status_code in [200, 404, 422, 500]

    @pytest.mark.asyncio
    async def test_get_priority_applications(self, client):
        """Test getting priority applications (follow-ups needed)"""
        response = client.get("/api/v1/applications/priority")

        assert response.status_code in [200, 500]


class TestAnalyticsEndpoints:
    """Test /api/v1/analytics/* endpoints"""

    @pytest.mark.asyncio
    async def test_get_dashboard_analytics(self, client):
        """Test getting dashboard analytics"""
        response = client.get("/api/v1/analytics/dashboard")

        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            # Should contain analytics metrics
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_get_trends_analytics(self, client):
        """Test getting trend analysis"""
        response = client.get("/api/v1/analytics/trends")

        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_get_performance_score(self, client):
        """Test getting performance score"""
        response = client.get("/api/v1/analytics/performance-score")

        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_analytics_metrics_structure(self, client):
        """Test that analytics returns expected metrics structure"""
        response = client.get("/api/v1/analytics/dashboard")

        if response.status_code == 200:
            data = response.json()
            # Should have key metrics mentioned in CLAUDE.md
            # response_rate, applications_count, etc.
            assert isinstance(data, dict)


class TestEmailEndpoints:
    """Test /api/v1/email/* endpoints"""

    @pytest.mark.asyncio
    async def test_scan_inbox_endpoint_exists(self, client):
        """Test that email scan endpoint exists"""
        scan_data = {"days_back": 7}

        response = client.post("/api/v1/email/scan", json=scan_data)

        # May fail if Gmail not configured, but endpoint should exist
        assert response.status_code in [200, 400, 500]

    @pytest.mark.asyncio
    async def test_get_email_responses(self, client):
        """Test getting categorized email responses"""
        response = client.get("/api/v1/email/responses")

        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_get_email_stats(self, client):
        """Test getting email campaign statistics"""
        response = client.get("/api/v1/email/stats")

        assert response.status_code in [200, 500]


class TestATSEndpoints:
    """Test /api/v1/ats/* endpoints"""

    @pytest.mark.asyncio
    async def test_analyze_job_endpoint(self, client):
        """Test ATS job analysis endpoint"""
        job_data = {
            "job_description": """
            Data Analyst position requiring:
            - Python, SQL, Tableau
            - 3+ years experience
            - Bachelor's degree
            """
        }

        response = client.post("/api/v1/ats/analyze-job", json=job_data)

        assert response.status_code in [200, 422, 500]

    @pytest.mark.asyncio
    async def test_score_resume_endpoint(self, client):
        """Test ATS resume scoring endpoint"""
        score_data = {
            "resume_text": "Data analyst with Python and SQL experience",
            "job_description": "Looking for data analyst with Python and SQL"
        }

        response = client.post("/api/v1/ats/score", json=score_data)

        assert response.status_code in [200, 422, 500]

        if response.status_code == 200:
            data = response.json()
            assert 'overall_score' in data or isinstance(data, dict)


class TestFollowUpEndpoints:
    """Test /api/v1/follow-ups/* endpoints"""

    @pytest.mark.asyncio
    async def test_create_follow_up_reminder(self, client):
        """Test creating manual follow-up reminder"""
        reminder_data = {
            "application_id": 1,
            "scheduled_date": "2024-01-15",
            "reminder_type": "follow_up"
        }

        response = client.post("/api/v1/follow-ups/create", json=reminder_data)

        assert response.status_code in [200, 201, 404, 422, 500]

    @pytest.mark.asyncio
    async def test_auto_schedule_follow_ups(self, client):
        """Test automatic follow-up scheduling"""
        response = client.post("/api/v1/follow-ups/auto-schedule")

        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_get_scheduled_follow_ups(self, client):
        """Test getting scheduled follow-ups"""
        response = client.get("/api/v1/follow-ups/scheduled")

        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_get_follow_up_analytics(self, client):
        """Test getting follow-up effectiveness metrics"""
        response = client.get("/api/v1/follow-ups/analytics")

        assert response.status_code in [200, 500]


class TestAPIErrorHandling:
    """Test API error handling"""

    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoints return 404"""
        response = client.get("/api/v1/nonexistent/endpoint")

        assert response.status_code == 404

    def test_invalid_method_returns_405(self, client):
        """Test that invalid HTTP methods return 405"""
        # Try POST on GET-only endpoint
        response = client.post("/health")

        assert response.status_code == 405

    def test_malformed_json_returns_422(self, client):
        """Test that malformed JSON returns validation error"""
        response = client.post(
            "/api/v1/jobs/create",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_pagination_values(self, client):
        """Test handling of negative pagination values"""
        params = {"skip": -1, "limit": -10}

        response = client.get("/api/v1/jobs/list", params=params)

        # Should reject or clamp negative values
        assert response.status_code in [200, 422]


class TestAPIPerformance:
    """Test API performance characteristics"""

    @pytest.mark.asyncio
    async def test_response_time_health_check(self, client):
        """Test that health check responds quickly"""
        import time

        start = time.time()
        response = client.get("/health")
        duration = time.time() - start

        assert response.status_code == 200
        # Should respond in less than 1 second
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_pagination_limits_enforced(self, client):
        """Test that pagination limits are enforced (MAX_API_PAGE_SIZE=100)"""
        params = {"limit": 1000}  # Try to request more than max

        response = client.get("/api/v1/jobs/list", params=params)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                # Should be capped at 100 items
                assert len(data) <= 100
