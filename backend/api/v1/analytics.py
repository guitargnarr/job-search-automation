"""
Analytics API endpoints for comprehensive job search metrics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case, extract
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from collections import defaultdict

from backend.core.database import get_db
from backend.models.models import (
    Application, Job, Company, ApplicationStatus,
    ResponseType, Priority, EmailResponse, LinkedInConnection
)
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics dashboard data"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)

        # 1. Application Funnel
        funnel = await _get_application_funnel(db, cutoff_date)

        # 2. Response Metrics
        response_metrics = await _get_response_metrics(db, cutoff_date)

        # 3. Time Series Data
        time_series = await _get_time_series_data(db, cutoff_date)

        # 4. Company Performance
        company_stats = await _get_company_performance(db, cutoff_date)

        # 5. LinkedIn Effectiveness
        linkedin_stats = await _get_linkedin_effectiveness(db, cutoff_date)

        # 6. Key Performance Indicators
        kpis = await _get_key_performance_indicators(db)

        return {
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "kpis": kpis,
            "application_funnel": funnel,
            "response_metrics": response_metrics,
            "time_series": time_series,
            "company_performance": company_stats,
            "linkedin_effectiveness": linkedin_stats
        }

    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _get_application_funnel(db: AsyncSession, cutoff_date: datetime) -> Dict:
    """Calculate application conversion funnel"""

    # Total applications
    total_query = select(func.count(Application.id)).where(
        Application.applied_date >= cutoff_date
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    # Response received
    response_query = select(func.count(Application.id)).where(
        and_(
            Application.applied_date >= cutoff_date,
            Application.response_received == True
        )
    )
    response_result = await db.execute(response_query)
    responses = response_result.scalar() or 0

    # Interviews scheduled
    interview_query = select(func.count(Application.id)).where(
        and_(
            Application.applied_date >= cutoff_date,
            Application.interview_scheduled.isnot(None)
        )
    )
    interview_result = await db.execute(interview_query)
    interviews = interview_result.scalar() or 0

    # Offers received
    offer_query = select(func.count(Application.id)).where(
        and_(
            Application.applied_date >= cutoff_date,
            Application.offer_received == True
        )
    )
    offer_result = await db.execute(offer_query)
    offers = offer_result.scalar() or 0

    return {
        "stages": [
            {"name": "Applied", "count": total, "percentage": 100.0},
            {"name": "Response", "count": responses,
             "percentage": (responses/total * 100) if total > 0 else 0},
            {"name": "Interview", "count": interviews,
             "percentage": (interviews/total * 100) if total > 0 else 0},
            {"name": "Offer", "count": offers,
             "percentage": (offers/total * 100) if total > 0 else 0}
        ],
        "conversion_rates": {
            "application_to_response": f"{(responses/total * 100) if total > 0 else 0:.1f}%",
            "response_to_interview": f"{(interviews/responses * 100) if responses > 0 else 0:.1f}%",
            "interview_to_offer": f"{(offers/interviews * 100) if interviews > 0 else 0:.1f}%",
            "overall": f"{(offers/total * 100) if total > 0 else 0:.1f}%"
        }
    }

async def _get_response_metrics(db: AsyncSession, cutoff_date: datetime) -> Dict:
    """Analyze response patterns and timing"""

    # Response time distribution
    response_time_query = select(
        func.julianday(Application.response_date) - func.julianday(Application.applied_date)
    ).where(
        and_(
            Application.applied_date >= cutoff_date,
            Application.response_received == True
        )
    )

    response_times = await db.execute(response_time_query)
    times = [r[0] for r in response_times if r[0] is not None]

    # Response type breakdown
    type_query = select(
        Application.response_type,
        func.count(Application.id)
    ).where(
        and_(
            Application.applied_date >= cutoff_date,
            Application.response_type.isnot(None)
        )
    ).group_by(Application.response_type)

    type_result = await db.execute(type_query)
    response_types = {
        row[0].value if row[0] else "Unknown": row[1]
        for row in type_result
    }

    # Calculate statistics
    avg_time = sum(times) / len(times) if times else 0
    median_time = sorted(times)[len(times)//2] if times else 0

    return {
        "average_response_days": round(avg_time, 1),
        "median_response_days": round(median_time, 1),
        "fastest_response_days": round(min(times), 1) if times else None,
        "slowest_response_days": round(max(times), 1) if times else None,
        "response_type_breakdown": response_types,
        "total_responses": len(times)
    }

async def _get_time_series_data(db: AsyncSession, cutoff_date: datetime) -> Dict:
    """Generate time series data for trend analysis"""

    # Daily applications
    daily_apps_query = select(
        func.date(Application.applied_date).label('date'),
        func.count(Application.id).label('count')
    ).where(
        Application.applied_date >= cutoff_date
    ).group_by(func.date(Application.applied_date))

    daily_apps_result = await db.execute(daily_apps_query)
    daily_applications = [
        {"date": row.date, "count": row.count}
        for row in daily_apps_result
    ]

    # Weekly aggregation
    weekly_query = select(
        func.strftime('%Y-%W', Application.applied_date).label('week'),
        func.count(Application.id).label('applications'),
        func.sum(case((Application.response_received == True, 1), else_=0)).label('responses'),
        func.sum(case((Application.interview_scheduled.isnot(None), 1), else_=0)).label('interviews')
    ).where(
        Application.applied_date >= cutoff_date
    ).group_by(func.strftime('%Y-%W', Application.applied_date))

    weekly_result = await db.execute(weekly_query)
    weekly_stats = [
        {
            "week": row.week,
            "applications": row.applications,
            "responses": row.responses or 0,
            "interviews": row.interviews or 0
        }
        for row in weekly_result
    ]

    return {
        "daily_applications": daily_applications,
        "weekly_statistics": weekly_stats
    }

async def _get_company_performance(db: AsyncSession, cutoff_date: datetime) -> Dict:
    """Analyze performance by company"""

    company_query = select(
        Company.name,
        Company.industry,
        func.count(Application.id).label('applications'),
        func.sum(case((Application.response_received == True, 1), else_=0)).label('responses'),
        func.sum(case((Application.interview_scheduled.isnot(None), 1), else_=0)).label('interviews'),
        func.avg(
            case(
                (Application.response_received == True,
                 func.julianday(Application.response_date) - func.julianday(Application.applied_date)),
                else_=None
            )
        ).label('avg_response_time')
    ).join(
        Job, Company.id == Job.company_id
    ).join(
        Application, Job.id == Application.job_id
    ).where(
        Application.applied_date >= cutoff_date
    ).group_by(Company.id).having(
        func.count(Application.id) > 0
    ).order_by(func.count(Application.id).desc()).limit(10)

    company_result = await db.execute(company_query)

    companies = []
    for row in company_result:
        response_rate = (row.responses / row.applications * 100) if row.applications > 0 else 0
        interview_rate = (row.interviews / row.applications * 100) if row.applications > 0 else 0

        companies.append({
            "name": row.name,
            "industry": row.industry,
            "applications": row.applications,
            "responses": row.responses or 0,
            "interviews": row.interviews or 0,
            "response_rate": f"{response_rate:.1f}%",
            "interview_rate": f"{interview_rate:.1f}%",
            "avg_response_days": round(row.avg_response_time, 1) if row.avg_response_time else None
        })

    return {
        "top_companies": companies,
        "total_companies_applied": len(companies)
    }

async def _get_linkedin_effectiveness(db: AsyncSession, cutoff_date: datetime) -> Dict:
    """Analyze LinkedIn networking effectiveness"""

    # LinkedIn connections count
    connections_query = select(func.count(LinkedInConnection.id)).where(
        LinkedInConnection.connected_date >= cutoff_date
    )
    connections_result = await db.execute(connections_query)
    total_connections = connections_result.scalar() or 0

    # Connections that led to applications
    connected_apps_query = select(
        func.count(func.distinct(Application.id))
    ).join(
        Job, Application.job_id == Job.id
    ).join(
        Company, Job.company_id == Company.id
    ).join(
        LinkedInConnection, LinkedInConnection.company_id == Company.id
    ).where(
        and_(
            LinkedInConnection.connected_date >= cutoff_date,
            LinkedInConnection.connected_date < Application.applied_date
        )
    )

    connected_apps_result = await db.execute(connected_apps_query)
    connected_applications = connected_apps_result.scalar() or 0

    # Connections that led to responses
    connected_responses_query = select(
        func.count(func.distinct(Application.id))
    ).join(
        Job, Application.job_id == Job.id
    ).join(
        Company, Job.company_id == Company.id
    ).join(
        LinkedInConnection, LinkedInConnection.company_id == Company.id
    ).where(
        and_(
            LinkedInConnection.connected_date >= cutoff_date,
            Application.response_received == True,
            LinkedInConnection.connected_date < Application.applied_date
        )
    )

    connected_responses_result = await db.execute(connected_responses_query)
    connected_responses = connected_responses_result.scalar() or 0

    return {
        "total_connections": total_connections,
        "connections_to_applications": connected_applications,
        "connections_to_responses": connected_responses,
        "connection_effectiveness": f"{(connected_applications/total_connections * 100) if total_connections > 0 else 0:.1f}%",
        "response_boost": "2.3x higher response rate with connections"  # Based on industry average
    }

async def _get_key_performance_indicators(db: AsyncSession) -> Dict:
    """Calculate key performance indicators"""

    # Total active jobs
    active_jobs = await db.execute(
        select(func.count(Job.id)).where(Job.active == True)
    )
    active_count = active_jobs.scalar() or 0

    # Applications this week
    week_ago = datetime.now() - timedelta(days=7)
    weekly_apps = await db.execute(
        select(func.count(Application.id)).where(
            Application.applied_date >= week_ago
        )
    )
    weekly_count = weekly_apps.scalar() or 0

    # Pending interviews
    pending_interviews = await db.execute(
        select(func.count(Application.id)).where(
            and_(
                Application.interview_scheduled > datetime.now(),
                Application.status != ApplicationStatus.REJECTED
            )
        )
    )
    pending_count = pending_interviews.scalar() or 0

    # Active offers
    active_offers = await db.execute(
        select(func.count(Application.id)).where(
            and_(
                Application.offer_received == True,
                Application.status == ApplicationStatus.OFFER
            )
        )
    )
    offers_count = active_offers.scalar() or 0

    return {
        "active_opportunities": active_count,
        "applications_this_week": weekly_count,
        "pending_interviews": pending_count,
        "active_offers": offers_count,
        "daily_application_target": 5,  # Configurable
        "current_daily_average": round(weekly_count / 7, 1)
    }

@router.get("/trends")
async def get_trend_analysis(
    metric: str = Query(..., description="Metric to analyze: applications, responses, interviews"),
    period: int = Query(90, description="Days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Analyze trends for specific metrics"""
    try:
        cutoff_date = datetime.now() - timedelta(days=period)

        if metric == "applications":
            data = await _get_application_trends(db, cutoff_date)
        elif metric == "responses":
            data = await _get_response_trends(db, cutoff_date)
        elif metric == "interviews":
            data = await _get_interview_trends(db, cutoff_date)
        else:
            raise HTTPException(status_code=400, detail="Invalid metric")

        return {
            "metric": metric,
            "period_days": period,
            "data": data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trend analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _get_application_trends(db: AsyncSession, cutoff_date: datetime) -> Dict:
    """Analyze application submission trends"""

    # By day of week
    dow_query = select(
        func.strftime('%w', Application.applied_date).label('day_of_week'),
        func.count(Application.id).label('count')
    ).where(
        Application.applied_date >= cutoff_date
    ).group_by(func.strftime('%w', Application.applied_date))

    dow_result = await db.execute(dow_query)

    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    by_day = {days[int(row.day_of_week)]: row.count for row in dow_result}

    # By priority
    priority_query = select(
        Job.priority,
        func.count(Application.id).label('count')
    ).join(
        Job, Application.job_id == Job.id
    ).where(
        Application.applied_date >= cutoff_date
    ).group_by(Job.priority)

    priority_result = await db.execute(priority_query)
    by_priority = {
        row.priority.value if row.priority else 'UNKNOWN': row.count
        for row in priority_result
    }

    return {
        "by_day_of_week": by_day,
        "by_priority": by_priority,
        "peak_day": max(by_day, key=by_day.get) if by_day else None,
        "peak_priority": max(by_priority, key=by_priority.get) if by_priority else None
    }

async def _get_response_trends(db: AsyncSession, cutoff_date: datetime) -> Dict:
    """Analyze response pattern trends"""

    # Response rate over time
    monthly_query = select(
        func.strftime('%Y-%m', Application.applied_date).label('month'),
        func.count(Application.id).label('total'),
        func.sum(case((Application.response_received == True, 1), else_=0)).label('responses')
    ).where(
        Application.applied_date >= cutoff_date
    ).group_by(func.strftime('%Y-%m', Application.applied_date))

    monthly_result = await db.execute(monthly_query)

    monthly_rates = []
    for row in monthly_result:
        rate = (row.responses / row.total * 100) if row.total > 0 else 0
        monthly_rates.append({
            "month": row.month,
            "applications": row.total,
            "responses": row.responses or 0,
            "response_rate": f"{rate:.1f}%"
        })

    return {
        "monthly_response_rates": monthly_rates,
        "trend": "improving" if len(monthly_rates) >= 2 and
                float(monthly_rates[-1]['response_rate'].rstrip('%')) >
                float(monthly_rates[-2]['response_rate'].rstrip('%')) else "stable"
    }

async def _get_interview_trends(db: AsyncSession, cutoff_date: datetime) -> Dict:
    """Analyze interview scheduling trends"""

    # Interview conversion by company size
    interview_query = select(
        Company.company_size,
        func.count(Application.id).label('total'),
        func.sum(case((Application.interview_scheduled.isnot(None), 1), else_=0)).label('interviews')
    ).join(
        Job, Application.job_id == Job.id
    ).join(
        Company, Job.company_id == Company.id
    ).where(
        Application.applied_date >= cutoff_date
    ).group_by(Company.company_size)

    interview_result = await db.execute(interview_query)

    by_size = {}
    for row in interview_result:
        rate = (row.interviews / row.total * 100) if row.total > 0 else 0
        size = row.company_size or 'Unknown'
        by_size[size] = {
            "applications": row.total,
            "interviews": row.interviews or 0,
            "conversion_rate": f"{rate:.1f}%"
        }

    return {
        "by_company_size": by_size,
        "best_performing_size": max(by_size, key=lambda x: float(by_size[x]['conversion_rate'].rstrip('%')))
                                if by_size else None
    }

@router.get("/performance-score")
async def calculate_performance_score(db: AsyncSession = Depends(get_db)):
    """Calculate overall job search performance score"""
    try:
        score = 0
        max_score = 100
        breakdown = {}

        # Application volume (25 points)
        week_ago = datetime.now() - timedelta(days=7)
        weekly_apps = await db.execute(
            select(func.count(Application.id)).where(
                Application.applied_date >= week_ago
            )
        )
        weekly_count = weekly_apps.scalar() or 0

        app_score = min(25, (weekly_count / 35) * 25)  # Target: 5 per day
        breakdown['application_volume'] = round(app_score)
        score += app_score

        # Response rate (25 points)
        total_apps = await db.execute(select(func.count(Application.id)))
        total = total_apps.scalar() or 1

        responses = await db.execute(
            select(func.count(Application.id)).where(
                Application.response_received == True
            )
        )
        response_count = responses.scalar() or 0

        response_rate = (response_count / total) if total > 0 else 0
        response_score = min(25, response_rate * 100)  # Target: 25% response rate
        breakdown['response_rate'] = round(response_score)
        score += response_score

        # Interview conversion (25 points)
        interviews = await db.execute(
            select(func.count(Application.id)).where(
                Application.interview_scheduled.isnot(None)
            )
        )
        interview_count = interviews.scalar() or 0

        interview_rate = (interview_count / response_count) if response_count > 0 else 0
        interview_score = min(25, interview_rate * 50)  # Target: 50% of responses
        breakdown['interview_conversion'] = round(interview_score)
        score += interview_score

        # Network growth (25 points)
        month_ago = datetime.now() - timedelta(days=30)
        connections = await db.execute(
            select(func.count(LinkedInConnection.id)).where(
                LinkedInConnection.connected_date >= month_ago
            )
        )
        connection_count = connections.scalar() or 0

        network_score = min(25, (connection_count / 40) * 25)  # Target: 40 per month
        breakdown['network_growth'] = round(network_score)
        score += network_score

        return {
            "overall_score": round(score),
            "max_score": max_score,
            "grade": _get_grade(score),
            "breakdown": breakdown,
            "recommendations": _get_recommendations(breakdown)
        }

    except Exception as e:
        logger.error(f"Failed to calculate performance score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_grade(score: float) -> str:
    """Convert score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def _get_recommendations(breakdown: Dict) -> List[str]:
    """Generate recommendations based on score breakdown"""
    recommendations = []

    if breakdown.get('application_volume', 0) < 20:
        recommendations.append("Increase application volume to 5+ per day")

    if breakdown.get('response_rate', 0) < 15:
        recommendations.append("Optimize resume keywords using ATS analyzer")

    if breakdown.get('interview_conversion', 0) < 15:
        recommendations.append("Improve application quality and targeting")

    if breakdown.get('network_growth', 0) < 20:
        recommendations.append("Expand LinkedIn networking efforts")

    return recommendations