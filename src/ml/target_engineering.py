"""
Target Variable Engineering for Supervised ML.

Creates 4 target variables:
1. Anomaly Score (regression) - Likelihood account is anomalous (0-1)
2. Priority Score (regression) - Review priority ranking (0-10)
3. Needs Attention (binary) - Requires immediate action (0/1)
4. Review Time (regression) - Estimated days to complete review
"""

import numpy as np
import pandas as pd


def create_anomaly_target(df: pd.DataFrame) -> np.ndarray:
    """
    Create anomaly score target (0-1 range).

    Anomaly indicators:
    - Flagged status: +0.5
    - High balance (>100M): +0.3
    - Zero balance: +0.2
    - Negative balance for asset/revenue: +0.3
    - Positive balance for liability/expense: +0.2

    Args:
        df: Features DataFrame with account metadata

    Returns:
        Anomaly scores array (0-1 range)
    """
    anomaly_score = np.zeros(len(df))

    # Flagged accounts are highly anomalous
    if "review_status" in df.columns:
        anomaly_score += (df["review_status"] == "flagged").astype(float) * 0.5

    # High balance anomaly
    if "balance" in df.columns:
        anomaly_score += (df["balance"].abs() > 100_000_000).astype(float) * 0.3

    # Zero balance anomaly
    if "balance" in df.columns:
        anomaly_score += (df["balance"] == 0).astype(float) * 0.2

    # Sign anomalies based on category
    if "balance" in df.columns and "category" in df.columns:
        # Assets and Revenue should typically be positive
        asset_revenue_negative = (
            (df["category"].isin(["Assets", "Revenue"])) & (df["balance"] < 0)
        ).astype(float) * 0.3

        # Liabilities and Expenses should typically be negative
        liability_expense_positive = (
            (df["category"].isin(["Liabilities", "Expenses"])) & (df["balance"] > 0)
        ).astype(float) * 0.2

        anomaly_score += asset_revenue_negative + liability_expense_positive

    # Cap at 1.0
    anomaly_score = np.minimum(anomaly_score, 1.0)

    return anomaly_score


def create_priority_target(df: pd.DataFrame) -> np.ndarray:
    """
    Create priority score target (0-10 range).

    Priority factors:
    - Criticality: Critical=10, High=7, Medium=4, Low=1
    - Balance magnitude: Higher balance = higher priority
    - Status: Flagged=+3, Pending=+1
    - Quarter/Year end: +2

    Args:
        df: Features DataFrame

    Returns:
        Priority scores array (0-10 range)
    """
    priority_score = np.zeros(len(df))

    # Criticality mapping
    if "criticality" in df.columns:
        criticality_map = {"Critical": 10, "High": 7, "Medium": 4, "Low": 1}
        priority_score += df["criticality"].map(criticality_map).fillna(1).values

    # Balance magnitude (normalized contribution 0-3)
    if "balance" in df.columns:
        balance_abs = df["balance"].abs()
        if balance_abs.max() > 0:
            balance_priority = (balance_abs / balance_abs.max()) * 3
            priority_score += balance_priority.values

    # Status boost
    if "review_status" in df.columns:
        priority_score += (df["review_status"] == "flagged").astype(float) * 3
        priority_score += (df["review_status"] == "pending").astype(float) * 1

    # Period importance
    if "period" in df.columns:
        # Quarter-end months get priority boost
        is_quarter_end = df["period"].str.contains("Mar|Jun|Sep|Dec", na=False)
        priority_score += is_quarter_end.astype(float) * 2

    # Cap at 10.0
    priority_score = np.minimum(priority_score, 10.0)

    return priority_score


