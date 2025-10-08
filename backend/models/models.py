"""
Database models for real job search automation
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, JSON, Float, Date, Enum, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from backend.core.database import Base

class Priority(enum.Enum):
    """Job priority levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    SKIP = "SKIP"

class ApplicationStatus(enum.Enum):
    """Application status tracking"""
    DRAFT = "DRAFT"
    READY = "READY"
    APPLIED = "APPLIED"
    RESPONDED = "RESPONDED"
    INTERVIEWING = "INTERVIEWING"
    OFFERED = "OFFERED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class ResponseType(enum.Enum):
    """Email response classifications"""
    INTERVIEW = "INTERVIEW"
    REJECTION = "REJECTION"
    INFO_REQUEST = "INFO_REQUEST"
    OFFER = "OFFER"
    OTHER = "OTHER"

class Company(Base):
    """Company information with research data"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    website = Column(String(500))
    industry = Column(String(100))
    size_range = Column(String(50))
    glassdoor_rating = Column(Float)
    linkedin_url = Column(String(500))

    # Research data
    recent_news = Column(JSON)  # List of recent news articles
    tech_stack = Column(JSON)   # Technologies used
    culture_notes = Column(Text)
    interview_process = Column(JSON)  # Common interview steps

    # Tracking
    last_researched = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    jobs = relationship("Job", back_populates="company")

class Job(Base):
    """Job postings with intelligent tracking"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))

    # Job details
    title = Column(String(255), nullable=False)
    job_url = Column(String(500))
    source = Column(String(50))  # linkedin, indeed, company_site
    job_description = Column(Text)
    requirements = Column(JSON)  # Parsed requirements
    posted_date = Column(Date)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    remote_type = Column(String(50))  # remote, hybrid, onsite
    location = Column(String(255))

    # Analysis scores
    ats_score = Column(Integer)  # 0-100
    fit_score = Column(Integer)  # 0-100
    keywords = Column(JSON)  # Extracted keywords
    missing_keywords = Column(JSON)  # Keywords we don't have

    # Status tracking
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    status = Column(String(50), default="new")
    application_deadline = Column(Date)

    # Timestamps
    discovered_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="jobs")
    application = relationship("Application", back_populates="job", uselist=False)

    # Indexes for performance
    __table_args__ = (
        Index("idx_job_priority_status", "priority", "status"),
        Index("idx_job_fit_score", "fit_score"),
    )

class Application(Base):
    """Application tracking with automation data"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), unique=True)

    # Application details
    applied_date = Column(DateTime)
    application_method = Column(String(100))  # company_site, linkedin, indeed
    resume_version = Column(String(100))
    cover_letter_version = Column(String(100))

    # Customization tracking
    keywords_added = Column(JSON)  # Keywords we added to resume
    customizations_made = Column(JSON)  # What we changed
    ats_score_achieved = Column(Integer)

    # Status tracking
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT)

    # Response tracking (automated)
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime)
    response_type = Column(Enum(ResponseType))
    response_content = Column(Text)  # Email content

    # Interview tracking
    interview_scheduled = Column(DateTime)
    interview_type = Column(String(50))  # phone, video, onsite
    interviewer_names = Column(JSON)
    interview_notes = Column(Text)

    # Referral tracking
    referral_used = Column(Boolean, default=False)
    referral_person = Column(String(255))
    referral_relationship = Column(String(100))

    # Follow-up tracking
    follow_ups_sent = Column(Integer, default=0)
    last_follow_up = Column(DateTime)
    next_follow_up_scheduled = Column(DateTime)
    followup_sent = Column(Boolean, default=False)  # Auto-followup flag for applications needing follow-up

    # Outcome
    offer_received = Column(Boolean, default=False)
    offer_amount = Column(Integer)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    job = relationship("Job", back_populates="application")
    emails = relationship("EmailTracking", back_populates="application")
    linkedin_outreach = relationship("LinkedInOutreach", back_populates="application")
    follow_ups = relationship("FollowUp", back_populates="application")

class EmailTracking(Base):
    """Automated email tracking"""
    __tablename__ = "email_tracking"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    # Email details
    gmail_id = Column(String(255), unique=True)  # Gmail message ID
    thread_id = Column(String(255))  # Gmail thread ID
    from_address = Column(String(255))
    to_address = Column(String(255))
    subject = Column(String(500))
    body = Column(Text)
    received_date = Column(DateTime)

    # Classification (automated)
    classification = Column(Enum(ResponseType))
    confidence_score = Column(Float)  # How sure we are

    # Action tracking
    processed = Column(Boolean, default=False)
    action_required = Column(Boolean, default=False)
    action_taken = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    processed_at = Column(DateTime)

    # Relationships
    application = relationship("Application", back_populates="emails")

    # Index for performance
    __table_args__ = (
        Index("idx_email_unprocessed", "processed", "received_date"),
    )

class LinkedInOutreach(Base):
    """LinkedIn automation tracking"""
    __tablename__ = "linkedin_outreach"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    # Contact details
    profile_url = Column(String(500))
    person_name = Column(String(255))
    person_title = Column(String(255))
    person_company = Column(String(255))

    # Connection tracking
    connection_status = Column(String(50))  # pending, connected, rejected
    connection_sent_date = Column(DateTime)
    connection_accepted_date = Column(DateTime)

    # Message tracking
    message_sent = Column(Text)
    message_sent_date = Column(DateTime)
    response_received = Column(Boolean, default=False)
    response_text = Column(Text)
    response_date = Column(DateTime)

    # Relationship strength
    mutual_connections = Column(Integer)
    interaction_count = Column(Integer, default=0)
    relationship_score = Column(Integer)  # 0-100

    # Follow-up
    follow_up_scheduled = Column(DateTime)
    follow_up_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    application = relationship("Application", back_populates="linkedin_outreach")

class FollowUp(Base):
    """Follow-up tracking and automation"""
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    # Follow-up details
    scheduled_date = Column(DateTime, nullable=False)
    channel = Column(String(50))  # email, linkedin
    recipient = Column(String(255))

    # Content
    subject = Column(String(500))
    message = Column(Text)

    # Status
    sent = Column(Boolean, default=False)
    sent_date = Column(DateTime)
    response_received = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now())

    # Relationships
    application = relationship("Application", back_populates="follow_ups")

    # Index for scheduled follow-ups
    __table_args__ = (
        Index("idx_followup_scheduled", "sent", "scheduled_date"),
    )

class TemplatePerformance(Base):
    """Track which templates actually work"""
    __tablename__ = "template_performance"

    id = Column(Integer, primary_key=True)

    # Template identification
    template_type = Column(String(50))  # resume, cover_letter
    template_name = Column(String(100))
    template_version = Column(String(50))

    # Performance metrics
    times_used = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    interviews_received = Column(Integer, default=0)
    offers_received = Column(Integer, default=0)

    # Calculated rates
    response_rate = Column(Float)
    interview_rate = Column(Float)
    offer_rate = Column(Float)
    avg_time_to_response = Column(Float)  # days

    # A/B testing
    is_control = Column(Boolean, default=False)
    variant_group = Column(String(50))

    # Timestamps
    first_used = Column(DateTime)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AnalyticsEvent(Base):
    """Track everything for analysis"""
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True)

    # Event details
    event_type = Column(String(100), nullable=False)
    event_category = Column(String(50))
    event_data = Column(JSON)

    # Context
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=func.now())

    # Index for querying
    __table_args__ = (
        Index("idx_analytics_type_date", "event_type", "created_at"),
    )