# System Architecture
## Technical Design for Job Search Automation Platform

### Overview

This document outlines the technical architecture required to transform the current file-copying system into a genuine automation platform. The design prioritizes modularity, scalability, and maintainability while keeping complexity manageable.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  Web Dashboard │ CLI Tools │ API Endpoints │ Mobile (Future)    │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway Layer                         │
├─────────────────────────────────────────────────────────────────┤
│              FastAPI │ Auth │ Rate Limiting │ Routing            │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                         │
├─────────────────────────────────────────────────────────────────┤
│ Email     │ ATS        │ LinkedIn   │ Job        │ Analytics   │
│ Monitor   │ Optimizer  │ Automation │ Aggregator │ Engine      │
│           │            │            │            │              │
│ Follow-up │ Company    │ Interview  │ Salary     │ AI Content  │
│ System    │ Research   │ Prep       │ Intel      │ Generator   │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      Data Access Layer                            │
├─────────────────────────────────────────────────────────────────┤
│   PostgreSQL │ Redis Cache │ File Storage │ Vector DB (Future)  │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                    External Services Layer                        │
├─────────────────────────────────────────────────────────────────┤
│ Gmail API │ LinkedIn │ Indeed API │ OpenAI │ Calendar │ News API │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. API Gateway (FastAPI)

```python
# main.py - Core API structure
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

app = FastAPI(
    title="Job Search Automation API",
    version="2.0.0",
    description="Intelligent job search automation platform"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routers
from routers import (
    applications, email, linkedin,
    jobs, analytics, ai_content
)

app.include_router(applications.router, prefix="/api/v1/applications")
app.include_router(email.router, prefix="/api/v1/email")
app.include_router(linkedin.router, prefix="/api/v1/linkedin")
app.include_router(jobs.router, prefix="/api/v1/jobs")
app.include_router(analytics.router, prefix="/api/v1/analytics")
app.include_router(ai_content.router, prefix="/api/v1/ai")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
```

### 2. Database Schema (PostgreSQL)

```sql
-- Enhanced database schema for real automation
CREATE DATABASE job_search_automation;

-- Companies table with enhanced fields
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    industry VARCHAR(100),
    size_range VARCHAR(50),
    glassdoor_rating DECIMAL(3,2),
    recent_news JSONB,
    tech_stack JSONB,
    culture_notes TEXT,
    last_researched TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table with intelligent tracking
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    title VARCHAR(255) NOT NULL,
    job_url VARCHAR(500),
    source VARCHAR(50), -- linkedin, indeed, company_site
    job_description TEXT,
    requirements JSONB,
    posted_date DATE,
    salary_range VARCHAR(100),
    remote_type VARCHAR(50),
    ats_score INTEGER,
    fit_score INTEGER,
    keywords JSONB,
    application_deadline DATE,
    status VARCHAR(50) DEFAULT 'new',
    priority VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applications with comprehensive tracking
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    applied_date TIMESTAMP,
    application_method VARCHAR(100),
    resume_version VARCHAR(100),
    cover_letter_version VARCHAR(100),
    ats_score INTEGER,
    keywords_matched JSONB,
    status VARCHAR(50) DEFAULT 'draft',
    response_received BOOLEAN DEFAULT FALSE,
    response_date TIMESTAMP,
    response_type VARCHAR(50), -- interview, rejection, info_request
    interview_scheduled TIMESTAMP,
    referral_used BOOLEAN DEFAULT FALSE,
    referral_person VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email tracking for automation
CREATE TABLE email_tracking (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    email_id VARCHAR(255) UNIQUE,
    from_address VARCHAR(255),
    subject VARCHAR(500),
    received_date TIMESTAMP,
    body_preview TEXT,
    classification VARCHAR(50), -- interview, rejection, info
    processed BOOLEAN DEFAULT FALSE,
    action_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LinkedIn automation tracking
CREATE TABLE linkedin_outreach (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    profile_url VARCHAR(500),
    person_name VARCHAR(255),
    person_title VARCHAR(255),
    connection_status VARCHAR(50), -- pending, connected, messaged
    message_sent TEXT,
    response_received BOOLEAN DEFAULT FALSE,
    response_text TEXT,
    outreach_date TIMESTAMP,
    follow_up_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Template performance tracking
CREATE TABLE template_performance (
    id SERIAL PRIMARY KEY,
    template_type VARCHAR(50), -- resume, cover_letter
    template_version VARCHAR(100),
    times_used INTEGER DEFAULT 0,
    responses_received INTEGER DEFAULT 0,
    interviews_received INTEGER DEFAULT 0,
    response_rate DECIMAL(5,2),
    avg_time_to_response INTERVAL,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics events for tracking everything
CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100),
    event_data JSONB,
    user_id INTEGER,
    session_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_priority ON jobs(priority);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_date ON applications(applied_date);
CREATE INDEX idx_email_tracking_processed ON email_tracking(processed);
CREATE INDEX idx_linkedin_outreach_status ON linkedin_outreach(connection_status);
```

