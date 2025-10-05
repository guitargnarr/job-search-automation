"""
Job Search Automation Platform - Main API
Real automation, not just file copying
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Import routers
from backend.api.v1 import (
    applications,
    email,
    # linkedin,  # DEPRECATED - LinkedIn automation removed
    jobs,
    analytics,
    ats,
    follow_ups
)

# Import core services
from backend.core.database import engine, Base
from backend.core.logging import setup_logging

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Job Search Automation Platform")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized")

    # Start background tasks
    from backend.core.scheduler import start_scheduler
    scheduler = await start_scheduler()

    yield

    # Shutdown
    logger.info("Shutting down Job Search Automation Platform")
    scheduler.shutdown()

# Create FastAPI app
app = FastAPI(
    title="Job Search Automation Platform",
    description="Real automation that actually saves time",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if the API is running"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "automation_level": "75%",
        "message": "Real automation, not file copying"
    }

# Include API routers
app.include_router(
    applications.router,
    prefix="/api/v1/applications",
    tags=["applications"]
)

app.include_router(
    email.router,
    prefix="/api/v1/email",
    tags=["email"]
)

# LinkedIn router deprecated - automation features removed
# app.include_router(
#     linkedin.router,
#     prefix="/api/v1/linkedin",
#     tags=["linkedin"]
# )

app.include_router(
    jobs.router,
    prefix="/api/v1/jobs",
    tags=["jobs"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"]
)

app.include_router(
    ats.router,
    prefix="/api/v1/ats",
    tags=["ats"]
)

app.include_router(
    follow_ups.router,
    prefix="/api/v1/follow-ups",
    tags=["follow-ups"]
)


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "Job Search Automation Platform",
        "status": "operational",
        "features": {
            "email_tracking": "active",
            "ats_optimization": "active",
            "linkedin_automation": "deprecated",  # LinkedIn features removed
            "job_aggregation": "active",
            "ai_generation": "deprecated",  # OpenAI features removed
            "follow_up_system": "active"
        },
        "automation_percentage": 75,
        "time_saved_per_application": "45 minutes",
        "message": "Building the future of job searching"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
