"""
Extract and clean Trial Balance data for ingestion pipeline testing
Converts Final Data sheet to clean CSV format matching PostgreSQL schema
"""

from pathlib import Path

import pandas as pd


def clean_trial_balance():
    """Extract and clean Final Data sheet"""
    # Read Excel file
    print("Reading Excel file...")
    df = pd.read_excel("data/sample/Trial Balance with Grouping - V0.xlsx", sheet_name="Final Data")

    # Use first row as headers
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    # Identify key columns (handle duplicate column names by position)
    columns_map = {
        "BS/PL": "bs_pl",
        "Status": "status",
        "G/L Acct": "account_code",
        "G/L Account Number": "account_name",  # This is actually the description
        "Main Head": "account_category",
        "Sub head": "sub_category",
        "C/M/L": "criticality",  # Critical/Medium/Low
        "Frequency": "review_frequency",
        "Responsible Department": "department",
        "APL Balance as on 30.06.2022": "balance",
        "Flag\n(Green / Red)": "review_flag",
        "Type of Report": "report_type",
        "Analysis Requrired": "analysis_required",  # Note: typo in source
        "Review Check point at ABEX": "review_checkpoint",
        "% Variance": "variance_pct",
        "Recon / Non Recon": "reconciliation_type",
    }

    # Extract relevant columns (handle columns that might not exist)
    clean_data = {}
    for source_col, target_col in columns_map.items():
        if source_col in df.columns:
            clean_data[target_col] = df[source_col]
        else:
            print(f"Warning: Column '{source_col}' not found")
            clean_data[target_col] = None

    clean_df = pd.DataFrame(clean_data)

    # Data cleaning
    print("\nCleaning data...")

    # 1. Clean account_code - extract numeric GL account
    if "account_code" in clean_df.columns:
        clean_df["account_code"] = pd.to_numeric(clean_df["account_code"], errors="coerce")
        clean_df["account_code"] = clean_df["account_code"].astype("Int64")  # Use nullable integer

    # 2. Clean balance - convert to numeric
    if "balance" in clean_df.columns:
        clean_df["balance"] = pd.to_numeric(clean_df["balance"], errors="coerce")

    # 3. Standardize boolean fields
    if "analysis_required" in clean_df.columns:
        clean_df["analysis_required"] = (
            clean_df["analysis_required"].str.strip().str.lower() == "yes"
        )

    # 4. Clean review_flag
    if "review_flag" in clean_df.columns:
        clean_df["review_flag"] = clean_df["review_flag"].str.strip()
        # Map to standardized values
        flag_map = {"Green": "reviewed", "Red": "flagged", "Not Considered": "skipped"}
        clean_df["review_status"] = clean_df["review_flag"].map(flag_map).fillna("pending")

    # 5. Clean criticality (C/M/L -> Critical/Medium/Low)
    if "criticality" in clean_df.columns:
        criticality_map = {
            "Critical": "Critical",
            "Medium": "Medium",
            "Low": "Low",
            "C": "Critical",
            "M": "Medium",
            "L": "Low",
        }
        clean_df["criticality"] = clean_df["criticality"].map(criticality_map)

    # 6. Add metadata columns
    clean_df["entity"] = "ABEX"  # Adani Ports & Logistics
    clean_df["period"] = "2022-06"  # June 2022

    # 7. Remove rows with missing account codes
    initial_count = len(clean_df)
    clean_df = clean_df.dropna(subset=["account_code"])
    removed_count = initial_count - len(clean_df)
    print(f"Removed {removed_count} rows with missing account codes")

    # 8. Sort by account code
    clean_df = clean_df.sort_values("account_code").reset_index(drop=True)

    # Select final columns for CSV
    output_columns = [
        "entity",
        "period",
        "account_code",
        "account_name",
        "balance",
        "bs_pl",
        "status",
        "account_category",
        "sub_category",
        "criticality",
        "review_frequency",
        "department",
        "review_status",
        "review_flag",
        "report_type",
        "analysis_required",
        "review_checkpoint",
        "reconciliation_type",
        "variance_pct",
    ]

    # Only include columns that exist
    output_columns = [col for col in output_columns if col in clean_df.columns]
    final_df = clean_df[output_columns]

    # Save to CSV
    output_path = Path("data/sample/trial_balance_cleaned.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)

    print(f"\nSaved cleaned data to: {output_path}")
    print(f"Total records: {len(final_df)}")
    print("\nSample records:")
    print(final_df.head(10).to_string())

    # Print summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"\nTotal Accounts: {len(final_df)}")
    print("\nBy BS/PL:")
    print(final_df["bs_pl"].value_counts())
    print("\nBy Status:")
    print(final_df["status"].value_counts())
    print("\nBy Review Status:")
    if "review_status" in final_df.columns:
        print(final_df["review_status"].value_counts())
    print("\nBy Criticality:")
    if "criticality" in final_df.columns:
        print(final_df["criticality"].value_counts())
    print("\nBalance Statistics:")
    print(final_df["balance"].describe())

    return final_df


if __name__ == "__main__":
    clean_df = clean_trial_balance()
    print("\n✅ Data extraction and cleaning complete!")
