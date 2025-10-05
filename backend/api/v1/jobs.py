"""
Jobs API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db

router = APIRouter()

@router.get("/")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    """List all jobs"""
    return {"message": "Jobs endpoint - to be implemented"}