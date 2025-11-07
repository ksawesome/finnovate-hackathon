import pandas as pd

df = pd.read_csv("data/sample/trial_balance_cleaned.csv")

print("=== DATA ANALYSIS FOR PHASE 1 PART 2 ===\n")

print(f"Total records: {len(df)}")

print("\n=== BALANCE STATISTICS ===")
print(df["balance"].describe())

print(f'\nMax balance: Rs. {df["balance"].max():,.2f}')
print(f'Min balance: Rs. {df["balance"].min():,.2f}')
print(f'Mean balance: Rs. {df["balance"].mean():,.2f}')
print(f'Median balance: Rs. {df["balance"].median():,.2f}')

# Calculate percentiles for threshold recommendations
print("\n=== BALANCE PERCENTILES (for threshold decisions) ===")
print(f'90th percentile: Rs. {df["balance"].quantile(0.90):,.2f}')
print(f'95th percentile: Rs. {df["balance"].quantile(0.95):,.2f}')
print(f'99th percentile: Rs. {df["balance"].quantile(0.99):,.2f}')

# Count accounts above proposed thresholds
print("\n=== ACCOUNTS ABOVE THRESHOLDS ===")
above_10m = (df["balance"].abs() > 10_000_000).sum()
above_5m = (df["balance"].abs() > 5_000_000).sum()
above_1m = (df["balance"].abs() > 1_000_000).sum()
print(f"Above 10M: {above_10m} accounts ({above_10m/len(df)*100:.1f}%)")
print(f"Above 5M: {above_5m} accounts ({above_5m/len(df)*100:.1f}%)")
print(f"Above 1M: {above_1m} accounts ({above_1m/len(df)*100:.1f}%)")

print("\n=== ENTITY DISTRIBUTION ===")
print(df["entity"].value_counts())

print("\n=== CRITICALITY DISTRIBUTION ===")
if "criticality" in df.columns:
    print(df["criticality"].value_counts())
    print(f'\nCritical accounts: {(df["criticality"] == "Critical").sum()}')
else:
    print("Criticality column not found")

print("\n=== ACCOUNT CODE RANGE ===")
print(f'Min: {df["account_code"].min()}')
print(f'Max: {df["account_code"].max()}')

print("\n=== ZERO BALANCE ANALYSIS ===")
zero_balance = (df["balance"] == 0.0).sum()
print(f"Zero balance accounts: {zero_balance} ({zero_balance/len(df)*100:.1f}%)")

print("\n=== BS/PL DISTRIBUTION ===")
if "bs_pl" in df.columns:
    print(df["bs_pl"].value_counts())

print("\n=== STATUS DISTRIBUTION ===")
if "status" in df.columns:
    print(df["status"].value_counts())
