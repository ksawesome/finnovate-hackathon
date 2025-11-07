"""Data ingestion module for loading and preprocessing trial balance data."""

import hashlib
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .db.mongodb import log_audit_event, log_gl_audit_event
from .db.postgres import create_gl_account, get_user_by_email
from .db.storage import save_processed_parquet, save_raw_csv
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
        'period',
        'bs_pl',
        'status'
    ]
    
    OPTIONAL_COLUMNS = [
        'company_code',
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
        if 'company_code' not in mapped_df.columns:
            mapped_df['company_code'] = '5500'  # Default company code
        if 'department' not in mapped_df.columns:
            mapped_df['department'] = None
        if 'criticality' not in mapped_df.columns:
            mapped_df['criticality'] = 'medium'
        if 'review_status' not in mapped_df.columns:
            mapped_df['review_status'] = 'pending'
        
        # Convert data types and handle NULL values
        # Balance is NOT NULL in DB schema - convert None/NaN to 0.0
        mapped_df['balance'] = mapped_df['balance'].fillna(0.0).astype(float)
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


class IngestionOrchestrator:
    """
    Orchestrate complete ingestion pipeline
    
    Flow:
    1. Upload CSV file
    2. Profile data
    3. Validate schema
    4. Generate fingerprint
    5. Check for duplicates
    6. Bulk insert to PostgreSQL
    7. Save metadata to MongoDB
    8. Cache to Parquet
    9. Log audit event
    """
    
    def __init__(self):
        self.profiler = DataProfiler()
        self.schema_mapper = SchemaMapper()
        self.fingerprinter = FileFingerprinter()
    
    def ingest_file(
        self,
        file_path: str,
        entity: str,
        period: str,
        skip_duplicates: bool = True,
        validate_before_insert: bool = True,
        fail_on_validation_error: bool = True,
        validation_suite_name: str = "ingestion_validation"
    ) -> Dict[str, Any]:
        """
        Ingest CSV file
        
        Args:
            file_path: Path to CSV file
            entity: Entity code
            period: Period (YYYY-MM)
            skip_duplicates: Skip if file already ingested
            validate_before_insert: Run Great Expectations validation before inserting to PostgreSQL
            fail_on_validation_error: Abort ingestion if validation fails (critical/high severity)
            validation_suite_name: Name for validation suite / run identifier
            
        Returns:
            Ingestion result with statistics
        """
        from .db.mongodb import save_ingestion_metadata
        from .db.postgres import bulk_create_gl_accounts
        # Lazy import to avoid circular dependencies at module load
        if validate_before_insert:
            try:
                from .data_validation import ValidationOrchestrator
            except Exception as e:  # pragma: no cover - defensive
                logger.log_event("validation_import_failed", level="ERROR", error=str(e))
                if fail_on_validation_error:
                    return {
                        "status": "failed",
                        "entity": entity,
                        "period": period,
                        "error": f"Failed to import validation module: {e}"
                    }
        
        start_time = datetime.utcnow()
        
        logger.log_event(
            "ingestion_started",
            file=file_path,
            entity=entity,
            period=period
        )
        
        try:
            # 1. Load CSV
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} records from {file_path}")
            
            # 2. Profile data
            profile = self.profiler.profile(df)
            
            # 3. Validate schema
            schema_validation = self.schema_mapper.validate_schema(df)
            
            if not schema_validation["is_valid"]:
                raise ValueError(
                    f"Schema validation failed. Missing columns: {schema_validation['missing_required']}"
                )
            
            # 4. Map to PostgreSQL schema
            df = self.schema_mapper.map_to_postgres_schema(df)
            
            # 4b. (Optional) Run validation prior to fingerprint & persistence
            validation_metrics: Dict[str, Any] = {}
            if validate_before_insert:
                validation_start = datetime.utcnow()
                try:
                    orchestrator = ValidationOrchestrator(suite_name=validation_suite_name)
                    v_result = orchestrator.validate_dataframe(
                        df,
                        entity=entity,
                        period=period,
                        fail_on_critical=False
                    )
                    validation_duration = (datetime.utcnow() - validation_start).total_seconds()
                    validation_metrics = {
                        "validation_passed": v_result.passed,
                        "validation_total_checks": v_result.total_checks,
                        "validation_failed_checks": v_result.failed_checks,
                        "validation_critical_failures": v_result.critical_failures,
                        "validation_success_percentage": v_result.success_percentage,
                        "validation_duration_seconds": validation_duration,
                        "validation_suite": v_result.validation_suite,
                        "validation_failed_expectations": v_result.failed_expectations,
                    }
                    logger.log_event(
                        "pre_ingestion_validation_completed",
                        passed=v_result.passed,
                        total_checks=v_result.total_checks,
                        failed=v_result.failed_checks,
                        critical_failures=v_result.critical_failures,
                        duration_seconds=validation_duration
                    )
                    if fail_on_validation_error and not v_result.passed:
                        # Abort before persistence
                        log_audit_event(
                            event_type="ingestion_validation_failed",
                            entity=entity,
                            period=period,
                            details={
                                "failed_checks": v_result.failed_checks,
                                "critical_failures": v_result.critical_failures,
                                "failed_expectations": v_result.failed_expectations
                            }
                        )
                        return {
                            "status": "validation_failed",
                            "entity": entity,
                            "period": period,
                            **validation_metrics
                        }
                except Exception as ve:
                    logger.log_event("pre_ingestion_validation_error", level="ERROR", error=str(ve))
                    if fail_on_validation_error:
                        return {
                            "status": "failed",
                            "entity": entity,
                            "period": period,
                            "error": f"Validation step failed: {ve}"
                        }
                    else:
                        validation_metrics = {
                            "validation_passed": False,
                            "validation_error": str(ve)
                        }

            # 5. Generate fingerprint
            fingerprint = self.fingerprinter.generate_fingerprint(file_path)
            
            # 6. Check duplicates
            if skip_duplicates and self.fingerprinter.check_duplicate(fingerprint):
                logger.warning("Duplicate file detected. Skipping ingestion.")
                return {
                    "status": "skipped",
                    "reason": "duplicate",
                    "fingerprint": fingerprint
                }
            
            # 7. Bulk insert to PostgreSQL
            result = bulk_create_gl_accounts(df, entity, period)
            
            logger.log_event(
                "db_insert",
                inserted=result["inserted"],
                updated=result["updated"],
                failed=result["failed"]
            )
            
            # 8. Save metadata to MongoDB
            save_ingestion_metadata(
                entity=entity,
                period=period,
                profile=profile,
                fingerprint=fingerprint,
                ingestion_result=result,
                validation=validation_metrics if validation_metrics else None
            )
            
            # 9. Cache to Parquet
            save_processed_parquet(df, f"{entity}_{period}_ingested")
            
            # 10. Log audit event
            log_audit_event(
                event_type="file_ingested",
                entity=entity,
                period=period,
                file_fingerprint=fingerprint,
                records_processed=result["inserted"] + result["updated"],
                execution_time_seconds=(datetime.utcnow() - start_time).total_seconds()
            )
            
            logger.log_event(
                "ingestion_completed",
                entity=entity,
                period=period,
                records=result["inserted"] + result["updated"],
                duration_seconds=(datetime.utcnow() - start_time).total_seconds()
            )
            
            return {
                "status": "success",
                "entity": entity,
                "period": period,
                "fingerprint": fingerprint,
                "profile": profile,
                "inserted": result["inserted"],
                "updated": result["updated"],
                "failed": result["failed"],
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
                **({} if not validation_metrics else validation_metrics)
            }
            
        except Exception as e:
            logger.log_event("error_occurred", level="ERROR", error=str(e))
            
            return {
                "status": "failed",
                "entity": entity,
                "period": period,
                "error": str(e)
            }


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
        
        # Log audit event to MongoDB (GL-scoped)
        log_gl_audit_event(
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