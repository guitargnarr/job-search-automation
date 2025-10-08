#!/usr/bin/env python3
"""
Simple test runner for Job Search Automation Platform
Runs tests without requiring pytest installation
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import test classes
from tests.test_email_service import (
    TestEmailClassification,
    TestEmailParsing,
    TestCompanyExtraction,
    TestClassificationEdgeCases
)

def run_test_class(test_class, class_name):
    """Run all tests in a test class"""
    print(f"\n{'='*70}")
    print(f"Running {class_name}")
    print('='*70)

    instance = test_class()
    instance.setup_method()

    test_methods = [m for m in dir(test_class) if m.startswith('test_')]
    passed = 0
    failed = 0
    errors = []

    for method_name in test_methods:
        try:
            method = getattr(instance, method_name)
            method()
            print(f"✅ {method_name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {method_name}: {str(e)}")
            failed += 1
            errors.append((method_name, str(e)))
        except Exception as e:
            print(f"💥 {method_name}: ERROR - {type(e).__name__}: {str(e)}")
            failed += 1
            errors.append((method_name, f"ERROR: {type(e).__name__}: {str(e)}"))

    return passed, failed, errors

def main():
    """Run all test classes"""
    print("="*70)
    print("Job Search Automation Platform - Test Suite")
    print("="*70)

    test_classes = [
        (TestEmailClassification, "TestEmailClassification"),
        (TestEmailParsing, "TestEmailParsing"),
        (TestCompanyExtraction, "TestCompanyExtraction"),
        (TestClassificationEdgeCases, "TestClassificationEdgeCases"),
    ]

    total_passed = 0
    total_failed = 0
    all_errors = []

    for test_class, class_name in test_classes:
        passed, failed, errors = run_test_class(test_class, class_name)
        total_passed += passed
        total_failed += failed
        all_errors.extend(errors)

    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print('='*70)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📊 Total:  {total_passed + total_failed}")

    if total_failed > 0:
        print(f"\n{'='*70}")
        print("FAILURES")
        print('='*70)
        for test_name, error in all_errors:
            print(f"\n{test_name}:")
            print(f"  {error}")

    # Exit code
    sys.exit(0 if total_failed == 0 else 1)

if __name__ == "__main__":
    main()
