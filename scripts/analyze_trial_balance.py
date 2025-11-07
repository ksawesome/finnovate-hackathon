"""Analyze all sheets in Trial Balance Excel file."""

import pandas as pd
from pathlib import Path

excel_path = Path("data/sample/Trial Balance with Grouping - V0.xlsx")
xl = pd.ExcelFile(excel_path)

print("=" * 80)
print("TRIAL BALANCE EXCEL FILE ANALYSIS")
print("=" * 80)
print(f"\nFile: {excel_path}")
print(f"Total Sheets: {len(xl.sheet_names)}\n")

for idx, sheet_name in enumerate(xl.sheet_names, 1):
    print("\n" + "=" * 80)
    print(f"SHEET {idx}: {sheet_name}")
    print("=" * 80)
    
    try:
        # Try reading with default settings
        df = pd.read_excel(xl, sheet_name=sheet_name)
        
        print(f"\nShape: {df.shape} (rows x columns)")
        print(f"\nColumns ({len(df.columns)}):")
        for col in df.columns:
            print(f"  - {col}")
        
        print(f"\nData Types:")
        for col, dtype in df.dtypes.items():
            print(f"  - {col}: {dtype}")
        
        print(f"\nNull Values:")
        nulls = df.isnull().sum()
        for col, count in nulls.items():
            if count > 0:
                print(f"  - {col}: {count} ({count/len(df)*100:.1f}%)")
        
        print(f"\nFirst 3 Rows:")
        print(df.head(3).to_string(max_cols=10))
        
        print(f"\nLast 3 Rows:")
        print(df.tail(3).to_string(max_cols=10))
        
        # Check for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            print(f"\nNumeric Columns Summary:")
            print(df[numeric_cols].describe().to_string())
        
    except Exception as e:
        print(f"\nError reading sheet: {e}")
        print("Attempting to read with different parameters...")
        try:
            df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
            print(f"Successfully read with no header. Shape: {df.shape}")
            print(f"First 5 rows:\n{df.head().to_string()}")
        except Exception as e2:
            print(f"Failed to read sheet: {e2}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
