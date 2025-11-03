"""Data validation module using Great Expectations."""

import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite

from .db.mongodb import save_validation_results, log_audit_event
from .db.postgres import get_gl_accounts_by_period


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
    log_audit_event(
        gl_code=gl_code,
        action="validated",
        actor={"source": "gx_validator"},
        details={"suite": suite_name, "passed": passed}
    )
    
    return results.to_json_dict()


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
    suite = context.create_expectation_suite(suite_name, overwrite_existing=True)
    
    # Add basic expectations for trial balance
    validator = context.sources.pandas_default.read_dataframe(df)
    
    # Trial balance must sum to zero (debits = credits)
    validator.expect_column_sum_to_be_between("balance", min_value=-1, max_value=1)
    
    # Required columns must exist
    validator.expect_table_columns_to_match_ordered_list([
        "account_code", "account_name", "balance", "entity", "period"
    ])
    
    # No null values in critical columns
    validator.expect_column_values_to_not_be_null("account_code")
    validator.expect_column_values_to_not_be_null("balance")
    
    # Balance should be numeric
    validator.expect_column_values_to_be_of_type("balance", "float64")
    
    return suite


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