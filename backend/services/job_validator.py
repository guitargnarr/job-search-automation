"""
Job Validator Service
Simple, direct validation of job URLs - NO THEATER, REAL RESULTS

This service performs HTTP requests to job URLs to verify:
1. Job posting exists (not 404)
2. Job is still accepting applications (has "Apply" button)
3. Job is not closed ("position filled" indicators)
"""

import requests
from urllib.parse import urlparse
from typing import Dict, Any
from backend.core.logging import get_logger

logger = get_logger(__name__)


class JobValidator:
    """
    V1 Pragmatic validator that checks job URLs directly

    NO WebSearch theater - goes directly to the job URL and checks if it's real.
    Simple HTTP GET + HTML keyword scanning.
    """

    # HTTP request configuration
    REQUEST_TIMEOUT = 10  # seconds
    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    # Validation keywords
    OPEN_KEYWORDS = [
        'apply', 'submit', 'apply now', 'apply online', 'submit application',
        'join us', 'careers', 'start your application', 'easy apply'
    ]

    CLOSED_KEYWORDS = [
        'no longer accepting', 'position filled', 'job closed', 'archived',
        'applications closed', 'hiring complete', 'role filled', 'expired'
    ]

    def validate_job_url(self, job_url: str) -> Dict[str, Any]:
        """
        Perform direct HTTP request to job URL and verify it's real and open

        This is a SYNCHRONOUS function - call with asyncio.to_thread() from async code.

        Args:
            job_url: Direct URL to job posting (e.g., https://amazon.jobs/en/jobs/123456)

        Returns:
            dict with structure:
            {
                'url': str,                 # Original URL
                'source': str,              # Domain (e.g., 'amazon.jobs')
                'exists': bool,             # True if page loaded (200 status)
                'status_code': int,         # HTTP status code
                'appears_open': bool,       # True if job appears to be accepting applications
                'reason': str,              # Human-readable explanation
                'validation_date': str      # When this was checked
            }
        """
        from datetime import datetime

        result = {
            'url': job_url,
            'source': self._extract_domain(job_url),
            'exists': False,
            'status_code': 0,
            'appears_open': False,
            'reason': 'Not yet checked',
            'validation_date': datetime.now().isoformat()
        }

        if not job_url or job_url.strip() == '':
            result['reason'] = "No URL provided"
            return result

        headers = {'User-Agent': self.USER_AGENT}

        try:
            logger.info(f"Validating job URL: {job_url}")

            # HTTP GET request to job URL
            response = requests.get(
                job_url,
                timeout=self.REQUEST_TIMEOUT,
                headers=headers,
                allow_redirects=True  # Follow redirects
            )

            result['status_code'] = response.status_code

            # Check if page exists
            if 200 <= response.status_code < 300:
                result['exists'] = True
                text = response.text.lower()

                # Check for OPEN indicators
                has_apply_button = any(kw in text for kw in self.OPEN_KEYWORDS)

                # Check for CLOSED indicators
                is_closed = any(kw in text for kw in self.CLOSED_KEYWORDS)

                if is_closed:
                    result['appears_open'] = False
                    result['reason'] = "Job is CLOSED (found closing keywords)"
                    logger.warning(f"Job CLOSED: {job_url}")
                elif has_apply_button:
                    result['appears_open'] = True
                    result['reason'] = "Job appears OPEN (Apply button found)"
                    logger.info(f"Job OPEN: {job_url}")
                else:
                    result['appears_open'] = False
                    result['reason'] = "Uncertain - no clear Apply button or Close indicator"
                    logger.warning(f"Job uncertain: {job_url}")

            elif response.status_code == 404:
                result['reason'] = "Job NOT FOUND (404) - likely fake or expired"
                logger.warning(f"Job 404: {job_url}")
            elif response.status_code == 403:
                result['reason'] = "Access forbidden (403) - may need authentication or be bot-protected"
                logger.warning(f"Job 403: {job_url}")
            elif response.status_code >= 500:
                result['reason'] = f"Server error ({response.status_code}) - try again later"
                logger.warning(f"Job server error: {job_url}")
            else:
                result['reason'] = f"HTTP {response.status_code} - unexpected status"
                logger.warning(f"Job unexpected status {response.status_code}: {job_url}")

            return result

        except requests.exceptions.Timeout:
            result['reason'] = "Request timed out (>10s) - site may be down"
            logger.error(f"Job validation timeout: {job_url}")
            return result

        except requests.exceptions.ConnectionError:
            result['reason'] = "Connection failed - URL may be invalid or site is down"
            logger.error(f"Job validation connection error: {job_url}")
            return result

        except requests.exceptions.RequestException as e:
            result['reason'] = f"Request error: {type(e).__name__}"
            logger.error(f"Job validation request error for {job_url}: {e}")
            return result

        except Exception as e:
            result['reason'] = f"Unexpected error: {str(e)}"
            logger.error(f"Job validation unexpected error for {job_url}: {e}")
            return result

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for source tracking"""
        try:
            return urlparse(url).netloc
        except Exception:
            return "unknown"


# Singleton instance
job_validator = JobValidator()
