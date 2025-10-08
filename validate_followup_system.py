#!/usr/bin/env python3
"""
Validation Script for Follow-Up System
Tests the follow-up detection logic and database updates
"""

import asyncio
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, '.')

from backend.core.database import async_session_maker
from backend.services.followup_service import followup_service
from backend.models.models import Application, ApplicationStatus
from sqlalchemy import select, update


async def print_separator(title: str):
    """Print a formatted section separator"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


async def show_current_applications():
    """Display current state of all applications"""
    async with async_session_maker() as db:
        query = select(Application)
        result = await db.execute(query)
        applications = result.scalars().all()

        print(f"\nTotal Applications: {len(applications)}")
        print("\n{:<5} {:<15} {:<20} {:<12} {:<10} {:<8}".format(
            "ID", "Status", "Applied Date", "Days Ago", "Response", "FollowUp"
        ))
        print("-" * 70)

        for app in applications:
            days_ago = "N/A"
            if app.applied_date:
                days_ago = str((datetime.now() - app.applied_date).days)

            print("{:<5} {:<15} {:<20} {:<12} {:<10} {:<8}".format(
                app.id,
                app.status.value if app.status else "Unknown",
                app.applied_date.strftime('%Y-%m-%d') if app.applied_date else "N/A",
                days_ago,
                "Yes" if app.response_received else "No",
                "Yes" if app.followup_sent else "No"
            ))


async def test_followup_detection_dry_run():
    """Test follow-up detection in dry-run mode (no database changes)"""
    print_separator("TEST 1: Dry Run - Detect Applications Needing Follow-Up")

    async with async_session_maker() as db:
        results = await followup_service.check_and_schedule_followup_emails(
            db,
            dry_run=True  # Important: no database changes
        )

        print(f"\n✅ Applications Checked: {results['applications_checked']}")
        print(f"📧 Follow-ups Needed: {results['followups_needed']}")
        print(f"🔒 Dry Run Mode: {results['dry_run']}")

        if results['applications_updated']:
            print("\nApplications that would be flagged for follow-up:")
            print("\n{:<5} {:<30} {:<25} {:<10} {:<10}".format(
                "ID", "Company", "Job Title", "Applied", "Days Ago"
            ))
            print("-" * 80)

            for app in results['applications_updated']:
                print("{:<5} {:<30} {:<25} {:<10} {:<10}".format(
                    app['application_id'],
                    app['company_name'][:29],
                    app['job_title'][:24],
                    app['applied_date'],
                    str(app['days_since_application'])
                ))
        else:
            print("\n✅ No applications need follow-up at this time")

        return results


async def test_followup_detection_live():
    """Test follow-up detection with actual database updates"""
    print_separator("TEST 2: Live Run - Update Database with Follow-Up Flags")

    print("\n⚠️  WARNING: This will modify the database!")
    print("Proceeding with live database updates...")

    async with async_session_maker() as db:
        results = await followup_service.check_and_schedule_followup_emails(
            db,
            dry_run=False  # Actually update the database
        )

        print(f"\n✅ Applications Updated: {len(results['applications_updated'])}")

        if results['applications_updated']:
            print("\nApplications flagged for follow-up:")
            for app in results['applications_updated']:
                print(f"  ✓ {app['company_name']} - {app['job_title']}")
        else:
            print("\n✅ No applications needed follow-up flags")

        return results


async def verify_database_updates():
    """Verify that the followup_sent flags were actually updated"""
    print_separator("TEST 3: Verify Database Updates")

    async with async_session_maker() as db:
        query = select(Application).where(Application.followup_sent == True)
        result = await db.execute(query)
        flagged_apps = result.scalars().all()

        print(f"\n✅ Applications with followup_sent=True: {len(flagged_apps)}")

        if flagged_apps:
            print("\nFlagged Applications:")
            for app in flagged_apps:
                await db.refresh(app, ['job'])
                if app.job:
                    await db.refresh(app.job, ['company'])
                    company_name = app.job.company.name if app.job.company else "Unknown"
                    print(f"  📧 ID {app.id}: {company_name} - {app.job.title}")
        else:
            print("\n✅ No applications currently flagged (expected on first run)")


async def test_get_pending_followups():
    """Test retrieval of pending follow-ups"""
    print_separator("TEST 4: Get Pending Follow-Ups")

    async with async_session_maker() as db:
        pending = await followup_service.get_pending_followups(db)

        print(f"\n✅ Pending Follow-Ups: {len(pending)}")

        if pending:
            print("\nDetails:")
            for follow_up in pending:
                print(f"\n  Application ID: {follow_up['application_id']}")
                print(f"  Company: {follow_up['company_name']}")
                print(f"  Job: {follow_up['job_title']}")
                print(f"  Applied: {follow_up['applied_date']}")
                print(f"  Days Since: {follow_up['days_since_application']}")
                print(f"  Status: {follow_up['status']}")
                print(f"  Follow-ups Sent: {follow_up['follow_ups_sent']}")
        else:
            print("\n✅ No pending follow-ups")


async def reset_followup_flags():
    """Reset all followup_sent flags for testing purposes"""
    print_separator("RESET: Clear Follow-Up Flags")

    print("\n⚠️  This will reset all followup_sent flags to False")
    print("Use this to re-run tests from clean state")

    async with async_session_maker() as db:
        stmt = update(Application).values(followup_sent=False)
        result = await db.execute(stmt)
        await db.commit()

        print(f"\n✅ Reset complete: {result.rowcount} applications updated")


async def main():
    """Run all validation tests"""
    print("\n" + "=" * 70)
    print("  FOLLOW-UP SYSTEM VALIDATION SCRIPT")
    print("  Testing automatic follow-up detection and scheduling")
    print("=" * 70)

    # Show current state
    await print_separator("Current Application State")
    await show_current_applications()

    # Test 1: Dry run (safe, no changes)
    dry_run_results = await test_followup_detection_dry_run()

    if dry_run_results['followups_needed'] > 0:
        # Show what would be updated
        print("\n" + "=" * 70)
        print("  Ready to proceed with live update?")
        print("=" * 70)
        print("\nThe following applications will be flagged:")
        for app in dry_run_results['applications_updated']:
            print(f"  - {app['company_name']}: {app['job_title']} ({app['days_since_application']} days)")

        # Test 2: Live update
        await test_followup_detection_live()

        # Test 3: Verify updates
        await verify_database_updates()

        # Test 4: Get pending follow-ups
        await test_get_pending_followups()
    else:
        print("\n" + "=" * 70)
        print("  No applications need follow-up at this time")
        print("=" * 70)
        print("\nPossible reasons:")
        print("  - All applications are < 7 days old")
        print("  - All applications already have followup_sent=True")
        print("  - All applications have received responses")
        print("\nTo test with fresh data, you can:")
        print("  1. Manually set some applied_date values to > 7 days ago")
        print("  2. Run this script's reset function: reset_followup_flags()")

    # Final summary
    print("\n" + "=" * 70)
    print("  VALIDATION COMPLETE")
    print("=" * 70)

    await print_separator("Final Application State")
    await show_current_applications()

    print("\n✅ Follow-up system validation completed successfully!")
    print("\nNext Steps:")
    print("  1. Review flagged applications above")
    print("  2. Implement actual email sending (currently just logs)")
    print("  3. Add to scheduler for automatic execution")
    print("  4. Create API endpoint for manual triggering")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
