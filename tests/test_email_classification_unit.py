"""
Unit tests for email classification logic - isolated from Gmail API
Tests only the classification algorithm without external dependencies
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.models import ResponseType


# Extract classification logic to test in isolation
def classify_email_content(subject, body):
    """
    Isolated classification logic from EmailAutomationService._classify_email
    This is a pure function that can be tested without mocking
    """
    combined_text = (subject + ' ' + body).lower()

    classification = {
        'type': ResponseType.OTHER,
        'confidence': 0.0,
        'action_required': False,
        'keywords_found': []
    }

    # Interview indicators
    interview_keywords = [
        'interview', 'phone screen', 'video call', 'meet with',
        'schedule', 'availability', 'calendar', 'zoom', 'teams',
        'next steps', 'speak with you', 'conversation', 'discuss'
    ]

    # Rejection indicators
    rejection_keywords = [
        'unfortunately', 'not selected', 'other candidates',
        'not moving forward', 'pursue other', 'decided to go',
        'position has been filled', 'no longer available',
        'thank you for your interest', 'best of luck', 'future opportunities'
    ]

    # Info request indicators
    info_keywords = [
        'additional information', 'please provide', 'could you send',
        'need more details', 'clarification', 'confirm', 'verify'
    ]

    # Offer indicators
    offer_keywords = [
        'offer', 'compensation', 'salary', 'benefits', 'start date',
        'pleased to offer', 'congratulations', 'welcome to'
    ]

    # Score each category
    scores = {}

    # Interview scoring
    interview_score = sum(1 for kw in interview_keywords if kw in combined_text)
    scores['interview'] = interview_score / len(interview_keywords)

    # Rejection scoring
    rejection_score = sum(1 for kw in rejection_keywords if kw in combined_text)
    scores['rejection'] = rejection_score / len(rejection_keywords)

    # Info request scoring
    info_score = sum(1 for kw in info_keywords if kw in combined_text)
    scores['info'] = info_score / len(info_keywords)

    # Offer scoring
    offer_score = sum(1 for kw in offer_keywords if kw in combined_text)
    scores['offer'] = offer_score / len(offer_keywords)

    # Determine classification based on highest score
    if scores['offer'] > 0.2:
        classification['type'] = ResponseType.OFFER
        classification['confidence'] = scores['offer']
        classification['action_required'] = True
    elif scores['interview'] > 0.15:
        classification['type'] = ResponseType.INTERVIEW
        classification['confidence'] = scores['interview']
        classification['action_required'] = True
    elif scores['rejection'] > 0.2:
        classification['type'] = ResponseType.REJECTION
        classification['confidence'] = scores['rejection']
        classification['action_required'] = False
    elif scores['info'] > 0.15:
        classification['type'] = ResponseType.INFO_REQUEST
        classification['confidence'] = scores['info']
        classification['action_required'] = True

    return classification


# ============================================================================
# TEST CASES
# ============================================================================

def test_interview_classification_with_zoom():
    """Test Case 1: Interview with Zoom keyword"""
    subject = "Interview Invitation - Software Engineer Position"
    body = """
    Hi Matthew,

    Thank you for applying. We would like to schedule an interview with you
    to discuss the opportunity further. Please let us know your availability
    for a Zoom call next week.

    Best regards,
    Hiring Team
    """

    result = classify_email_content(subject, body)

    assert result['type'] == ResponseType.INTERVIEW, \
        f"Expected INTERVIEW, got {result['type']}"
    assert result['confidence'] > 0.15, \
        f"Interview confidence {result['confidence']} should be > 0.15"
    assert result['action_required'] is True, \
        "Interview should require action"

    print("✅ test_interview_classification_with_zoom")


def test_rejection_classification_standard():
    """Test Case 2: Standard rejection email"""
    subject = "Thank you for your application"
    body = """
    Dear Matthew,

    Thank you for your interest in the Data Analyst position. After careful
    consideration, we have decided to move forward with other candidates whose
    qualifications more closely match our current needs.

    We wish you the best of luck in your job search.

    Best regards,
    HR Team
    """

    result = classify_email_content(subject, body)

    assert result['type'] == ResponseType.REJECTION, \
        f"Expected REJECTION, got {result['type']}"
    assert result['confidence'] > 0.20, \
        f"Rejection confidence {result['confidence']} should be > 0.20"
    assert result['action_required'] is False, \
        "Rejection should not require action"

    print("✅ test_rejection_classification_standard")


def test_offer_classification_with_salary():
    """Test Case 3: Job offer with salary details"""
    subject = "Job Offer - Senior Data Analyst"
    body = """
    Congratulations Matthew!

    We are pleased to offer you the position of Senior Data Analyst.
    Your starting salary will be $95,000 per year, with full benefits.

    Your start date is scheduled for November 1st. Please review the attached
    offer letter and let us know your decision.

    Welcome to the team!
    """

    result = classify_email_content(subject, body)

    assert result['type'] == ResponseType.OFFER, \
        f"Expected OFFER, got {result['type']}"
    assert result['confidence'] > 0.20, \
        f"Offer confidence {result['confidence']} should be > 0.20"
    assert result['action_required'] is True, \
        "Offer should require action"

    print("✅ test_offer_classification_with_salary")


def test_info_request_classification():
    """Test Case 4: Request for additional information"""
    subject = "Additional Information Needed"
    body = """
    Hi Matthew,

    Before we can proceed, we need some additional information:

    1. Please provide references from your previous employers
    2. Could you send us your portfolio?
    3. We need verification of your degree

    Please send these materials at your earliest convenience.
    """

    result = classify_email_content(subject, body)

    assert result['type'] == ResponseType.INFO_REQUEST, \
        f"Expected INFO_REQUEST, got {result['type']}"
    assert result['action_required'] is True, \
        "Info request should require action"

    print("✅ test_info_request_classification")


def test_case_insensitive_classification():
    """Test Case 5: Case insensitivity"""
    subject = "INTERVIEW INVITATION"
    body = "WE WOULD LIKE TO SCHEDULE A VIDEO CALL WITH YOU"

    result = classify_email_content(subject, body)

    assert result['type'] == ResponseType.INTERVIEW, \
        f"Expected INTERVIEW (case-insensitive), got {result['type']}"

    print("✅ test_case_insensitive_classification")


def test_rejection_with_future_opportunities():
    """Test Case 6: Rejection with future opportunities mention"""
    subject = "Application Status Update"
    body = """
    Unfortunately, we will not be moving forward with your application
    at this time. However, we will keep your resume on file for future
    opportunities that may be a better fit.
    """

    result = classify_email_content(subject, body)

    assert result['type'] == ResponseType.REJECTION, \
        f"Expected REJECTION, got {result['type']}"

    print("✅ test_rejection_with_future_opportunities")


def test_interview_with_multiple_keywords():
    """Test Case 7: Interview with multiple strong signals"""
    subject = "Next Steps - Interview Scheduling"
    body = """
    We would like to discuss your application further. Please share your
    availability for a conversation with our team. We can schedule either
    a phone screen or video call, whichever works best for you.
    """

    result = classify_email_content(subject, body)

    assert result['type'] == ResponseType.INTERVIEW, \
        f"Expected INTERVIEW, got {result['type']}"
    assert result['confidence'] > 0.15, \
        "Multiple keywords should increase confidence"

    print("✅ test_interview_with_multiple_keywords")


def test_other_classification_for_generic_email():
    """Test Case 8: Generic email with no strong signals"""
    subject = "Application Received"
    body = "Thank you for your application. We have received it."

    result = classify_email_content(subject, body)

    assert result['type'] == ResponseType.OTHER, \
        f"Expected OTHER for generic email, got {result['type']}"
    assert result['action_required'] is False, \
        "Generic email should not require action"

    print("✅ test_other_classification_for_generic_email")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all unit tests"""
    print("=" * 70)
    print("Email Classification Unit Tests")
    print("=" * 70)

    tests = [
        test_interview_classification_with_zoom,
        test_rejection_classification_standard,
        test_offer_classification_with_salary,
        test_info_request_classification,
        test_case_insensitive_classification,
        test_rejection_with_future_opportunities,
        test_interview_with_multiple_keywords,
        test_other_classification_for_generic_email,
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
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed > 0:
        print("\nFAILURES:")
        for test_name, error in errors:
            print(f"  {test_name}: {error}")
        return 1

    print("\n🎉 All tests passed!")
    return 0


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
