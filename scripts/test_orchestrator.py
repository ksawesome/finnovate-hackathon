"""Test IngestionOrchestrator"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import IngestionOrchestrator

print("\n=== Testing IngestionOrchestrator ===")

orchestrator = IngestionOrchestrator()

# Test with sample file
result = orchestrator.ingest_file(
    file_path="data/sample/trial_balance_cleaned.csv",
    entity="ABEX",
    period="2022-06",
    skip_duplicates=False
)

print(f"\nStatus: {result['status']}")
if result['status'] == 'success':
    print(f"✅ Duration: {result['duration_seconds']:.2f} seconds")
    print(f"✅ Inserted: {result['inserted']}")
    print(f"✅ Updated: {result['updated']}")
    print(f"✅ Failed: {result['failed']}")
    print(f"✅ Fingerprint: {result['fingerprint'][:16]}...")
    print(f"✅ Zero-balance accounts: {result['profile'].get('zero_balance_accounts', 0)}")
    print(f"✅ Balance sum: ₹{result['profile']['balance_stats']['sum']:,.2f}")
else:
    print(f"❌ Error: {result.get('error', 'Unknown')}")

print("\n✅ IngestionOrchestrator TEST COMPLETE\n")
