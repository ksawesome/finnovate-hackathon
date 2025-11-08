"""Generate and inspect executive summary PDF."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reports import generate_report

print("Generating Executive Summary Report...")
print("=" * 60)

try:
    files = generate_report(
        "executive_summary", entity="AEML", period="Mar-24", output_dir="data/reports"
    )

    print("\n✅ Report generated successfully!")
    print("\nGenerated files:")
    for fmt, path in files.items():
        file_path = Path(path)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  {fmt:12s}: {path}")
            print(f"                Size: {size:,} bytes ({size/1024:.1f} KB)")
        else:
            print(f"  {fmt:12s}: {path} (FILE NOT FOUND)")

    # Try to read and display markdown content
    if "markdown" in files:
        md_path = Path(files["markdown"])
        if md_path.exists():
            print("\n" + "=" * 60)
            print("MARKDOWN CONTENT PREVIEW:")
            print("=" * 60)
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Show first 1500 characters
                print(content[:1500])
                if len(content) > 1500:
                    print(f"\n... (truncated, total {len(content)} characters)")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("To view PDF, open:")
print(f"  {Path(files['pdf']).absolute()}")