def create_attention_target(df: pd.DataFrame) -> np.ndarray:
    """
    Create binary needs-attention target.

    Needs attention if:
    - Flagged status
    - High criticality AND pending
    - Balance > 100M AND pending
    - Zero balance AND critical

    Args:
        df: Features DataFrame

    Returns:
        Binary attention flags (0 or 1)
    """
    needs_attention = np.zeros(len(df), dtype=int)

    # Flagged always needs attention
    if "review_status" in df.columns:
        needs_attention |= (df["review_status"] == "flagged").astype(int).values

    # High criticality pending
    if "criticality" in df.columns and "review_status" in df.columns:
        high_crit_pending = (
            ((df["criticality"] == "Critical") & (df["review_status"] == "pending"))
            .astype(int)
            .values
        )
        needs_attention |= high_crit_pending

    # High balance pending
    if "balance" in df.columns and "review_status" in df.columns:
        high_balance_pending = (
            ((df["balance"].abs() > 100_000_000) & (df["review_status"] == "pending"))
            .astype(int)
            .values
        )
        needs_attention |= high_balance_pending

    # Zero balance critical
    if "balance" in df.columns and "criticality" in df.columns:
        zero_critical = (
            ((df["balance"] == 0) & (df["criticality"] == "Critical")).astype(int).values
        )
        needs_attention |= zero_critical

    return needs_attention


def create_review_time_target(df: pd.DataFrame) -> np.ndarray:
    """
    Create estimated review time target (days).

    Factors:
    - Base time: 5 days
    - Criticality: Critical=-2, High=-1, Medium=0, Low=+1
    - Complexity (balance): Higher balance = more time
    - Status: Reviewed=actual time, Pending=estimate

    Args:
        df: Features DataFrame with temporal info

    Returns:
        Estimated review time in days
    """
    review_time = np.full(len(df), 5.0)  # Base 5 days

    # Criticality adjustment
    if "criticality" in df.columns:
        crit_adjustment = (
            df["criticality"]
            .map({"Critical": -2, "High": -1, "Medium": 0, "Low": 1})
            .fillna(0)
            .values
        )
        review_time += crit_adjustment

    # Complexity based on balance
    if "balance" in df.columns:
        balance_abs = df["balance"].abs()
        if balance_abs.max() > 0:
            # Higher balance = up to +3 days
            complexity_days = (balance_abs / balance_abs.max()) * 3
            review_time += complexity_days.values

    # Use actual review velocity if available
    if "review_velocity" in df.columns:
        actual_time = df["review_velocity"].fillna(5.0).values
        # Only use actual time for reviewed items
        if "review_status" in df.columns:
            is_reviewed = (df["review_status"] == "reviewed").values
            review_time = np.where(is_reviewed, actual_time, review_time)

    # Ensure positive
    review_time = np.maximum(review_time, 1.0)

    return review_time


def create_all_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create all 4 target variables.

    Args:
        df: Features DataFrame

    Returns:
        DataFrame with target columns added
    """
    targets_df = df.copy()

    targets_df["target_anomaly_score"] = create_anomaly_target(df)
    targets_df["target_priority_score"] = create_priority_target(df)
    targets_df["target_needs_attention"] = create_attention_target(df)
    targets_df["target_review_time"] = create_review_time_target(df)

    return targets_df


if __name__ == "__main__":
    # Test target creation
    print("Testing Target Engineering...")

    # Create sample data
    sample_df = pd.DataFrame(
        {
            "account_code": ["1000", "2000", "3000", "4000"],
            "balance": [100_000_000, -50_000_000, 0, 10_000],
            "category": ["Assets", "Liabilities", "Assets", "Expenses"],
            "criticality": ["Critical", "High", "Low", "Medium"],
            "review_status": ["flagged", "pending", "reviewed", "pending"],
            "period": ["Mar-24", "Feb-24", "Mar-24", "Jan-24"],
            "review_velocity": [2.5, 4.0, 1.0, 6.0],
        }
    )

    # Create targets
    anomaly = create_anomaly_target(sample_df)
    priority = create_priority_target(sample_df)
    attention = create_attention_target(sample_df)
    review_time = create_review_time_target(sample_df)

    print(f"\n✅ Anomaly scores: {anomaly}")
    print(f"✅ Priority scores: {priority}")
    print(f"✅ Attention flags: {attention}")
    print(f"✅ Review times: {review_time}")

    # Create all targets
    targets_df = create_all_targets(sample_df)
    print("\n📊 Targets DataFrame:")
    print(
        targets_df[
            [
                "account_code",
                "target_anomaly_score",
                "target_priority_score",
                "target_needs_attention",
                "target_review_time",
            ]
        ]
    )
