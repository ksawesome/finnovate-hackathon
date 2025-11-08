"""Test report generation functionality."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reports import generate_report, list_available_reports

print("Available reports:", list_available_reports())

print("\n" + "=" * 60)
print("Testing executive summary report...")
print("=" * 60)

try:
    result = generate_report(
        "executive_summary", entity="AEML", period="Mar-24", output_dir="data/reports"
    )

    print("\n✅ Report generated successfully!")
    print("\nGenerated files:")
    for fmt, path in result.items():
        print(f"  {fmt:12s}: {path}")

except Exception as e:
    print(f"\n❌ Error: {e!s}")
    import traceback

    traceback.print_exc()
