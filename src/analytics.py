"""Analytics module for financial analysis."""

import pandas as pd
from sklearn.model_selection import train_test_split

from .db.postgres import get_gl_accounts_by_period
from .db.storage import load_processed_parquet, save_processed_parquet


def perform_analytics(period: str) -> dict:
    """
    Perform analytics on trial balance data for a period.

    Args:
        period: Period to analyze (e.g., "2025-01").

    Returns:
        dict: Analytics results.
    """
    # Load from PostgreSQL
    gl_accounts = get_gl_accounts_by_period(period)

    if not gl_accounts:
        return {"error": f"No data for period {period}"}

    # Convert to DataFrame
    data = [
        {
            "account_code": acc.account_code,
            "account_name": acc.account_name,
            "balance": float(acc.balance),
            "entity": acc.entity,
            "review_status": acc.review_status,
        }
        for acc in gl_accounts
    ]

    df = pd.DataFrame(data)

    # Compute analytics
    total_balance = df["balance"].sum()
    mean_balance = df["balance"].mean()
    pending_reviews = len(df[df["review_status"] == "pending"])
    approved_reviews = len(df[df["review_status"] == "approved"])

    # Group by entity
    entity_summary = df.groupby("entity")["balance"].agg(["sum", "count", "mean"]).to_dict()

    results = {
        "period": period,
        "total_balance": total_balance,
        "mean_balance": mean_balance,
        "total_accounts": len(df),
        "pending_reviews": pending_reviews,
        "approved_reviews": approved_reviews,
        "entity_summary": entity_summary,
    }

    # Cache results
    save_processed_parquet(df, f"analytics_{period}")

    return results


def compare_periods(period1: str, period2: str) -> dict:
    """
    Compare GL account balances between two periods.

    Args:
        period1: First period.
        period2: Second period.

    Returns:
        dict: Comparison results with variances.
    """
    df1 = load_processed_parquet(f"analytics_{period1}")
    df2 = load_processed_parquet(f"analytics_{period2}")

    # Merge on account_code
    merged = df1.merge(df2, on="account_code", suffixes=("_p1", "_p2"), how="outer")

    # Calculate variance
    merged["variance"] = merged["balance_p2"] - merged["balance_p1"]
    merged["variance_pct"] = (merged["variance"] / merged["balance_p1"].abs()) * 100

    # Identify large variances (>10% or >$50k)
    large_variances = merged[
        (merged["variance_pct"].abs() > 10) | (merged["variance"].abs() > 50000)
    ]

    return {
        "period1": period1,
        "period2": period2,
        "total_accounts": len(merged),
        "large_variances": len(large_variances),
        "variance_details": large_variances.to_dict("records"),
    }


def train_model(df: pd.DataFrame):
    """
    Train a simple ML model for anomaly detection.

    Args:
        df: Feature DataFrame.
    """
    # Placeholder for ML training
    if "target" not in df.columns:
        # Create synthetic target for demo
        df["target"] = (df["balance"].abs() > df["balance"].abs().quantile(0.9)).astype(int)

    X = df.drop(columns=["target"], errors="ignore")
    X = X.select_dtypes(include=[float, int])
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Training logic would go here
    # For now, just return shapes
    return {
        "X_train_shape": X_train.shape,
        "X_test_shape": X_test.shape,
        "features": list(X.columns),
    }
