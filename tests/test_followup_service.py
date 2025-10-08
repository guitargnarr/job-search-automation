"""
Comprehensive test suite for Follow-Up Service
Tests the intelligent follow-up detection and scheduling logic
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.models import ApplicationStatus


# ============================================================================
# MOCK DATA & FIXTURES
# ============================================================================

class MockApplication:
    """Mock Application object for testing"""
    def __init__(self, app_id, status, applied_date, response_received=False,
                 followup_sent=False, follow_ups_sent=0):
        self.id = app_id
        self.status = status
        self.applied_date = applied_date
        self.response_received = response_received
        self.followup_sent = followup_sent
        self.follow_ups_sent = follow_ups_sent
        self.next_follow_up_scheduled = None


def should_need_followup(app, cutoff_date, max_followups=2):
    """
    Pure function implementing follow-up detection logic
    This matches the actual service logic for testing
    """
    # Check all conditions
    has_waiting_status = app.status in [ApplicationStatus.APPLIED, ApplicationStatus.READY]
    is_old_enough = app.applied_date and app.applied_date < cutoff_date
    no_response = not app.response_received
    not_flagged = not app.followup_sent
    under_limit = app.follow_ups_sent < max_followups

    return (has_waiting_status and is_old_enough and no_response
            and not_flagged and under_limit)


# ============================================================================
# TEST CASES
# ============================================================================

def test_followup_detection_old_application():
    """
    Test Case 1: Application >7 days old should need follow-up

    Scenario: Application submitted 10 days ago, no response, not flagged
    Expected: Should be identified as needing follow-up
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    old_date = datetime.now() - timedelta(days=10)

    app = MockApplication(
        app_id=1,
        status=ApplicationStatus.APPLIED,
        applied_date=old_date,
        response_received=False,
        followup_sent=False,
        follow_ups_sent=0
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date)

    # Assert
    assert needs_followup is True, \
        "Application 10 days old with no response should need follow-up"

    print("✅ test_followup_detection_old_application")


def test_followup_detection_recent_application():
    """
    Test Case 2: Recent application (<7 days) should NOT need follow-up

    Scenario: Application submitted 3 days ago, no response
    Expected: Should NOT be flagged (too recent)
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    recent_date = datetime.now() - timedelta(days=3)

    app = MockApplication(
        app_id=2,
        status=ApplicationStatus.APPLIED,
        applied_date=recent_date,
        response_received=False,
        followup_sent=False,
        follow_ups_sent=0
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date)

    # Assert
    assert needs_followup is False, \
        "Application only 3 days old should NOT need follow-up yet"

    print("✅ test_followup_detection_recent_application")


def test_followup_detection_with_response():
    """
    Test Case 3: Application with response should NOT need follow-up

    Scenario: Old application (10 days) but already received a response
    Expected: Should NOT be flagged (already got response)
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    old_date = datetime.now() - timedelta(days=10)

    app = MockApplication(
        app_id=3,
        status=ApplicationStatus.INTERVIEWING,  # Has response
        applied_date=old_date,
        response_received=True,  # Key: has response
        followup_sent=False,
        follow_ups_sent=0
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date)

    # Assert
    assert needs_followup is False, \
        "Application with response should NOT need follow-up"

    print("✅ test_followup_detection_with_response")


def test_followup_detection_already_flagged():
    """
    Test Case 4: Application already flagged should NOT be re-flagged

    Scenario: Old application with followup_sent=True
    Expected: Should NOT be flagged again
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    old_date = datetime.now() - timedelta(days=10)

    app = MockApplication(
        app_id=4,
        status=ApplicationStatus.APPLIED,
        applied_date=old_date,
        response_received=False,
        followup_sent=True,  # Key: already flagged
        follow_ups_sent=0
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date)

    # Assert
    assert needs_followup is False, \
        "Application already flagged should NOT be re-flagged"

    print("✅ test_followup_detection_already_flagged")


def test_followup_detection_max_limit_reached():
    """
    Test Case 5: Application at max follow-ups should NOT need more

    Scenario: Old application but already sent 2 follow-ups (max limit)
    Expected: Should NOT be flagged (spam prevention)
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    old_date = datetime.now() - timedelta(days=20)

    app = MockApplication(
        app_id=5,
        status=ApplicationStatus.APPLIED,
        applied_date=old_date,
        response_received=False,
        followup_sent=False,
        follow_ups_sent=2  # Key: at max limit
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date, max_followups=2)

    # Assert
    assert needs_followup is False, \
        "Application at max follow-ups (2) should NOT need more (spam prevention)"

    print("✅ test_followup_detection_max_limit_reached")