### 3. Task Queue Architecture (Celery + Redis)

```python
# celery_app.py - Async task processing
from celery import Celery
from celery.schedules import crontab
import redis

# Celery configuration
celery_app = Celery(
    'job_search_automation',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
    include=['tasks.email', 'tasks.linkedin', 'tasks.jobs', 'tasks.analytics']
)

# Task routing
celery_app.conf.task_routes = {
    'tasks.email.*': {'queue': 'email'},
    'tasks.linkedin.*': {'queue': 'linkedin'},
    'tasks.jobs.*': {'queue': 'jobs'},
    'tasks.analytics.*': {'queue': 'analytics'},
}

# Scheduled tasks
celery_app.conf.beat_schedule = {
    'check-emails': {
        'task': 'tasks.email.scan_inbox',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'aggregate-jobs': {
        'task': 'tasks.jobs.aggregate_new_jobs',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
    'send-follow-ups': {
        'task': 'tasks.follow_up.send_scheduled',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'update-analytics': {
        'task': 'tasks.analytics.calculate_metrics',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'linkedin-connection-campaign': {
        'task': 'tasks.linkedin.run_connection_campaign',
        'schedule': crontab(hour='*/4'),  # Every 4 hours
    },
}
```

### 4. Service Layer Architecture

```python
# services/email_service.py - Email automation service
import asyncio
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import re

class EmailAutomationService:
    def __init__(self):
        self.gmail_service = self._initialize_gmail()
        self.classifier = ResponseClassifier()

    async def scan_inbox_for_responses(self) -> List[Dict[str, Any]]:
        """Scan inbox for job application responses"""
        query = 'is:unread (from:workday.com OR from:greenhouse.io OR from:lever.co OR subject:"application" OR subject:"interview")'

        messages = await self._fetch_messages(query)
        classified_messages = []

        for message in messages:
            classification = self.classifier.classify(message)

            # Update database
            await self._update_application_status(
                message['company'],
                classification['type'],
                message['content']
            )

            # Trigger appropriate workflows
            if classification['type'] == 'interview':
                await self._schedule_interview_prep(message)
            elif classification['type'] == 'rejection':
                await self._trigger_rejection_analysis(message)

            classified_messages.append({
                'message': message,
                'classification': classification
            })

        return classified_messages

    async def _fetch_messages(self, query: str) -> List[Dict]:
        """Fetch messages matching query"""
        results = self.gmail_service.users().messages().list(
            userId='me',
            q=query,
            maxResults=50
        ).execute()

        messages = results.get('messages', [])
        full_messages = []

        for msg in messages:
            full_msg = self.gmail_service.users().messages().get(
                userId='me',
                id=msg['id']
            ).execute()
            full_messages.append(self._parse_message(full_msg))

        return full_messages
```

