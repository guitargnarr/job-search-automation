"""
LinkedIn Automation Service - Systematic networking and warm lead generation
Uses Playwright for reliable automation that doesn't get detected
"""

import asyncio
import random
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.models import (
    LinkedInOutreach, Application, Job, Company
)

logger = get_logger(__name__)

class LinkedInAutomationService:
    """
    Automates LinkedIn networking to generate warm leads
    Focuses on quality connections over quantity
    """

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context = None
        self.playwright = None
        self.is_logged_in = False

        # Message templates for different scenarios
        self.templates = self._load_message_templates()

        # Rate limiting to avoid detection
        self.daily_connection_count = 0
        self.last_action_time = datetime.now()

    async def initialize(self):
        """Initialize browser with anti-detection measures"""
        try:
            self.playwright = await async_playwright().start()

            # Launch browser with stealth settings
            self.browser = await self.playwright.chromium.launch(
                headless=settings.LINKEDIN_HEADLESS,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-gpu',
                    '--window-size=1920,1080',
                ]
            )

            # Create context with anti-detection
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York'
            )

            # Add anti-detection scripts
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: async () => ({ state: 'granted' })
                    })
                });
            """)

            self.page = await self.context.new_page()

            logger.info("LinkedIn automation browser initialized")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    async def login(self, email: Optional[str] = None, password: Optional[str] = None):
        """Login to LinkedIn with credentials"""
        if self.is_logged_in:
            return True

        email = email or settings.LINKEDIN_EMAIL
        password = password or settings.LINKEDIN_PASSWORD

        if not email or not password:
            logger.error("LinkedIn credentials not provided")
            return False

        try:
            # Navigate to LinkedIn
            await self.page.goto('https://www.linkedin.com/login')
            await self._random_delay(2, 4)

            # Fill login form
            await self.page.fill('input[id="username"]', email)
            await self._random_delay(0.5, 1)

            await self.page.fill('input[id="password"]', password)
            await self._random_delay(0.5, 1)

            # Click login button
            await self.page.click('button[type="submit"]')
            await self._random_delay(3, 5)

            # Check if logged in
            if 'feed' in self.page.url or 'mynetwork' in self.page.url:
                self.is_logged_in = True
                logger.info("Successfully logged into LinkedIn")

                # Save cookies for future sessions
                cookies = await self.context.cookies()
                self._save_cookies(cookies)

                return True
            else:
                logger.error("LinkedIn login failed")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def search_company_employees(self, company_name: str,
                                      target_titles: Optional[List[str]] = None,
                                      max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for employees at target company
        Prioritizes hiring managers and recruiters
        """
        if not self.is_logged_in:
            await self.login()

        employees = []

        try:
            # Build search query
            search_query = f"{company_name}"
            if target_titles:
                search_query += f" {' OR '.join(target_titles)}"

            # Navigate to search
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
            await self.page.goto(search_url)
            await self._random_delay(3, 5)

            # Wait for results
            await self.page.wait_for_selector('.search-results-container', timeout=10000)

            # Extract employee information
            results = await self.page.query_selector_all('.search-result__wrapper')

            for result in results[:max_results]:
                try:
                    # Extract profile data
                    name_elem = await result.query_selector('.entity-result__title-text a')
                    name = await name_elem.inner_text() if name_elem else ""

                    title_elem = await result.query_selector('.entity-result__primary-subtitle')
                    title = await title_elem.inner_text() if title_elem else ""

                    link_elem = await result.query_selector('.entity-result__title-text a')
                    profile_url = await link_elem.get_attribute('href') if link_elem else ""

                    # Check for mutual connections
                    mutual_elem = await result.query_selector('.entity-result__secondary-subtitle')
                    mutual_text = await mutual_elem.inner_text() if mutual_elem else ""
                    mutual_connections = self._extract_mutual_connections(mutual_text)

                    employee = {
                        'name': name.strip(),
                        'title': title.strip(),
                        'profile_url': profile_url.split('?')[0] if profile_url else "",
                        'company': company_name,
                        'mutual_connections': mutual_connections,
                        'relevance_score': self._calculate_relevance_score(
                            title, mutual_connections, target_titles
                        )
                    }

                    employees.append(employee)

                except Exception as e:
                    logger.error(f"Error extracting employee data: {e}")
                    continue

            # Sort by relevance
            employees.sort(key=lambda x: x['relevance_score'], reverse=True)

            logger.info(f"Found {len(employees)} employees at {company_name}")
            return employees

        except Exception as e:
            logger.error(f"Error searching company employees: {e}")
            return []

    async def send_connection_request(self, profile_url: str, message: str,
                                     application_id: Optional[int] = None) -> bool:
        """
        Send personalized connection request
        Includes tracking in database
        """
        if not self.is_logged_in:
            await self.login()

        # Check daily limit
        if self.daily_connection_count >= settings.LINKEDIN_MAX_CONNECTIONS_PER_DAY:
            logger.warning("Daily connection limit reached")
            return False

        try:
            # Navigate to profile
            await self.page.goto(profile_url)
            await self._random_delay(3, 5)

            # Find connect button
            connect_button = await self.page.query_selector(
                'button[aria-label*="Connect"]'
            )

            if not connect_button:
                # Try "More" button first
                more_button = await self.page.query_selector('button[aria-label="More actions"]')
                if more_button:
                    await more_button.click()
                    await self._random_delay(1, 2)

                    connect_option = await self.page.query_selector(
                        'div[role="menu"] span:has-text("Connect")'
                    )
                    if connect_option:
                        await connect_option.click()
                    else:
                        logger.warning(f"Connect option not found for {profile_url}")
                        return False
            else:
                await connect_button.click()

            await self._random_delay(2, 3)

            # Add note if dialog appears
            add_note_button = await self.page.query_selector('button[aria-label="Add a note"]')
            if add_note_button:
                await add_note_button.click()
                await self._random_delay(1, 2)

                # Type message with human-like timing
                message_field = await self.page.query_selector('textarea[name="message"]')
                if message_field:
                    await self._type_like_human(message_field, message)
                    await self._random_delay(1, 2)

            # Send request
            send_button = await self.page.query_selector('button[aria-label="Send now"]')
            if send_button:
                await send_button.click()
                await self._random_delay(2, 3)

                self.daily_connection_count += 1
                logger.info(f"Connection request sent to {profile_url}")
                return True
            else:
                logger.warning("Send button not found")
                return False

        except Exception as e:
            logger.error(f"Error sending connection request: {e}")
            return False

    async def send_message(self, profile_url: str, message: str) -> bool:
        """Send message to connected user"""
        if not self.is_logged_in:
            await self.login()

        try:
            # Navigate to profile
            await self.page.goto(profile_url)
            await self._random_delay(3, 5)

            # Find message button
            message_button = await self.page.query_selector(
                'button[aria-label*="Message"]'
            )

            if not message_button:
                logger.warning(f"Not connected to {profile_url}")
                return False

            await message_button.click()
            await self._random_delay(2, 3)

            # Type message
            message_field = await self.page.query_selector(
                '.msg-form__contenteditable'
            )
            if message_field:
                await self._type_like_human(message_field, message)
                await self._random_delay(1, 2)

                # Send message
                send_button = await self.page.query_selector(
                    'button[type="submit"]'
                )
                if send_button:
                    await send_button.click()
                    await self._random_delay(2, 3)

                    logger.info(f"Message sent to {profile_url}")
                    return True

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def generate_connection_message(self, person: Dict[str, Any],
                                   position: str, company: str) -> str:
        """
        Generate personalized connection request message
        Uses templates but adds personalization
        """
        # Select template based on person's role
        if any(keyword in person['title'].lower() for keyword in
              ['recruiter', 'talent', 'hiring']):
            template_key = 'recruiter'
        elif any(keyword in person['title'].lower() for keyword in
                ['manager', 'director', 'lead', 'head']):
            template_key = 'hiring_manager'
        else:
            template_key = 'peer'

        template = self.templates['connection_request'][template_key]

        # Personalize message
        message = template.format(
            name=person['name'].split()[0],  # First name
            title=person['title'],
            company=company,
            position=position,
            mutual_connections=person.get('mutual_connections', 0)
        )

        # Add personal touch if mutual connections
        if person.get('mutual_connections', 0) > 0:
            message = message.replace(
                "I noticed",
                f"I noticed we have {person['mutual_connections']} mutual connections and"
            )

        # Keep under 300 characters (LinkedIn limit)
        if len(message) > 300:
            message = message[:297] + "..."

        return message

    def generate_follow_up_message(self, person: Dict[str, Any],
                                  position: str, days_since: int) -> str:
        """Generate follow-up message for existing connections"""
        template = self.templates['follow_up']['default']

        message = template.format(
            name=person['name'].split()[0],
            position=position,
            company=person['company'],
            days_since=days_since
        )

        return message

    async def execute_targeted_campaign(self, db: AsyncSession, job_id: int,
                                       max_connections: int = 10) -> Dict[str, Any]:
        """
        Execute complete LinkedIn campaign for specific job
        This is the main automation that generates warm leads
        """
        results = {
            'connections_sent': 0,
            'messages_sent': 0,
            'profiles_found': 0,
            'errors': []
        }

        try:
            # Get job details
            job = await db.get(Job, job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return results

            company = await db.get(Company, job.company_id)

            # Search for relevant employees
            target_titles = [
                'recruiter', 'hiring manager', 'talent acquisition',
                job.title.split()[0],  # First word of job title
                'hr', 'human resources'
            ]

            employees = await self.search_company_employees(
                company.name,
                target_titles,
                max_connections * 2  # Search for more, filter down
            )

            results['profiles_found'] = len(employees)

            # Send connection requests to top matches
            for employee in employees[:max_connections]:
                try:
                    # Generate personalized message
                    message = self.generate_connection_message(
                        employee,
                        job.title,
                        company.name
                    )

                    # Send connection request
                    success = await self.send_connection_request(
                        employee['profile_url'],
                        message,
                        job.id
                    )

                    if success:
                        # Track in database
                        outreach = LinkedInOutreach(
                            application_id=job.id,
                            profile_url=employee['profile_url'],
                            person_name=employee['name'],
                            person_title=employee['title'],
                            person_company=company.name,
                            connection_status='pending',
                            connection_sent_date=datetime.now(),
                            message_sent=message,
                            mutual_connections=employee.get('mutual_connections', 0),
                            relationship_score=employee['relevance_score']
                        )
                        db.add(outreach)
                        results['connections_sent'] += 1

                    # Rate limiting
                    await self._random_delay(30, 60)

                except Exception as e:
                    logger.error(f"Error with connection to {employee['name']}: {e}")
                    results['errors'].append(str(e))
                    continue

            await db.commit()

            logger.info(f"Campaign results: {results}")
            return results

        except Exception as e:
            logger.error(f"Campaign error: {e}")
            results['errors'].append(str(e))
            return results

    def _calculate_relevance_score(self, title: str, mutual_connections: int,
                                  target_titles: Optional[List[str]] = None) -> int:
        """Calculate relevance score for prioritization"""
        score = 0

        # Title relevance
        title_lower = title.lower()
        if 'recruiter' in title_lower or 'talent' in title_lower:
            score += 30
        elif 'hiring' in title_lower:
            score += 25
        elif 'manager' in title_lower or 'director' in title_lower:
            score += 20
        elif 'lead' in title_lower or 'senior' in title_lower:
            score += 15

        # Target title match
        if target_titles:
            for target in target_titles:
                if target.lower() in title_lower:
                    score += 10

        # Mutual connections (very valuable)
        score += mutual_connections * 5

        return min(100, score)

    def _extract_mutual_connections(self, text: str) -> int:
        """Extract number of mutual connections from text"""
        import re
        match = re.search(r'(\d+)\s*mutual', text)
        if match:
            return int(match.group(1))
        return 0

    async def _type_like_human(self, element, text: str):
        """Type text with human-like timing"""
        for char in text:
            await element.type(char)
            await asyncio.sleep(random.uniform(0.05, 0.15))

    async def _random_delay(self, min_seconds: float, max_seconds: float):
        """Add random delay to appear human"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    def _save_cookies(self, cookies: List[Dict]):
        """Save cookies for future sessions"""
        cookie_path = Path.home() / '.linkedin_cookies.json'
        with open(cookie_path, 'w') as f:
            json.dump(cookies, f)

    def _load_cookies(self) -> Optional[List[Dict]]:
        """Load saved cookies"""
        cookie_path = Path.home() / '.linkedin_cookies.json'
        if cookie_path.exists():
            with open(cookie_path, 'r') as f:
                return json.load(f)
        return None

    def _load_message_templates(self) -> Dict[str, Dict[str, str]]:
        """Load message templates"""
        return {
            'connection_request': {
                'recruiter': "Hi {name}, I noticed you're a {title} at {company}. "
                           "I recently applied for the {position} role and would "
                           "love to connect to learn more about the team and culture.",

                'hiring_manager': "Hi {name}, I'm very interested in the {position} role "
                                "at {company}. With my background in the field, I believe "
                                "I could contribute significantly to your team. Would love to connect!",

                'peer': "Hi {name}, I see we're both in similar fields. I'm exploring "
                       "opportunities at {company}, specifically the {position} role. "
                       "Would appreciate connecting to learn about your experience there.",
            },
            'follow_up': {
                'default': "Hi {name}, I wanted to follow up on my application for the "
                         "{position} role at {company}. I'm very enthusiastic about "
                         "the opportunity and would love to discuss how my experience "
                         "aligns with your team's needs.",
            }
        }

    async def cleanup(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# Singleton instance
linkedin_service = LinkedInAutomationService()