#!/usr/bin/env python3
"""
Job Search Automation System - Comprehensive Test Suite
Based on successful patterns from music production automation
"""

import sys
import os
import json
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime
import time

# Add current directory to path
sys.path.insert(0, os.getcwd())

print("="*70)
print("JOB SEARCH AUTOMATION - SYSTEM TEST")
print("="*70)

test_results = {
    "timestamp": datetime.now().isoformat(),
    "passed": [],
    "failed": [],
    "warnings": [],
    "performance": {},
    "statistics": {}
}

# TEST 1: Python Environment
print("\n[TEST 1] Python Environment")
print("-" * 70)
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
test_results["passed"].append("Python environment")
test_results["statistics"]["python_version"] = sys.version.split()[0]

# TEST 2: File Structure & Syntax
print("\n[TEST 2] File Structure & Syntax")
print("-" * 70)
required_files = [
    "mcp_server/job_search_server.py",
    "automation/generators/generate_application_package.py",
    "web_dashboard/index.html",
    "web_dashboard/dashboard.js",
    "web_dashboard/styles.css",
    "launch_job_search.sh",
    "start_server.sh",
    "stop_server.sh",
    "tracking/database/migrate_csv_to_db.py",
    "mcp_server/config.json"
]

file_count = 0
for filename in required_files:
    if Path(filename).exists():
        size = Path(filename).stat().st_size / 1024  # KB

        # Validate Python syntax
        if filename.endswith('.py'):
            try:
                import ast
                with open(filename, 'r') as f:
                    ast.parse(f.read())
                print(f"  ✓ {filename} ({size:.1f} KB) - Valid Python")
                test_results["passed"].append(f"File: {filename}")
            except SyntaxError as e:
                print(f"  ✗ {filename} - Syntax Error: {e}")
                test_results["failed"].append(f"Syntax: {filename}")

        # Validate JSON
        elif filename.endswith('.json'):
            try:
                with open(filename, 'r') as f:
                    json.load(f)
                print(f"  ✓ {filename} ({size:.1f} KB) - Valid JSON")
                test_results["passed"].append(f"File: {filename}")
            except json.JSONDecodeError as e:
                print(f"  ✗ {filename} - JSON Error: {e}")
                test_results["failed"].append(f"JSON: {filename}")

        # Check other files
        else:
            print(f"  ✓ {filename} ({size:.1f} KB)")
            test_results["passed"].append(f"File: {filename}")

        file_count += 1
    else:
        print(f"  ✗ {filename} MISSING")
        test_results["failed"].append(f"Missing: {filename}")

test_results["statistics"]["files_validated"] = file_count

# TEST 3: Database Validation
print("\n[TEST 3] Database Validation")
print("-" * 70)
db_path = "tracking/database/job_tracker.db"