```python
# services/ats_optimizer.py - ATS optimization service
from typing import Dict, List, Tuple
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import docx

class ATSOptimizer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.vectorizer = TfidfVectorizer()

    def analyze_resume_fit(
        self,
        resume_path: str,
        job_description: str
    ) -> Dict[str, Any]:
        """Analyze resume fit for ATS and job description"""

        # Extract text from resume
        resume_text = self._extract_resume_text(resume_path)

        # Extract keywords and requirements
        job_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(resume_text)

        # Calculate scores
        keyword_coverage = self._calculate_coverage(job_keywords, resume_keywords)
        density_score = self._calculate_density(resume_text, job_keywords)
        format_score = self._check_ats_format(resume_path)

        # Generate recommendations
        missing_keywords = set(job_keywords) - set(resume_keywords)
        recommendations = self._generate_recommendations(
            missing_keywords,
            density_score,
            format_score
        )

        return {
            'ats_score': int((keyword_coverage + density_score + format_score) / 3),
            'keyword_coverage': keyword_coverage,
            'density_score': density_score,
            'format_score': format_score,
            'missing_keywords': list(missing_keywords),
            'recommendations': recommendations,
            'optimized_resume': self._generate_optimized_version(
                resume_path,
                missing_keywords
            )
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords using NLP"""
        doc = self.nlp(text)

        # Extract noun phrases and important entities
        keywords = []

        # Get noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Limit to 3-word phrases
                keywords.append(chunk.text.lower())

        # Get named entities (skills, technologies, etc.)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'SKILL']:
                keywords.append(ent.text.lower())

        # Get important single tokens
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN'] and
                not token.is_stop and
                len(token.text) > 2):
                keywords.append(token.text.lower())

        return list(set(keywords))
```

### 5. External Service Integrations

```python
# integrations/linkedin_automation.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random

class LinkedInAutomation:
    def __init__(self):
        self.driver = self._initialize_driver()
        self.message_templates = MessageTemplates()

    def _initialize_driver(self):
        """Initialize undetected Chrome driver"""
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')

        # Add residential proxy if available
        if PROXY_CONFIG:
            options.add_argument(f'--proxy-server={PROXY_CONFIG}')

        driver = uc.Chrome(options=options)
        return driver

    async def execute_connection_campaign(
        self,
        company: str,
        position: str,
        max_connections: int = 10
    ):
        """Execute targeted connection campaign"""

        # Search for employees at target company
        employees = await self._search_company_employees(company)

        # Prioritize connections
        prioritized = self._prioritize_targets(employees, {
            'hiring_manager': 3.0,
            'same_department': 2.5,
            'recruiter': 2.0,
            'mutual_connections': 1.5,
            'same_school': 1.2
        })

        # Send connection requests
        sent_count = 0
        for employee in prioritized[:max_connections]:
            try:
                # Generate personalized message
                message = self.message_templates.generate_connection_request(
                    employee, company, position
                )

                # Send connection request
                await self._send_connection_request(employee['profile_url'], message)

                # Log in database
                await self._log_outreach(employee, message)

                # Human-like delay
                delay = random.uniform(30, 90)
                await asyncio.sleep(delay)

                sent_count += 1

            except Exception as e:
                logger.error(f"Failed to connect with {employee['name']}: {e}")

        return {'sent': sent_count, 'targets': prioritized[:sent_count]}

    def _search_company_employees(self, company: str) -> List[Dict]:
        """Search for employees at target company"""
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={company}"
        self.driver.get(search_url)

        # Wait for results to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-result"))
        )

        # Extract employee information
        employees = []
        results = self.driver.find_elements(By.CLASS_NAME, "search-result")

        for result in results:
            try:
                employee = {
                    'name': result.find_element(By.CLASS_NAME, "name").text,
                    'title': result.find_element(By.CLASS_NAME, "title").text,
                    'profile_url': result.find_element(By.TAG_NAME, "a").get_attribute("href"),
                    'mutual_connections': self._get_mutual_connections(result)
                }
                employees.append(employee)
            except:
                continue

        return employees
```

### 6. AI Integration Layer

