"""Data ingestion module for loading and preprocessing trial balance data."""

import pandas as pd
import hashlib
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any
from datetime import datetime

from .db.storage import save_raw_csv, save_processed_parquet, load_raw_csv
from .db.postgres import create_gl_account, get_user_by_email
from .db.mongodb import log_audit_event
from .utils.logging_config import StructuredLogger

logger = StructuredLogger("data_ingestion")


class DataProfiler:
    """
    Profile CSV data before ingestion
    
    Generates statistics:
    - Row and column counts
    - Data types
    - Null percentages
    - Balance statistics
    - Zero-balance account detection
    """
    
    @staticmethod
    def profile(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate data profile
        
        Args:
            df: DataFrame to profile
            
        Returns:
            Dictionary with profile statistics
        """
        logger.log_event("data_profiling_started", rows=len(df), columns=len(df.columns))
        
        profile = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
            "null_percentages": (df.isnull().sum() / len(df) * 100).to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }
        
        # Balance column statistics
        if 'balance' in df.columns:
            balance_col = df['balance'].astype(float)
            profile["balance_stats"] = {
                "sum": float(balance_col.sum()),
                "mean": float(balance_col.mean()),
                "median": float(balance_col.median()),
                "min": float(balance_col.min()),
                "max": float(balance_col.max()),
                "std": float(balance_col.std()),
            }
            
            # Zero-balance detection
            zero_balance_count = (balance_col.abs() < 0.01).sum()
            profile["zero_balance_accounts"] = int(zero_balance_count)
            profile["zero_balance_percentage"] = float(zero_balance_count / len(df) * 100)
        
        # Unique value counts for categorical columns
        categorical_cols = ['entity', 'company_code', 'period', 'bs_pl', 'status', 'department']
        profile["unique_counts"] = {}
        for col in categorical_cols:
            if col in df.columns:
                profile["unique_counts"][col] = int(df[col].nunique())
        
        logger.log_event(
            "data_profiling_completed",
            rows=profile["row_count"],
            zero_balance=profile.get("zero_balance_accounts", 0)
        )
        
        return profile


class SchemaMapper:
    """
    Map CSV columns to PostgreSQL schema
    
    Required columns:
    - account_code, account_name, balance, entity, company_code, period, bs_pl, status
    
    Optional columns:
    - department, criticality, review_status, etc.
    """
    
    REQUIRED_COLUMNS = [
        'account_code',
        'account_name',
        'balance',
        'entity',
        'company_code',
        'period',
        'bs_pl',
        'status'
    ]
    
    OPTIONAL_COLUMNS = [
        'department',
        'criticality',
        'review_status',
        'reviewer_name',
        'review_date',
        'reconciliation_type',
        'sla_deadline'
    ]
    
    @staticmethod
    def validate_schema(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame against required schema
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Validation result with missing/extra columns
        """
        logger.log_event("schema_validation_started", columns=len(df.columns))
        
        df_columns = set(df.columns)
        required_columns = set(SchemaMapper.REQUIRED_COLUMNS)
        all_known_columns = set(SchemaMapper.REQUIRED_COLUMNS + SchemaMapper.OPTIONAL_COLUMNS)
        
        missing_required = required_columns - df_columns
        extra_columns = df_columns - all_known_columns
        
        is_valid = len(missing_required) == 0
        
        result = {
            "is_valid": is_valid,
            "missing_required": list(missing_required),
            "extra_columns": list(extra_columns),
            "present_optional": list(df_columns & set(SchemaMapper.OPTIONAL_COLUMNS))
        }
        
        if is_valid:
            logger.log_event("schema_validation_passed", **result)
        else:
            logger.log_event("schema_validation_failed", level="ERROR", **result)
        
        return result
    
    @staticmethod
    def map_to_postgres_schema(df: pd.DataFrame) -> pd.DataFrame:
        """
        Map DataFrame to PostgreSQL schema
        
        - Rename columns if needed
        - Add default values for missing optional columns
        - Convert data types
        """
        mapped_df = df.copy()
        
        # Add default values for missing optional columns
        if 'department' not in mapped_df.columns:
            mapped_df['department'] = None
        if 'criticality' not in mapped_df.columns:
            mapped_df['criticality'] = 'medium'
        if 'review_status' not in mapped_df.columns:
            mapped_df['review_status'] = 'pending'
        
        # Convert data types
        mapped_df['balance'] = mapped_df['balance'].astype(float)
        mapped_df['account_code'] = mapped_df['account_code'].astype(str)
        
        logger.log_event("schema_mapping_completed", rows=len(mapped_df))
        
        return mapped_df


class FileFingerprinter:
    """
    Generate SHA-256 fingerprint for file lineage tracking
    
    Detects:
    - Duplicate file uploads
    - Data lineage for audit compliance
    """
    
    @staticmethod
    def generate_fingerprint(file_path: str) -> str:
        """
        Generate SHA-256 hash of file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            SHA-256 hash string
        """
        logger.log_event("fingerprint_generation_started", file=file_path)
        
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        fingerprint = sha256_hash.hexdigest()
        
        logger.log_event("fingerprint_generated", fingerprint=fingerprint)
        
        return fingerprint
    
    @staticmethod
    def check_duplicate(fingerprint: str) -> bool:
        """
        Check if file already ingested
        
        Args:
            fingerprint: SHA-256 hash
            
        Returns:
            True if duplicate exists
        """
        from .db.mongodb import get_audit_trail_collection
        
        collection = get_audit_trail_collection()
        
        existing = collection.find_one({
            "event_type": "file_ingested",
            "file_fingerprint": fingerprint
        })
        
        is_duplicate = existing is not None
        
        if is_duplicate:
            logger.log_event("duplicate_file_detected", fingerprint=fingerprint, level="WARNING")
        
        return is_duplicate


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