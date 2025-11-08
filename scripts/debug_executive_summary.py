"""Debug executive summary data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analytics import (
    calculate_gl_hygiene_score,
    calculate_review_status_summary,
    perform_analytics,
)
from src.insights import generate_executive_summary, generate_proactive_insights

entity = "AEML"
period = "Mar-24"

print("=" * 60)
print("DEBUGGING EXECUTIVE SUMMARY DATA")
print("=" * 60)

print("\n1. Analytics Data:")
try:
    analytics = perform_analytics(entity, period)
    print(f"   Keys: {list(analytics.keys())}")
    print(f"   Total Balance: {analytics.get('total_balance', 'N/A')}")
    print(f"   Account Count: {analytics.get('account_count', 'N/A')}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n2. Hygiene Score:")
try:
    hygiene = calculate_gl_hygiene_score(entity, period)
    print(f"   Overall Score: {hygiene.get('overall_score', 'N/A')}")
    print(f"   Grade: {hygiene.get('grade', 'N/A')}")
    print(f"   Components: {list(hygiene.get('components', {}).keys())}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n3. Review Status:")
try:
    review_status = calculate_review_status_summary(entity, period)
    print(f"   Keys: {list(review_status.keys())}")
    if "overall" in review_status:
        print(f"   Completion: {review_status['overall'].get('completion_pct', 'N/A')}%")
        print(f"   Pending: {review_status['overall'].get('pending', 'N/A')}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n4. Executive Summary:")
try:
    exec_summary = generate_executive_summary(entity, period)
    print(f"   Keys: {list(exec_summary.keys())}")
    print(f"   Highlights: {len(exec_summary.get('highlights', []))} items")
    print(f"   Concerns: {len(exec_summary.get('concerns', []))} items")
    if exec_summary.get("highlights"):
        print(f"   First highlight: {exec_summary['highlights'][0][:80]}...")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n5. Proactive Insights:")
try:
    insights = generate_proactive_insights(entity, period)
    print(f"   Count: {len(insights)} insights")
    if insights:
        print(f"   First insight: {insights[0].get('title', 'N/A')}")
        print(f"   Priority: {insights[0].get('priority', 'N/A')}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