```python
# integrations/ai_content_generator.py
import openai
from typing import Dict, Optional
import json

class AIContentGenerator:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.system_prompt = self._load_system_prompt()

    async def generate_cover_letter(
        self,
        job_description: str,
        company_info: Dict,
        user_experience: str
    ) -> str:
        """Generate personalized cover letter using GPT-4"""

        prompt = f"""
        Generate a compelling cover letter for the following position:

        Job Description:
        {job_description}

        Company Information:
        - Name: {company_info['name']}
        - Recent News: {company_info['recent_news']}
        - Culture: {company_info['culture']}
        - Tech Stack: {company_info.get('tech_stack', 'N/A')}

        Candidate Experience:
        {user_experience}

        Requirements:
        1. Reference specific company initiatives or recent news
        2. Map candidate experience directly to job requirements
        3. Demonstrate cultural fit
        4. Include specific technologies/skills from the job description
        5. Keep it concise (300-400 words)
        6. Use a professional but personable tone
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        cover_letter = response.choices[0].message.content

        # Add to review queue for human approval
        await self._add_to_review_queue(cover_letter, job_description)

        return cover_letter

    async def generate_follow_up_email(
        self,
        application_details: Dict,
        days_since: int,
        company_news: Optional[str] = None
    ) -> str:
        """Generate personalized follow-up email"""

        prompt = f"""
        Generate a follow-up email for a job application:

        Position: {application_details['position']}
        Company: {application_details['company']}
        Applied: {days_since} days ago
        Previous Contact: {application_details.get('last_contact', 'Initial application')}

        {f'Recent Company News: {company_news}' if company_news else ''}

        Requirements:
        1. Professional and concise
        2. Reference the specific position
        3. {f'Mention the recent news: {company_news}' if company_news else 'Express continued interest'}
        4. Request status update politely
        5. Provide value (insight, article, etc.) if possible
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=200
        )

        return response.choices[0].message.content
```

### 7. Caching Layer (Redis)

```python
# cache/redis_cache.py
import redis
import json
from typing import Any, Optional
import hashlib

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=2,
            decode_responses=True
        )

    def cache_key(self, prefix: str, params: Dict) -> str:
        """Generate cache key from parameters"""
        param_string = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()
        return f"{prefix}:{param_hash}"

    async def get_or_set(
        self,
        key: str,
        fetch_function,
        ttl: int = 3600
    ) -> Any:
        """Get from cache or fetch and set"""

        # Try to get from cache
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)

        # Fetch fresh data
        data = await fetch_function()

        # Cache it
        self.redis_client.setex(
            key,
            ttl,
            json.dumps(data)
        )

        return data

    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        for key in self.redis_client.scan_iter(match=pattern):
            self.redis_client.delete(key)
```

---

## Security Architecture

### Authentication & Authorization

```python
# security/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Security configuration
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return username
```

### API Security

```python
# security/api_security.py
from fastapi import Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )

        # Log request
        self.requests[client_ip].append(now)

        response = await call_next(request)
        return response
```

---

