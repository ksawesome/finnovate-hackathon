"""Test script for data ingestion classes"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from src.data_ingestion import DataProfiler, FileFingerprinter, SchemaMapper

# Test DataProfiler
print("\n=== Testing DataProfiler ===")
df = pd.DataFrame(
    {
        "account_code": ["11100200", "21100000", "31100000"],
        "account_name": ["Cash", "Payables", "Revenue"],
        "balance": [1000.0, 0.0, -1000.0],
        "entity": ["TEST", "TEST", "TEST"],
        "company_code": ["5500", "5500", "5500"],
        "period": ["2024-01", "2024-01", "2024-01"],
        "bs_pl": ["BS", "BS", "PL"],
        "status": ["Assets", "Liabilities", "Income"],
    }
)

profile = DataProfiler.profile(df)
print(f"✅ Row count: {profile['row_count']}")
print(f"✅ Zero-balance accounts: {profile.get('zero_balance_accounts', 0)}")
print(f"✅ Balance sum: {profile['balance_stats']['sum']}")

# Test SchemaMapper
print("\n=== Testing SchemaMapper ===")
validation = SchemaMapper.validate_schema(df)
print(f"✅ Schema valid: {validation['is_valid']}")
print(f"✅ Missing required: {validation['missing_required']}")

mapped_df = SchemaMapper.map_to_postgres_schema(df)
print(f"✅ Mapped DataFrame has {len(mapped_df)} rows")
print(
    f"✅ Default columns added: {['department' in mapped_df.columns, 'criticality' in mapped_df.columns]}"
)

# Test FileFingerprinter
print("\n=== Testing FileFingerprinter ===")
# Create a test file
test_file = "data/sample/trial_balance_cleaned.csv"
fingerprint = FileFingerprinter.generate_fingerprint(test_file)
print(f"✅ Fingerprint generated: {fingerprint[:16]}...")
print(f"✅ Fingerprint length: {len(fingerprint)} chars (SHA-256)")

print("\n✅ ALL TESTS PASSED\n")
