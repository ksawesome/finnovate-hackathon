"""Test which report modules can be imported."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing report imports...")
print("=" * 60)

reports_to_test = [
    ("executive_summary_report", "ExecutiveSummaryReport"),
    ("status_report", "GLAccountStatusReport"),
    ("variance_report", "VarianceAnalysisReport"),
    ("hygiene_report", "GLHygieneDashboardReport"),
    ("reviewer_performance_report", "ReviewerPerformanceReport"),
    ("sla_compliance_report", "SLAComplianceReport"),
]

successful = []
failed = []

for module_name, class_name in reports_to_test:
    try:
        exec(f"from src.reports.{module_name} import {class_name}")
        print(f"✓ {module_name}")
        successful.append(module_name)
    except Exception as e:
        print(f"✗ {module_name}: {e}")
        failed.append((module_name, str(e)))

print("\n" + "=" * 60)
print(f"Results: {len(successful)}/{len(reports_to_test)} successful")

if failed:
    print("\nFailed imports:")
    for module_name, error in failed:
        print(f"  - {module_name}: {error}")

# Now check registered reports
print("\n" + "=" * 60)
from src.reports import REPORT_TYPES

print(f"Registered report types: {list(REPORT_TYPES.keys())}")
