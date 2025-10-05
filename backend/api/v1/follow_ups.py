"""
Follow-up System API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db

router = APIRouter()

@router.get("/scheduled")
async def get_scheduled_followups(db: AsyncSession = Depends(get_db)):
    """Get scheduled follow-ups"""
    return {"message": "Follow-ups endpoint - to be implemented"}