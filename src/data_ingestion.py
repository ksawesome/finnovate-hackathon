"""Data ingestion module for loading and preprocessing trial balance data."""

import pandas as pd
from pathlib import Path
from decimal import Decimal

from .db.storage import save_raw_csv, save_processed_parquet, load_raw_csv
from .db.postgres import create_gl_account, get_user_by_email
from .db.mongodb import log_audit_event


def load_trial_balance(file_path: str) -> pd.DataFrame:
    """
    Load trial balance CSV file into a pandas DataFrame.

    Args:
        file_path: Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded trial balance data.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    df = pd.read_csv(path)
    
    # Save to raw directory
    save_raw_csv(df, path.name)
    
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic preprocessing of trial balance data.

    Args:
        df: Raw trial balance DataFrame.

    Returns:
        pd.DataFrame: Preprocessed DataFrame.
    """
    # Drop nulls
    df = df.dropna().reset_index(drop=True)
    
    # Ensure required columns exist
    required_cols = ['account_code', 'account_name', 'balance', 'entity', 'period']
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return df


def ingest_to_postgres(df: pd.DataFrame, uploaded_by: str = "system"):
    """
    Ingest preprocessed trial balance data to PostgreSQL.
    
    Args:
        df: Preprocessed DataFrame with GL account data.
        uploaded_by: Email of user who uploaded the data.
    """
    for _, row in df.iterrows():
        # Get assigned user if email column exists
        assigned_user_id = None
        if 'assigned_user_email' in row and pd.notna(row['assigned_user_email']):
            user = get_user_by_email(row['assigned_user_email'])
            if user:
                assigned_user_id = user.id
        
        # Create GL account in PostgreSQL
        gl_account = create_gl_account(
            account_code=str(row['account_code']),
            account_name=str(row['account_name']),
            entity=str(row['entity']),
            balance=Decimal(str(row['balance'])),
            period=str(row['period']),
            assigned_user_id=assigned_user_id
        )
        
        # Log audit event to MongoDB
        log_audit_event(
            gl_code=str(row['account_code']),
            action="uploaded",
            actor={"email": uploaded_by, "source": "csv_upload"},
            details={"entity": str(row['entity']), "period": str(row['period'])}
        )
    
    # Cache as Parquet for fast analytics
    period = df['period'].iloc[0] if len(df) > 0 else "unknown"
    save_processed_parquet(df, f"gl_accounts_{period}")


def pipeline(file_path: str, uploaded_by: str = "system") -> pd.DataFrame:
    """
    Complete ingestion pipeline: load → preprocess → store.
    
    Args:
        file_path: Path to CSV file.
        uploaded_by: Email of uploader.
        
    Returns:
        Preprocessed DataFrame.
    """
    df = load_trial_balance(file_path)
    df = preprocess_data(df)
    ingest_to_postgres(df, uploaded_by)
    return df