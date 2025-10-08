#!/usr/bin/env python3
"""
Standalone Follow-Up Logic Tests
Pure logic tests with NO backend imports - prevents async hangs
Tests the business rules without any database/service dependencies
"""

from datetime import datetime, timedelta
from enum import Enum


# ============================================================================
# STANDALONE ENUMS (copied from models to avoid imports)
# ============================================================================

class ApplicationStatus(Enum):
    """Application status - standalone for testing"""
    DRAFT = "DRAFT"
    READY = "READY"
    APPLIED = "APPLIED"
    RESPONDED = "RESPONDED"
    INTERVIEWING = "INTERVIEWING"
    OFFERED = "OFFERED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


# ============================================================================
# MOCK APPLICATION CLASS
# ============================================================================

class MockApplication:
    """Mock Application for testing without database"""
    def __init__(self, app_id, status, applied_date, response_received=False,
                 followup_sent=False, follow_ups_sent=0):
        self.id = app_id
        self.status = status
        self.applied_date = applied_date
        self.response_received = response_received
        self.followup_sent = followup_sent
        self.follow_ups_sent = follow_ups_sent


# ============================================================================
# CORE BUSINESS LOGIC (extracted from service for testing)
# ============================================================================

def should_need_followup(app, cutoff_date, max_followups=2):
    """
    Follow-up detection logic - pure function
    Returns True if application needs follow-up
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

def test_old_application_needs_followup():
    """Test 1: 10-day old application should need follow-up"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(1, ApplicationStatus.APPLIED,
                          datetime.now() - timedelta(days=10))

    result = should_need_followup(app, cutoff)
    assert result is True, "10-day old APPLIED app should need follow-up"
    print("✅ Test 1: Old application needs follow-up")


def test_recent_application_no_followup():
    """Test 2: 3-day old application should NOT need follow-up"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(2, ApplicationStatus.APPLIED,
                          datetime.now() - timedelta(days=3))

    result = should_need_followup(app, cutoff)
    assert result is False, "3-day old app should NOT need follow-up"
    print("✅ Test 2: Recent application excluded")


def test_application_with_response_no_followup():
    """Test 3: Application with response should NOT need follow-up"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(3, ApplicationStatus.INTERVIEWING,
                          datetime.now() - timedelta(days=10),
                          response_received=True)

    result = should_need_followup(app, cutoff)
    assert result is False, "App with response should NOT need follow-up"
    print("✅ Test 3: Application with response excluded")


def test_already_flagged_no_duplicate():
    """Test 4: Already flagged application should NOT be re-flagged"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(4, ApplicationStatus.APPLIED,
                          datetime.now() - timedelta(days=10),
                          followup_sent=True)

    result = should_need_followup(app, cutoff)
    assert result is False, "Already flagged app should NOT be re-flagged"
    print("✅ Test 4: Already flagged excluded")


def test_max_followups_spam_prevention():
    """Test 5: Max follow-ups limit enforced"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(5, ApplicationStatus.APPLIED,
                          datetime.now() - timedelta(days=20),
                          follow_ups_sent=2)

    result = should_need_followup(app, cutoff, max_followups=2)
    assert result is False, "App at max follow-ups should be blocked"
    print("✅ Test 5: Max follow-ups limit enforced")


def test_ready_status_included():
    """Test 6: READY status should be checked"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(6, ApplicationStatus.READY,
                          datetime.now() - timedelta(days=10))

    result = should_need_followup(app, cutoff)
    assert result is True, "READY status should be included"
    print("✅ Test 6: READY status included")


def test_rejected_status_excluded():
    """Test 7: REJECTED status should be excluded"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(7, ApplicationStatus.REJECTED,
                          datetime.now() - timedelta(days=10))

    result = should_need_followup(app, cutoff)
    assert result is False, "REJECTED status should be excluded"
    print("✅ Test 7: REJECTED status excluded")


def test_no_applied_date_excluded():
    """Test 8: No applied_date should be excluded"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(8, ApplicationStatus.APPLIED, None)

    result = should_need_followup(app, cutoff)
    assert result is False, "App without date should be excluded"
    print("✅ Test 8: No applied_date excluded")


def test_boundary_exactly_7_days():
    """Test 9: Exactly 7 days (boundary test)"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(9, ApplicationStatus.APPLIED,
                          datetime.now() - timedelta(days=7, seconds=1))

    result = should_need_followup(app, cutoff)
    assert result is False, "Exactly 7 days should NOT trigger"
    print("✅ Test 9: Boundary - exactly 7 days excluded")