## Deployment Architecture

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run migrations
RUN alembic upgrade head

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/jobsearch
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./:/app

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=jobsearch
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery_worker:
    build: .
    command: celery -A celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/jobsearch
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  celery_beat:
    build: .
    command: celery -A celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/jobsearch
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
```

---

## Monitoring & Observability

### Logging Architecture

```python
# monitoring/logger.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging"""

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler('logs/application.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()
```

### Metrics Collection

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
job_applications_total = Counter(
    'job_applications_total',
    'Total number of job applications',
    ['status', 'source']
)

response_time_seconds = Histogram(
    'response_time_seconds',
    'Response time in seconds',
    ['endpoint']
)

active_campaigns = Gauge(
    'active_campaigns',
    'Number of active LinkedIn campaigns'
)

ats_score_distribution = Histogram(
    'ats_score_distribution',
    'Distribution of ATS scores',
    buckets=[0, 20, 40, 60, 80, 100]
)
```

---

## Performance Optimization

### Database Optimization

```sql
-- Performance indexes
CREATE INDEX idx_applications_date_range
ON applications(applied_date)
WHERE status != 'draft';

CREATE INDEX idx_jobs_fit_score
ON jobs(fit_score DESC)
WHERE status = 'active';

CREATE INDEX idx_email_unprocessed
ON email_tracking(received_date)
WHERE processed = false;

-- Materialized view for analytics
CREATE MATERIALIZED VIEW application_analytics AS
SELECT
    DATE_TRUNC('week', applied_date) as week,
    COUNT(*) as total_applications,
    COUNT(CASE WHEN response_received THEN 1 END) as responses,
    COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews,
    AVG(EXTRACT(days FROM (response_date - applied_date))) as avg_response_time
FROM applications
WHERE applied_date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY week
WITH DATA;

-- Refresh weekly
CREATE OR REPLACE FUNCTION refresh_analytics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW application_analytics;
END;
$$ LANGUAGE plpgsql;
```

### Caching Strategy

```python
# Cache configuration by data type
CACHE_CONFIG = {
    'company_research': {
        'ttl': 7 * 24 * 3600,  # 1 week
        'invalidate_on': ['company_update']
    },
    'job_listings': {
        'ttl': 6 * 3600,  # 6 hours
        'invalidate_on': ['new_job_added']
    },
    'template_performance': {
        'ttl': 24 * 3600,  # 1 day
        'invalidate_on': ['new_response']
    },
    'user_analytics': {
        'ttl': 3600,  # 1 hour
        'invalidate_on': ['application_submitted']
    }
}
```

---

## Testing Architecture

### Test Structure

```python
# tests/test_structure.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
SQLALCHEMY_DATABASE_URL = "postgresql://test:test@localhost/test_jobsearch"

@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)

@pytest.fixture
def mock_gmail_service(mocker):
    """Mock Gmail API"""
    return mocker.patch('services.email_service.build')

@pytest.fixture
def mock_openai(mocker):
    """Mock OpenAI API"""
    return mocker.patch('openai.ChatCompletion.acreate')

# Integration tests
class TestEmailIntegration:
    def test_scan_inbox(self, client, mock_gmail_service):
        """Test email scanning"""
        mock_gmail_service.return_value.users().messages().list.return_value.execute.return_value = {
            'messages': [{'id': '123', 'snippet': 'Interview invitation'}]
        }

        response = client.post("/api/v1/email/scan")
        assert response.status_code == 200
        assert response.json()['processed'] == 1

# Performance tests
class TestPerformance:
    def test_ats_optimization_speed(self, client):
        """ATS optimization should complete in <2 seconds"""
        import time

        start = time.time()
        response = client.post("/api/v1/ats/analyze", json={
            'resume_path': 'test_resume.docx',
            'job_description': 'Test job description...'
        })
        duration = time.time() - start

        assert duration < 2.0
        assert response.status_code == 200
```

---

## Scalability Considerations

### Horizontal Scaling

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: job-search-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: job-search-api
  template:
    metadata:
      labels:
        app: job-search-api
    spec:
      containers:
      - name: api
        image: job-search-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Queue Scaling

```python
# Autoscaling Celery workers based on queue length
class CeleryAutoscaler:
    def __init__(self):
        self.min_workers = 2
        self.max_workers = 10
        self.queue_threshold = 100

    def check_and_scale(self):
        queue_length = self.get_queue_length()
        current_workers = self.get_worker_count()

        if queue_length > self.queue_threshold:
            new_workers = min(
                current_workers + 2,
                self.max_workers
            )
            self.scale_workers(new_workers)
        elif queue_length < 10 and current_workers > self.min_workers:
            self.scale_workers(self.min_workers)
```

---

## Conclusion

This architecture provides a robust foundation for transforming the current file-copying system into a genuine automation platform. Key principles:

1. **Modular Design**: Each component is independent and testable
2. **Scalable Infrastructure**: Can grow with usage
3. **Security First**: Authentication, rate limiting, and data protection
4. **Observable System**: Comprehensive logging and metrics
5. **Performance Optimized**: Caching, indexes, and async processing

The architecture supports incremental implementation while maintaining system stability and performance.