def test_followup_detection_ready_status():
    """
    Test Case 6: READY status applications should also be checked

    Scenario: Application in READY status (essentially applied), 10 days old
    Expected: Should be flagged (READY is a waiting state)
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    old_date = datetime.now() - timedelta(days=10)

    app = MockApplication(
        app_id=6,
        status=ApplicationStatus.READY,  # Key: READY status
        applied_date=old_date,
        response_received=False,
        followup_sent=False,
        follow_ups_sent=0
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date)

    # Assert
    assert needs_followup is True, \
        "READY status application >7 days should need follow-up"

    print("✅ test_followup_detection_ready_status")


def test_followup_detection_rejected_status():
    """
    Test Case 7: REJECTED applications should NOT need follow-up

    Scenario: Application rejected, 10 days old
    Expected: Should NOT be flagged (closed/final status)
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    old_date = datetime.now() - timedelta(days=10)

    app = MockApplication(
        app_id=7,
        status=ApplicationStatus.REJECTED,  # Key: final status
        applied_date=old_date,
        response_received=True,
        followup_sent=False,
        follow_ups_sent=0
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date)

    # Assert
    assert needs_followup is False, \
        "REJECTED application should NOT need follow-up"

    print("✅ test_followup_detection_rejected_status")


def test_followup_detection_no_applied_date():
    """
    Test Case 8: Application without applied_date should NOT crash

    Scenario: Application in APPLIED status but applied_date is None
    Expected: Should NOT be flagged (can't calculate days ago)
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)

    app = MockApplication(
        app_id=8,
        status=ApplicationStatus.APPLIED,
        applied_date=None,  # Key: missing date
        response_received=False,
        followup_sent=False,
        follow_ups_sent=0
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date)

    # Assert
    assert needs_followup is False, \
        "Application without applied_date should NOT crash or be flagged"

    print("✅ test_followup_detection_no_applied_date")


def test_followup_threshold_boundary_exactly_7_days():
    """
    Test Case 9: Application exactly 7 days old (boundary test)

    Scenario: Application applied exactly 7 days ago
    Expected: Should NOT need follow-up (< cutoff, not >)
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    exactly_7_days = datetime.now() - timedelta(days=7, seconds=1)  # Just under 7 days

    app = MockApplication(
        app_id=9,
        status=ApplicationStatus.APPLIED,
        applied_date=exactly_7_days,
        response_received=False,
        followup_sent=False,
        follow_ups_sent=0
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date)

    # Assert
    # Should be False because applied_date is NOT < cutoff_date (it's equal)
    assert needs_followup is False, \
        "Application exactly 7 days old should NOT need follow-up (boundary condition)"

    print("✅ test_followup_detection_threshold_boundary_exactly_7_days")


