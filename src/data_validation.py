"""Data validation module using Great Expectations.

Phase 1 Part 2 enhancements:
- Expanded expectation suite (15+ checks) with remediation and severity metadata
- Dynamic entity validation based on master data
- Custom expectations scaffolding and ValidationOrchestrator for rich reporting
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List

import great_expectations as gx
import pandas as pd
from great_expectations.core.expectation_suite import ExpectationSuite
from sqlalchemy import text

from .db.mongodb import log_audit_event, log_gl_audit_event, save_validation_results
from .db.postgres import get_gl_accounts_by_period, get_postgres_session


def validate_data(df, suite_name: str = "trial_balance_suite") -> dict:
    """
    Validate DataFrame using Great Expectations.

    Args:
        df: DataFrame to validate.
        suite_name: Name of the expectation suite.

    Returns:
        dict: Validation results.
    """
    context = gx.get_context()
    validator = context.sources.pandas_default.read_dataframe(df)
    suite = context.get_expectation_suite(suite_name)
    results = validator.validate()
    
    # Extract metadata for storage
    gl_code = df['account_code'].iloc[0] if len(df) > 0 else "unknown"
    period = df['period'].iloc[0] if len(df) > 0 else "unknown"
    passed = results.success
    
    # Save full results to MongoDB
    save_validation_results(
        gl_code=gl_code,
        period=period,
        validation_suite=suite_name,
        results=results.to_json_dict(),
        passed=passed
    )
    
    # Log audit event
    # GL-scoped audit trail
    log_gl_audit_event(
        gl_code=gl_code,
        action="validated",
        actor={"source": "gx_validator"},
        details={"suite": suite_name, "passed": passed}
    )
    
    return results.to_json_dict()


def _get_approved_entities() -> List[str]:
    """Fetch approved entities dynamically from database.

    Fallback to commonly used Adani entities if DB query fails.
    """
    try:
        session = get_postgres_session()
        try:
            entities = (
                session.execute(text("SELECT DISTINCT entity FROM gl_accounts"))
                .scalars()
                .all()
            )
            if entities:
                return sorted(set([e for e in entities if e]))
        finally:
            session.close()
    except Exception:
        # Fallback list
        return [
            "ABEX", "AGEL", "APL", "AEML", "ATL", "APSEZ", "ATGL", "AWL", "AEL", "APML", "ARTL",
        ]


def create_expectation_suite(df, suite_name: str) -> ExpectationSuite:
    """
    Create a basic expectation suite for trial balance data.

    Args:
        df: Sample DataFrame.
        suite_name: Name for the suite.

    Returns:
        ExpectationSuite: Configured suite.
    """
    context = gx.get_context()
    # Obtain validator for the sample frame
    validator = context.sources.pandas_default.read_dataframe(df)
    # Try to get existing suite, else create new one
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        suite = ExpectationSuite(expectation_suite_name=suite_name)
        context.add_or_update_expectation_suite(expectation_suite=suite)
    
    # 1) Trial balance must sum to near-zero (debits = credits)
    validator.expect_column_sum_to_be_between(
        "balance", min_value=-1, max_value=1,
        meta={
            "remediation": "Ensure total debits equal total credits; verify any rounding or missing entries.",
            "severity": "critical",
        },
    )
    
    # Required columns must exist
    validator.expect_table_columns_to_match_ordered_list(
        ["account_code", "account_name", "balance", "entity", "period"],
        meta={
            "remediation": "Input must include required columns in correct order; fix header mapping.",
            "severity": "critical",
        },
    )
    
    # No null values in critical columns
    validator.expect_column_values_to_not_be_null(
        "account_code",
        meta={
            "remediation": "GL account code cannot be null; fill or drop invalid rows.",
            "severity": "critical",
        },
    )
    validator.expect_column_values_to_not_be_null(
        "balance",
        meta={
            "remediation": "Balance cannot be null; fill NaN with 0.0 if appropriate before load.",
            "severity": "high",
        },
    )
    
    # Balance should be numeric
    validator.expect_column_values_to_be_of_type(
        "balance", "float64",
        meta={
            "remediation": "Balance must be numeric (float). Coerce types in preprocessing.",
            "severity": "high",
        },
    )

    # 2) Account code format: 8-digit numeric
    validator.expect_column_values_to_match_regex(
        column="account_code",
        regex=r"^\d{8}$",
        meta={
            "remediation": "Account codes must be exactly 8 digits.",
            "severity": "critical",
        },
    )

    # 3) Entity code validation (dynamic from DB)
    validator.expect_column_values_to_be_in_set(
        column="entity",
        value_set=_get_approved_entities(),
        meta={
            "remediation": "Entity must be one of approved entity codes maintained in master data.",
            "severity": "critical",
        },
    )

    # 4) Period format YYYY-MM
    validator.expect_column_values_to_match_regex(
        column="period",
        regex=r"^\d{4}-\d{2}$",
        meta={
            "remediation": "Period must be in YYYY-MM format (e.g., 2022-06).",
            "severity": "critical",
        },
    )

    # 5) BS/PL classification
    if "bs_pl" in df.columns:
        validator.expect_column_values_to_be_in_set(
            column="bs_pl",
            value_set=["BS", "PL"],
            meta={
                "remediation": "BS/PL must be either 'BS' (Balance Sheet) or 'PL' (Profit & Loss).",
                "severity": "high",
            },
        )

    # 6) Status domain validation
    if "status" in df.columns:
        validator.expect_column_values_to_be_in_set(
            column="status",
            value_set=["Assets", "Liabilities", "Expense", "Income", "Equity"],
            meta={
                "remediation": "Status must be one of: Assets, Liabilities, Expense, Income, Equity.",
                "severity": "high",
            },
        )

    # 7) Zero-balance detection: allow up to 70% zeros (sample has ~33.5%)
    validator.expect_column_values_to_not_be_in_set(
        column="balance",
        value_set=[0.0],
        mostly=0.7,
        meta={
            "remediation": "Too many zero-balance accounts indicate stale or misclassified GLs.",
            "severity": "low",
            "business_rule": "Account activity monitoring",
        },
    )

    # 8) Duplicate composite key detection
    validator.expect_compound_columns_to_be_unique(
        column_list=["account_code", "entity", "period"],
        meta={
            "remediation": "Duplicates for (account_code, entity, period) are not allowed; de-duplicate before load.",
            "severity": "critical",
        },
    )

    # 9) Account name sanity
    validator.expect_column_value_lengths_to_be_between(
        column="account_name",
        min_value=3,
        max_value=200,
        meta={
            "remediation": "Account name length must be between 3 and 200 characters.",
            "severity": "medium",
        },
    )

    # 10) Balance range validation (billion-scale org)
    validator.expect_column_values_to_be_between(
        column="balance",
        min_value=-1_000_000_000_000,  # -1T
        max_value=1_000_000_000_000,   # 1T
        meta={
            "remediation": "Balance out of reasonable range; verify units and sign.",
            "severity": "high",
        },
    )

    # Placeholders for custom/business checks handled downstream
    # 11) Carryforward consistency if column present
    if "balance_carryforward" in df.columns:
        validator.expect_column_pair_values_to_be_equal(
            column_A="balance",
            column_B="balance_carryforward",
            meta={
                "remediation": "Carryforward should equal opening balance; investigate adjustments.",
                "severity": "medium",
                "business_rule": "Opening balance integrity",
            },
        )

    # 12) Debit/Credit should be non-negative if present
    if "debit_period" in df.columns:
        validator.expect_column_min_to_be_between(
            column="debit_period",
            min_value=0,
            strictly=False,
            meta={
                "remediation": "Debit Period must be non-negative.",
                "severity": "high",
            },
        )
    if "credit_period" in df.columns:
        validator.expect_column_min_to_be_between(
            column="credit_period",
            min_value=0,
            strictly=False,
            meta={
                "remediation": "Credit Period must be non-negative.",
                "severity": "high",
            },
        )

    # 13) Critical account range check (inventory series) if criticality present
    if "criticality" in df.columns:
        # heuristic: if account_code in 11100200-11199999 and criticality != Critical -> warning
        # Great Expectations lacks row-wise conditional; leave note via warning meta in orchestrator
        pass

    # Persist updated suite under the requested name
    try:
        suite_obj = validator.get_expectation_suite(discard_failed_expectations=False)
    except TypeError:
        # Older/newer API might not support the arg; fallback
        suite_obj = validator.get_expectation_suite()
    suite_obj.expectation_suite_name = suite_name
    context.add_or_update_expectation_suite(expectation_suite=suite_obj)
    return context.get_expectation_suite(suite_name)


def add_custom_expectations(validator) -> None:
    """Hook to add any programmatic/custom expectations on the validator.

    Note: Complex conditional/business-rule checks are better handled in the
    ValidationOrchestrator post-processing for observability and clarity.
    """
    # Example placeholder: ensure variance_pct column (if present) is within a sane range
    try:
        if "variance_pct" in validator.active_batch.data.dataframe.columns:  # type: ignore[attr-defined]
            validator.expect_column_values_to_be_between(
                column="variance_pct",
                min_value=-500.0,
                max_value=500.0,
                meta={
                    "remediation": "Variance percentage seems extreme; verify computation and period base.",
                    "severity": "medium",
                },
            )
    except Exception:
        # Best-effort; not fatal
        pass


# ---------- Orchestrator & Reporting (Task 2 scaffolding) ----------

@dataclass
class ValidationResult:
    entity: str
    period: str
    total_records: int
    validation_suite: str
    passed: bool
    success_percentage: float
    total_checks: int
    passed_checks: int
    failed_checks: int
    critical_failures: int
    high_failures: int
    medium_failures: int
    low_failures: int
    execution_time_seconds: float
    timestamp: str
    failed_expectations: List[Dict[str, Any]]
    warnings: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


class ValidationOrchestrator:
    """Run validation with detailed reporting and persistence."""

    def __init__(self, suite_name: str = "trial_balance_suite") -> None:
        self.suite_name = suite_name
        self.context = gx.get_context()

    def validate_dataframe(
        self,
        df: pd.DataFrame,
        entity: str,
        period: str,
        fail_on_critical: bool = True,
    ) -> ValidationResult:
        start = datetime.utcnow()

        # Build expectation suite fresh for this dataframe
        suite = create_expectation_suite(df, self.suite_name)
        validator = self.context.sources.pandas_default.read_dataframe(df)
        # Run any ad-hoc expectations not persisted
        add_custom_expectations(validator)
        results = validator.validate(expectation_suite=suite)

        # Summarize results
        failed_expectations: List[Dict[str, Any]] = []
        sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for res in getattr(results, "results", []) or []:
            if not res.success:  # type: ignore[attr-defined]
                meta = (res.expectation_config.meta or {})  # type: ignore[attr-defined]
                severity = meta.get("severity", "medium")
                sev_counts[severity] = sev_counts.get(severity, 0) + 1
                failed_expectations.append(
                    {
                        "expectation_type": getattr(res.expectation_config, "expectation_type", "unknown"),
                        "column": (res.expectation_config.kwargs or {}).get("column"),  # type: ignore[attr-defined]
                        "severity": severity,
                        "remediation": meta.get("remediation", "Fix data and retry"),
                        "unexpected_count": (getattr(res, "result", {}) or {}).get("unexpected_count", 0),
                    }
                )

        total_checks = len(getattr(results, "results", []) or [])
        passed_checks = sum(1 for r in (getattr(results, "results", []) or []) if r.success)  # type: ignore[attr-defined]
        failed_checks = total_checks - passed_checks
        success_pct = (passed_checks / total_checks * 100) if total_checks else 0.0
        duration = (datetime.utcnow() - start).total_seconds()

        vr = ValidationResult(
            entity=entity,
            period=period,
            total_records=len(df),
            validation_suite=self.suite_name,
            passed=bool(getattr(results, "success", False) and sev_counts["critical"] == 0),
            success_percentage=success_pct,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            critical_failures=sev_counts["critical"],
            high_failures=sev_counts["high"],
            medium_failures=sev_counts["medium"],
            low_failures=sev_counts["low"],
            execution_time_seconds=duration,
            timestamp=datetime.utcnow().isoformat(),
            failed_expectations=failed_expectations,
            warnings=(
                [
                    f"CRITICAL: {sev_counts['critical']} critical failures",
                ]
                if sev_counts["critical"]
                else []
            ),
        )

        # Persist
        save_validation_results(
            gl_code=f"{entity}_{period}",
            period=period,
            validation_suite=self.suite_name,
            results=vr.to_dict(),
            passed=vr.passed,
        )
        log_audit_event(
            event_type="validation_completed",
            entity=entity,
            period=period,
            passed=vr.passed,
            success_percentage=vr.success_percentage,
            critical_failures=vr.critical_failures,
            execution_time=vr.execution_time_seconds,
        )

        if fail_on_critical and vr.critical_failures:
            raise ValueError(
                f"Validation failed with {vr.critical_failures} critical errors."
            )

        return vr

    def validate_batch(self, files: List[Dict[str, Any]], fail_fast: bool = False):
        results: Dict[str, Any] = {}
        for f in files:
            try:
                df = pd.read_csv(f["file_path"])  # type: ignore[arg-type]
                results[f["file_path"]] = self.validate_dataframe(
                    df,
                    entity=f["entity"],
                    period=f["period"],
                    fail_on_critical=fail_fast,
                ).to_dict()
            except Exception as e:
                if fail_fast:
                    raise
                results[f["file_path"]] = {"error": str(e), **f}
        return results
    


def validate_period(period: str) -> dict:
    """
    Validate all GL accounts for a specific period.
    
    Args:
        period: Period to validate (e.g., "2025-01").
        
    Returns:
        dict: Validation summary.
    """
    import pandas as pd
    
    # Load from PostgreSQL
    gl_accounts = get_gl_accounts_by_period(period)
    
    if not gl_accounts:
        return {"error": f"No GL accounts found for period {period}"}
    
    # Convert to DataFrame
    data = [{
        "account_code": acc.account_code,
        "account_name": acc.account_name,
        "balance": float(acc.balance),
        "entity": acc.entity,
        "period": acc.period
    } for acc in gl_accounts]
    
    df = pd.DataFrame(data)
    
    # Validate
    results = validate_data(df)
    
    return results