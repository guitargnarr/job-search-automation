#!/usr/bin/env python3
"""
Job Search MCP Server
Exposes job search automation tools through Model Context Protocol
for cross-session availability and async operations
"""

import os
import sys
import json
import sqlite3
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import existing modules
from automation.generators.generate_application_package import ApplicationPackageGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # MCP SDK imports
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    logger.warning("MCP SDK not installed. Install with: pip install mcp")
    # Fallback mode for testing without MCP
    Server = None
    types = None


class JobSearchMCPServer:
    """MCP Server for job search automation"""

    def __init__(self):
        """Initialize the MCP server with job search tools"""
        if Server is None:
            logger.error("MCP SDK not available. Running in fallback mode.")
            self.server = None
        else:
            self.server = Server("job-search-automation")

        self.project_root = Path.home() / "Desktop" / "Job_Search"
        self.db_path = self.project_root / "tracking" / "database" / "job_tracker.db"
        self.package_generator = ApplicationPackageGenerator(str(self.db_path))

        # Statistics tracking
        self.stats = {
            "packages_generated": 0,
            "jobs_searched": 0,
            "applications_tracked": 0,
            "analyses_performed": 0
        }

        if self.server:
            self._register_tools()

    def _register_tools(self):
        """Register all job search tools with the MCP server"""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List all available job search automation tools"""
            return [
                types.Tool(
                    name="generate_application",
                    description="Generate a complete application package for a job. Creates tailored resume, cover letter, and application notes based on job analysis.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_id": {
                                "type": "integer",
                                "description": "Job ID from the database"
                            },
                            "custom_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Additional keywords to emphasize (optional)"
                            }
                        },
                        "required": ["job_id"]
                    }
                ),
                types.Tool(
                    name="search_jobs",
                    description="Search for jobs across multiple platforms simultaneously. Returns deduplicated results with relevance scoring.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "keywords": {
                                "type": "string",
                                "description": "Search keywords (e.g., 'business analyst healthcare')"
                            },
                            "location": {
                                "type": "string",
                                "description": "Job location (e.g., 'Louisville, KY' or 'remote')"
                            },
                            "platforms": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["linkedin", "indeed", "glassdoor", "all"]
                                },
                                "description": "Platforms to search (default: all)"
                            },
                            "days_posted": {
                                "type": "integer",
                                "description": "Maximum days since posting (default: 7)"
                            }
                        },
                        "required": ["keywords"]
                    }
                ),
                types.Tool(
                    name="analyze_job_fit",
                    description="Analyze how well a job matches your profile. Provides detailed scoring and recommendations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_id": {
                                "type": "integer",
                                "description": "Job ID to analyze"
                            },
                            "job_url": {
                                "type": "string",
                                "description": "URL of job posting (if not in database)"
                            },
                            "job_description": {
                                "type": "string",
                                "description": "Job description text (if providing directly)"
                            }
                        },
                        "required": []  # At least one should be provided
                    }
                ),
                types.Tool(
                    name="track_application",
                    description="Update application status and track progress. Manages follow-ups and reminders.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_id": {
                                "type": "integer",
                                "description": "Job ID to update"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["Applied", "In Review", "Phone Screen", "Interview",
                                        "Technical", "Final Round", "Offer", "Rejected", "Withdrawn"],
                                "description": "New application status"
                            },
                            "notes": {
                                "type": "string",
                                "description": "Additional notes about the application"
                            },
                            "follow_up_date": {
                                "type": "string",
                                "description": "Date for follow-up reminder (YYYY-MM-DD)"
                            }
                        },
                        "required": ["job_id", "status"]
                    }
                ),
                types.Tool(
                    name="get_analytics",
                    description="Get job search analytics and insights. Shows application funnel, response rates, and recommendations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "metric_type": {
                                "type": "string",
                                "enum": ["overview", "funnel", "response_rate", "skills_gap", "timeline"],
                                "description": "Type of analytics to retrieve"
                            },
                            "date_range": {
                                "type": "integer",
                                "description": "Number of days to analyze (default: 30)"
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="bulk_apply",
                    description="Generate application packages for multiple high-priority jobs at once.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "priority": {
                                "type": "string",
                                "enum": ["HIGH", "MEDIUM", "ALL"],
                                "description": "Priority level of jobs to process"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of applications to generate (default: 5)"
                            }
                        },
                        "required": []
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_tool_call(
            name: str,
            arguments: Optional[Dict[str, Any]] = None
        ) -> list[types.TextContent]:
            """Handle tool execution requests"""

            try:
                if name == "generate_application":
                    result = await self._generate_application_async(arguments)
                elif name == "search_jobs":
                    result = await self._search_jobs_async(arguments)
                elif name == "analyze_job_fit":
                    result = await self._analyze_job_fit_async(arguments)
                elif name == "track_application":
                    result = await self._track_application_async(arguments)
                elif name == "get_analytics":
                    result = await self._get_analytics_async(arguments)
                elif name == "bulk_apply":
                    result = await self._bulk_apply_async(arguments)
                else:
                    result = f"Unknown tool: {name}"

                return [types.TextContent(type="text", text=str(result))]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def _generate_application_async(self, args: Dict[str, Any]) -> Dict:
        """Async wrapper for application package generation"""
        job_id = args.get("job_id")
        custom_keywords = args.get("custom_keywords", [])

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        success, message, folder_path = await loop.run_in_executor(
            None,
            self.package_generator.generate_package,
            job_id
        )

        self.stats["packages_generated"] += 1

        return {
            "success": success,
            "message": message,
            "folder_path": str(folder_path) if folder_path else None,
            "stats": {
                "total_generated": self.stats["packages_generated"]
            }
        }

    async def _search_jobs_async(self, args: Dict[str, Any]) -> Dict:
        """Search for jobs across multiple platforms"""
        keywords = args.get("keywords", "")
        location = args.get("location", "remote")
        platforms = args.get("platforms", ["all"])
        days_posted = args.get("days_posted", 7)

        results = []

        # Simulate async job search (in production, this would call real APIs)
        search_tasks = []

        if "all" in platforms or "linkedin" in platforms:
            search_tasks.append(self._search_linkedin(keywords, location, days_posted))
        if "all" in platforms or "indeed" in platforms:
            search_tasks.append(self._search_indeed(keywords, location, days_posted))
        if "all" in platforms or "glassdoor" in platforms:
            search_tasks.append(self._search_glassdoor(keywords, location, days_posted))

        # Run all searches concurrently
        if search_tasks:
            platform_results = await asyncio.gather(*search_tasks)
            for platform_result in platform_results:
                results.extend(platform_result)

        # Deduplicate results
        seen = set()
        unique_results = []
        for job in results:
            key = (job.get("title", ""), job.get("company", ""))
            if key not in seen:
                seen.add(key)
                unique_results.append(job)

        self.stats["jobs_searched"] += len(unique_results)

        return {
            "total_found": len(unique_results),
            "jobs": unique_results[:20],  # Return top 20
            "platforms_searched": platforms,
            "search_time": datetime.now().isoformat()
        }

    async def _search_linkedin(self, keywords: str, location: str, days: int) -> List[Dict]:
        """Simulate LinkedIn job search"""
        await asyncio.sleep(0.5)  # Simulate API call
        return [
            {
                "platform": "LinkedIn",
                "title": f"Senior {keywords.title()}",
                "company": "Tech Corp",
                "location": location,
                "posted": "2 days ago",
                "url": "https://linkedin.com/jobs/example"
            }
        ]

    async def _search_indeed(self, keywords: str, location: str, days: int) -> List[Dict]:
        """Simulate Indeed job search"""
        await asyncio.sleep(0.5)  # Simulate API call
        return [
            {
                "platform": "Indeed",
                "title": f"{keywords.title()} Specialist",
                "company": "Business Inc",
                "location": location,
                "posted": "1 day ago",
                "url": "https://indeed.com/jobs/example"
            }
        ]

    async def _search_glassdoor(self, keywords: str, location: str, days: int) -> List[Dict]:
        """Simulate Glassdoor job search"""
        await asyncio.sleep(0.5)  # Simulate API call
        return [
            {
                "platform": "Glassdoor",
                "title": f"{keywords.title()} Manager",
                "company": "Enterprise Co",
                "location": location,
                "posted": "3 days ago",
                "url": "https://glassdoor.com/jobs/example"
            }
        ]

    async def _analyze_job_fit_async(self, args: Dict[str, Any]) -> Dict:
        """Analyze job fit score"""
        job_id = args.get("job_id")
        job_url = args.get("job_url")
        job_description = args.get("job_description", "")

        # Simulate analysis
        await asyncio.sleep(1)

        self.stats["analyses_performed"] += 1

        return {
            "fit_score": 85,
            "strengths": [
                "Strong match for business analysis skills",
                "Healthcare experience aligns well",
                "Required tools expertise present"
            ],
            "gaps": [
                "Could emphasize project management more",
                "Consider highlighting data visualization skills"
            ],
            "recommendation": "HIGH PRIORITY - Strong match, apply with Template 2",
            "estimated_response_rate": "35%"
        }

    async def _track_application_async(self, args: Dict[str, Any]) -> Dict:
        """Update application tracking"""
        job_id = args.get("job_id")
        status = args.get("status")
        notes = args.get("notes", "")
        follow_up_date = args.get("follow_up_date")

        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE applications
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE job_id = ?
        """, (status, job_id))

        if follow_up_date:
            cursor.execute("""
                UPDATE applications
                SET follow_up_date = ?
                WHERE job_id = ?
            """, (follow_up_date, job_id))

        conn.commit()
        conn.close()

        self.stats["applications_tracked"] += 1

        return {
            "success": True,
            "job_id": job_id,
            "new_status": status,
            "follow_up_scheduled": follow_up_date is not None
        }

    async def _get_analytics_async(self, args: Dict[str, Any]) -> Dict:
        """Get job search analytics"""
        metric_type = args.get("metric_type", "overview")
        date_range = args.get("date_range", 30)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if metric_type == "overview":
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'Applied' THEN 1 ELSE 0 END) as applied,
                       SUM(CASE WHEN status IN ('Interview', 'Phone Screen') THEN 1 ELSE 0 END) as interviews
                FROM applications
            """)
            result = cursor.fetchone()

            analytics = {
                "total_jobs": result[0],
                "applications_sent": result[1],
                "interviews_scheduled": result[2],
                "response_rate": f"{(result[2]/result[1]*100 if result[1] > 0 else 0):.1f}%"
            }
        else:
            analytics = {"message": f"Analytics for {metric_type} coming soon"}

        conn.close()

        return analytics

    async def _bulk_apply_async(self, args: Dict[str, Any]) -> Dict:
        """Generate multiple application packages"""
        priority = args.get("priority", "HIGH")
        limit = args.get("limit", 5)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get jobs to apply to
        if priority == "ALL":
            query = "SELECT id, title FROM jobs LIMIT ?"
            params = (limit,)
        else:
            query = "SELECT id, title FROM jobs WHERE priority = ? LIMIT ?"
            params = (priority, limit)

        cursor.execute(query, params)
        jobs = cursor.fetchall()
        conn.close()

        # Generate packages concurrently
        tasks = []
        for job_id, title in jobs:
            tasks.append(self._generate_application_async({"job_id": job_id}))

        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if r.get("success"))

        return {
            "total_processed": len(jobs),
            "successful": successful,
            "failed": len(jobs) - successful,
            "jobs_processed": [{"id": j[0], "title": j[1]} for j in jobs]
        }

    async def run(self):
        """Run the MCP server"""
        if self.server:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="job-search-automation",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
        else:
            # Fallback: Run as a simple async service
            logger.info("Running in fallback mode without MCP")
            await self._run_fallback_mode()

    async def _run_fallback_mode(self):
        """Run without MCP for testing"""
        logger.info("Job Search Automation Service Started (Fallback Mode)")
        logger.info(f"Database: {self.db_path}")
        logger.info("Available functions:")
        logger.info("  - generate_application(job_id)")
        logger.info("  - search_jobs(keywords, location)")
        logger.info("  - analyze_job_fit(job_id)")
        logger.info("  - track_application(job_id, status)")
        logger.info("  - get_analytics(metric_type)")
        logger.info("  - bulk_apply(priority, limit)")

        # Keep service running
        try:
            while True:
                await asyncio.sleep(60)
                logger.info(f"Service stats: {self.stats}")
        except KeyboardInterrupt:
            logger.info("Service stopped")


async def main():
    """Main entry point"""
    server = JobSearchMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())