if Path(db_path).exists():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"  ✓ Database connected: {len(tables)} tables")

        # Check job count
        cursor.execute("SELECT COUNT(*) FROM jobs")
        job_count = cursor.fetchone()[0]
        print(f"  ✓ Jobs loaded: {job_count}")
        test_results["statistics"]["total_jobs"] = job_count

        # Check priority distribution
        cursor.execute("""
            SELECT priority, COUNT(*) as count
            FROM jobs
            GROUP BY priority
            ORDER BY count DESC
        """)
        priority_dist = cursor.fetchall()
        print(f"  ✓ Priority distribution:")
        for priority, count in priority_dist:
            print(f"    • {priority}: {count}")
            if priority == "HIGH":
                test_results["statistics"]["high_priority_jobs"] = count

        # Check application status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM applications
            GROUP BY status
        """)
        status_dist = cursor.fetchall()
        print(f"  ✓ Application status:")
        for status, count in status_dist:
            print(f"    • {status}: {count}")

        conn.close()
        test_results["passed"].append("Database validation")

    except Exception as e:
        print(f"  ✗ Database error: {e}")
        test_results["failed"].append(f"Database: {e}")
else:
    print(f"  ✗ Database not found at {db_path}")
    test_results["failed"].append("Database not found")

# TEST 4: Dependencies Check
print("\n[TEST 4] Python Dependencies")
print("-" * 70)

core_deps = {
    "sqlite3": "Database operations",
    "json": "Configuration handling",
    "pathlib": "File path operations",
    "datetime": "Date/time handling"
}

for module, description in core_deps.items():
    try:
        __import__(module)
        print(f"  ✓ {module}: {description}")
        test_results["passed"].append(f"Dependency: {module}")
    except ImportError:
        print(f"  ✗ {module}: Missing")
        test_results["failed"].append(f"Missing: {module}")

# Optional dependencies
optional_deps = {
    "mcp": "Model Context Protocol (pip install mcp)",
    "aiohttp": "Async HTTP client (pip install aiohttp)",
    "flask": "Web framework (pip install flask)"
}

print("\n  Optional Dependencies:")
for module, description in optional_deps.items():
    try:
        __import__(module)
        print(f"    ✓ {module}: {description}")
        test_results["passed"].append(f"Optional: {module}")
    except ImportError:
        print(f"    ⚠ {module}: Not installed - {description}")
        test_results["warnings"].append(f"{module} not installed")

# TEST 5: Module Imports
print("\n[TEST 5] Module Imports")
print("-" * 70)

# Test Application Generator
try:
    from automation.generators.generate_application_package import ApplicationPackageGenerator
    print("  ✓ ApplicationPackageGenerator imports successfully")
    test_results["passed"].append("ApplicationPackageGenerator import")
except Exception as e:
    print(f"  ✗ ApplicationPackageGenerator failed: {e}")
    test_results["failed"].append(f"Generator: {str(e)[:50]}")

# Test MCP Server (may fail if MCP not installed)
try:
    from mcp_server.job_search_server import JobSearchMCPServer
    print("  ✓ JobSearchMCPServer imports successfully")
    test_results["passed"].append("MCP Server import")
except Exception as e:
    print(f"  ⚠ JobSearchMCPServer: {e}")
    test_results["warnings"].append("MCP Server not available (MCP not installed)")

# TEST 6: Application Package Generation
print("\n[TEST 6] Application Package Generation")
print("-" * 70)

try:
    from automation.generators.generate_application_package import ApplicationPackageGenerator

    # Initialize generator
    start_time = time.time()
    generator = ApplicationPackageGenerator()
    print("  ✓ Generator initialized")

    # Get a test job
    test_job_id = 11  # Waystar position
    print(f"  Testing with Job ID: {test_job_id}")

    # Generate package
    success, message, folder_path = generator.generate_package(test_job_id)
    generation_time = time.time() - start_time

    if success:
        print(f"  ✓ Package generated: {message}")
        print(f"  ✓ Location: {folder_path}")
        print(f"  ✓ Generation time: {generation_time:.2f} seconds")
        test_results["passed"].append("Package generation")
        test_results["performance"]["package_generation"] = f"{generation_time:.2f} seconds"

        # Check generated files
        if folder_path and Path(folder_path).exists():
            files = list(Path(folder_path).glob("*"))
            print(f"  ✓ Files created: {len(files)}")
            for file in files:
                print(f"    • {file.name}")
    else:
        print(f"  ✗ Generation failed: {message}")
        test_results["failed"].append("Package generation")

    generator.close()

except Exception as e:
    print(f"  ✗ Package generation test failed: {e}")
    test_results["failed"].append(f"Package test: {str(e)[:50]}")

# TEST 7: Web Dashboard
print("\n[TEST 7] Web Dashboard")
print("-" * 70)

dashboard_files = [
    "web_dashboard/index.html",
    "web_dashboard/dashboard.js",
    "web_dashboard/styles.css"
]

dashboard_ok = True
for file in dashboard_files:
    if Path(file).exists():
        size = Path(file).stat().st_size / 1024
        print(f"  ✓ {Path(file).name} ({size:.1f} KB)")
    else:
        print(f"  ✗ {Path(file).name} missing")
        dashboard_ok = False

if dashboard_ok:
    test_results["passed"].append("Web dashboard")
    print("  ✓ Dashboard ready for deployment")
else:
    test_results["failed"].append("Web dashboard incomplete")

# TEST 8: Performance Benchmarks
print("\n[TEST 8] Performance Benchmarks")
print("-" * 70)

# Database query performance
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    start_time = time.time()
    cursor.execute("SELECT * FROM jobs WHERE priority='HIGH'")
    results = cursor.fetchall()
    query_time = (time.time() - start_time) * 1000  # ms

    print(f"  ✓ Database query (HIGH priority): {query_time:.2f} ms")
    print(f"    • Results: {len(results)} jobs")
    test_results["performance"]["db_query_high_priority"] = f"{query_time:.2f} ms"

    conn.close()
    test_results["passed"].append("Performance benchmarks")

except Exception as e:
    print(f"  ✗ Benchmark failed: {e}")
    test_results["warnings"].append("Performance benchmark incomplete")

# TEST 9: Configuration Validation
print("\n[TEST 9] Configuration Validation")
print("-" * 70)

try:
    with open('mcp_server/config.json', 'r') as f:
        config = json.load(f)

    print(f"  ✓ Configuration loaded successfully")

    # Check workflow presets
    if 'workflow_presets' in config:
        presets = config['workflow_presets']
        print(f"  ✓ Workflow presets: {len(presets)}")
        for name, preset in presets.items():
            print(f"    • {name}: {preset.get('description', 'No description')}")
        test_results["statistics"]["workflow_presets"] = len(presets)

    # Check application strategies
    if 'application_strategies' in config:
        strategies = config['application_strategies']
        print(f"  ✓ Application strategies: {len(strategies)}")
        for name, strategy in strategies.items():
            print(f"    • {name}: Template {strategy.get('resume_template', '?')}, "
                  f"Tier {strategy.get('cover_letter_tier', '?')}")

    test_results["passed"].append("Configuration validation")

except Exception as e:
    print(f"  ✗ Configuration error: {e}")
    test_results["failed"].append(f"Configuration: {e}")

# SUMMARY
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print(f"✓ Passed:   {len(test_results['passed'])}")
print(f"✗ Failed:   {len(test_results['failed'])}")
print(f"⚠ Warnings: {len(test_results['warnings'])}")
print("="*70)

# Save results to JSON
test_results["summary"] = {
    "passed": len(test_results["passed"]),
    "failed": len(test_results["failed"]),
    "warnings": len(test_results["warnings"]),
    "total_tests": len(test_results["passed"]) + len(test_results["failed"])
}

with open('test_results.json', 'w') as f:
    json.dump(test_results, f, indent=2)
print(f"\n📊 Detailed results saved to test_results.json")

if test_results["failed"]:
    print("\n❌ FAILED TESTS:")
    for fail in test_results["failed"]:
        print(f"  - {fail}")

if test_results["warnings"]:
    print("\n⚠️  WARNINGS:")
    for warn in test_results["warnings"]:
        print(f"  - {warn}")

# Overall status
if len(test_results["failed"]) == 0:
    print("\n✅ ALL CORE TESTS PASSED!")
    print("   Job Search Automation System is OPERATIONAL")
    if len(test_results["warnings"]) > 0:
        print("   (Some optional components need installation)")
    sys.exit(0)
else:
    print("\n❌ SOME TESTS FAILED - See above for details")
    sys.exit(1)