def test_boundary_just_over_7_days():
    """Test 10: Just over 7 days (boundary test)"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(10, ApplicationStatus.APPLIED,
                          datetime.now() - timedelta(days=7, hours=1))

    result = should_need_followup(app, cutoff)
    assert result is True, "7 days + 1 hour should trigger"
    print("✅ Test 10: Boundary - just over 7 days included")


def test_one_followup_sent_can_send_second():
    """Test 11: Can send second follow-up"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(11, ApplicationStatus.APPLIED,
                          datetime.now() - timedelta(days=15),
                          follow_ups_sent=1)

    result = should_need_followup(app, cutoff, max_followups=2)
    assert result is True, "Should allow second follow-up"
    print("✅ Test 11: Second follow-up allowed")


def test_custom_threshold_14_days():
    """Test 12: Custom threshold (14 days)"""
    cutoff = datetime.now() - timedelta(days=14)
    app = MockApplication(12, ApplicationStatus.APPLIED,
                          datetime.now() - timedelta(days=10))

    result = should_need_followup(app, cutoff)
    assert result is False, "10 days < 14 day threshold"
    print("✅ Test 12: Custom threshold respected")


# ============================================================================
# COMPREHENSIVE SCENARIOS
# ============================================================================

def test_scenario_typical():
    """Scenario: Typical follow-up needed"""
    cutoff = datetime.now() - timedelta(days=7)
    app = MockApplication(100, ApplicationStatus.APPLIED,
                          datetime.now() - timedelta(days=10),
                          response_received=False, followup_sent=False, follow_ups_sent=0)

    result = should_need_followup(app, cutoff)
    assert result is True
    print("✅ Scenario 1: Typical case - needs follow-up")


def test_scenario_all_conditions_fail():
    """Scenario: All conditions preventing follow-up"""
    cutoff = datetime.now() - timedelta(days=7)

    # Wrong status
    app1 = MockApplication(101, ApplicationStatus.REJECTED,
                           datetime.now() - timedelta(days=10))
    assert should_need_followup(app1, cutoff) is False

    # Too recent
    app2 = MockApplication(102, ApplicationStatus.APPLIED,
                           datetime.now() - timedelta(days=3))
    assert should_need_followup(app2, cutoff) is False

    # Has response
    app3 = MockApplication(103, ApplicationStatus.APPLIED,
                           datetime.now() - timedelta(days=10),
                           response_received=True)
    assert should_need_followup(app3, cutoff) is False

    # Already flagged
    app4 = MockApplication(104, ApplicationStatus.APPLIED,
                           datetime.now() - timedelta(days=10),
                           followup_sent=True)
    assert should_need_followup(app4, cutoff) is False

    # Max limit
    app5 = MockApplication(105, ApplicationStatus.APPLIED,
                           datetime.now() - timedelta(days=10),
                           follow_ups_sent=2)
    assert should_need_followup(app5, cutoff) is False

    print("✅ Scenario 2: All exclusion conditions work")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Execute all test cases"""
    print("=" * 70)
    print("  FOLLOW-UP SERVICE UNIT TESTS")
    print("  Pure logic tests - NO database, NO emails, NO external dependencies")
    print("=" * 70)

    tests = [
        test_old_application_needs_followup,
        test_recent_application_no_followup,
        test_application_with_response_no_followup,
        test_already_flagged_no_duplicate,
        test_max_followups_spam_prevention,
        test_ready_status_included,
        test_rejected_status_excluded,
        test_no_applied_date_excluded,
        test_boundary_exactly_7_days,
        test_boundary_just_over_7_days,
        test_one_followup_sent_can_send_second,
        test_custom_threshold_14_days,
        test_scenario_typical,
        test_scenario_all_conditions_fail,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__}: ERROR - {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("  TEST RESULTS")
    print("=" * 70)
    print(f"✅ PASSED: {passed}/{len(tests)}")
    print(f"❌ FAILED: {failed}/{len(tests)}")

    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED - Follow-up logic validated!")
        print("\nValidated:")
        print("  ✓ 7-day threshold detection")
        print("  ✓ Status filtering (APPLIED/READY only)")
        print("  ✓ Response checking (exclude if received)")
        print("  ✓ Duplicate prevention (followup_sent flag)")
        print("  ✓ Spam prevention (max 2 follow-ups)")
        print("  ✓ Boundary conditions (exactly 7 days vs >7 days)")
        print("  ✓ Edge cases (no date, rejected status)")
        print("\n✅ CONSTRAINT: NO EMAILS SENT - Pure logic tests only")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = run_all_tests()
    sys.exit(exit_code)