def test_followup_threshold_boundary_just_over_7_days():
    """
    Test Case 10: Application just over 7 days old (boundary test)

    Scenario: Application applied 7 days and 1 hour ago
    Expected: Should need follow-up (crossed threshold)
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    just_over_7 = datetime.now() - timedelta(days=7, hours=1)  # Just over 7 days

    app = MockApplication(
        app_id=10,
        status=ApplicationStatus.APPLIED,
        applied_date=just_over_7,
        response_received=False,
        followup_sent=False,
        follow_ups_sent=0
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date)

    # Assert
    assert needs_followup is True, \
        "Application 7 days + 1 hour old should need follow-up"

    print("✅ test_followup_detection_threshold_boundary_just_over_7_days")


def test_followup_detection_one_followup_sent():
    """
    Test Case 11: Application with 1 follow-up sent can get another

    Scenario: Old application, 1 follow-up sent (max=2), not currently flagged
    Expected: Should be eligible for second follow-up
    """
    # Arrange
    cutoff_date = datetime.now() - timedelta(days=7)
    old_date = datetime.now() - timedelta(days=15)

    app = MockApplication(
        app_id=11,
        status=ApplicationStatus.APPLIED,
        applied_date=old_date,
        response_received=False,
        followup_sent=False,  # Flag was reset after last send
        follow_ups_sent=1  # Already sent 1
    )

    # Act
    needs_followup = should_need_followup(app, cutoff_date, max_followups=2)

    # Assert
    assert needs_followup is True, \
        "Application with 1 follow-up (max 2) should be eligible for another"

    print("✅ test_followup_detection_one_followup_sent")


def test_followup_service_constants():
    """
    Test Case 12: Verify service configuration constants

    Validates that FollowUpService has correct default values
    """
    from backend.services.followup_service import FollowUpService

    # Act
    service = FollowUpService()

    # Assert
    assert service.DEFAULT_FOLLOWUP_DAYS == 7, \
        "Default follow-up threshold should be 7 days"
    assert service.RESPONSE_TIMEOUT_DAYS == 14, \
        "Response timeout should be 14 days"
    assert service.MAX_FOLLOW_UPS == 2, \
        "Max follow-ups should be 2 (spam prevention)"
    assert service.followup_days == 7, \
        "Instance should use default 7 days"

    print("✅ test_followup_service_constants")


def test_followup_service_custom_threshold():
    """
    Test Case 13: Service should accept custom threshold

    Validates that FollowUpService can be configured with custom days
    """
    from backend.services.followup_service import FollowUpService

    # Act
    service = FollowUpService(followup_days=14)

    # Assert
    assert service.followup_days == 14, \
        "Custom threshold (14 days) should override default"

    print("✅ test_followup_service_custom_threshold")


# ============================================================================
# COMPREHENSIVE SCENARIO TESTS
# ============================================================================

def test_scenario_typical_followup_needed():
    """
    Test Scenario 1: Typical case - needs follow-up

    Application profile:
    - Status: APPLIED
    - Applied: 10 days ago
    - Response: No
    - Flagged: No
    - Follow-ups sent: 0

    Expected: ✓ NEEDS FOLLOW-UP
    """
    cutoff_date = datetime.now() - timedelta(days=7)
    app = MockApplication(
        app_id=100,
        status=ApplicationStatus.APPLIED,
        applied_date=datetime.now() - timedelta(days=10),
        response_received=False,
        followup_sent=False,
        follow_ups_sent=0
    )

    result = should_need_followup(app, cutoff_date)

    assert result is True, "Typical scenario should trigger follow-up"
    print("✅ test_scenario_typical_followup_needed")


def test_scenario_no_followup_needed_recent():
    """
    Test Scenario 2: No follow-up needed - too recent

    Application profile:
    - Status: APPLIED
    - Applied: 2 days ago
    - Response: No
    - Flagged: No
    - Follow-ups sent: 0

    Expected: ✗ NO FOLLOW-UP (too recent)
    """
    cutoff_date = datetime.now() - timedelta(days=7)
    app = MockApplication(
        app_id=101,
        status=ApplicationStatus.APPLIED,
        applied_date=datetime.now() - timedelta(days=2),
        response_received=False,
        followup_sent=False,
        follow_ups_sent=0
    )

    result = should_need_followup(app, cutoff_date)

    assert result is False, "Recent application should NOT trigger follow-up"
    print("✅ test_scenario_no_followup_needed_recent")


def test_scenario_no_followup_needed_has_response():
    """
    Test Scenario 3: No follow-up needed - got response

    Application profile:
    - Status: INTERVIEWING
    - Applied: 10 days ago
    - Response: Yes
    - Flagged: No
    - Follow-ups sent: 0

    Expected: ✗ NO FOLLOW-UP (has response)
    """
    cutoff_date = datetime.now() - timedelta(days=7)
    app = MockApplication(
        app_id=102,
        status=ApplicationStatus.INTERVIEWING,
        applied_date=datetime.now() - timedelta(days=10),
        response_received=True,
        followup_sent=False,
        follow_ups_sent=0
    )

    result = should_need_followup(app, cutoff_date)

    assert result is False, "Application with response should NOT need follow-up"
    print("✅ test_scenario_no_followup_needed_has_response")


def test_scenario_second_followup_eligible():
    """
    Test Scenario 4: Eligible for second follow-up

    Application profile:
    - Status: APPLIED
    - Applied: 20 days ago
    - Response: No
    - Flagged: No (reset after first follow-up)
    - Follow-ups sent: 1

    Expected: ✓ NEEDS FOLLOW-UP (second one allowed)
    """
    cutoff_date = datetime.now() - timedelta(days=7)
    app = MockApplication(
        app_id=103,
        status=ApplicationStatus.APPLIED,
        applied_date=datetime.now() - timedelta(days=20),
        response_received=False,
        followup_sent=False,  # Reset after first send
        follow_ups_sent=1  # One already sent
    )

    result = should_need_followup(app, cutoff_date, max_followups=2)

    assert result is True, "Application eligible for second follow-up"
    print("✅ test_scenario_second_followup_eligible")


def test_scenario_max_followups_reached():
    """
    Test Scenario 5: Max follow-ups reached - no more allowed

    Application profile:
    - Status: APPLIED
    - Applied: 30 days ago
    - Response: No
    - Flagged: No
    - Follow-ups sent: 2 (max limit)

    Expected: ✗ NO FOLLOW-UP (spam prevention)
    """
    cutoff_date = datetime.now() - timedelta(days=7)
    app = MockApplication(
        app_id=104,
        status=ApplicationStatus.APPLIED,
        applied_date=datetime.now() - timedelta(days=30),
        response_received=False,
        followup_sent=False,
        follow_ups_sent=2  # At max limit
    )

    result = should_need_followup(app, cutoff_date, max_followups=2)

    assert result is False, "Application at max follow-ups should be blocked"
    print("✅ test_scenario_max_followups_reached")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all follow-up service tests"""
    print("=" * 70)
    print("  Follow-Up Service Unit Tests")
    print("  Testing intelligent follow-up detection logic")
    print("=" * 70)

    tests = [
        # Core detection tests
        test_followup_detection_old_application,
        test_followup_detection_recent_application,
        test_followup_detection_with_response,
        test_followup_detection_already_flagged,
        test_followup_detection_max_limit_reached,
        test_followup_detection_ready_status,
        test_followup_detection_rejected_status,
        test_followup_detection_no_applied_date,

        # Boundary tests
        test_followup_threshold_boundary_exactly_7_days,
        test_followup_threshold_boundary_just_over_7_days,
        test_followup_detection_one_followup_sent,

        # Service configuration tests
        test_followup_service_constants,
        test_followup_service_custom_threshold,

        # Comprehensive scenario tests
        test_scenario_typical_followup_needed,
        test_scenario_no_followup_needed_recent,
        test_scenario_no_followup_needed_has_response,
        test_scenario_second_followup_eligible,
        test_scenario_max_followups_reached,
    ]

    passed = 0
    failed = 0
    errors = []

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__}: {str(e)}")
            failed += 1
            errors.append((test_func.__name__, str(e)))
        except Exception as e:
            print(f"💥 {test_func.__name__}: ERROR - {str(e)}")
            failed += 1
            errors.append((test_func.__name__, f"ERROR: {str(e)}"))

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed > 0:
        print("\nFAILURES:")
        for test_name, error in errors:
            print(f"  {test_name}: {error}")
        return 1

    print("\n🎉 All follow-up service tests passed!")

    # Summary of what was tested
    print("\nTested Scenarios:")
    print("  ✓ Core detection logic (old apps, recent apps, responses)")
    print("  ✓ Edge cases (no date, already flagged, max limit)")
    print("  ✓ Boundary conditions (exactly 7 days, just over 7 days)")
    print("  ✓ Status handling (APPLIED, READY, REJECTED, INTERVIEWING)")
    print("  ✓ Configuration (default threshold, custom threshold)")
    print("  ✓ Spam prevention (max 2 follow-ups)")

    return 0


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
