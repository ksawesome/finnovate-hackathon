"""Analytics module for financial analysis."""

import pandas as pd
from sklearn.model_selection import train_test_split

from .db.postgres import get_gl_accounts_by_period
from .db.storage import load_processed_parquet, save_processed_parquet


def perform_analytics(entity: str, period: str) -> dict:
    """
    Perform analytics on trial balance data for an entity and period.

    Args:
        entity: Entity code to analyze (e.g., "AEML").
        period: Period to analyze (e.g., "Mar-24").

    Returns:
        dict: Analytics results.
    """
    # Load from PostgreSQL
    gl_accounts = get_gl_accounts_by_period(period)

    if not gl_accounts:
        return {"error": f"No data for period {period}"}

    # Filter by entity
    gl_accounts = [acc for acc in gl_accounts if acc.entity == entity]

    if not gl_accounts:
        return {"error": f"No data for entity {entity} in period {period}"}

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
    flagged_reviews = len(df[df["review_status"] == "flagged"])

    # Status distribution
    by_status = df["review_status"].value_counts().to_dict()

    # Group by entity
    entity_summary = df.groupby("entity")["balance"].agg(["sum", "count", "mean"]).to_dict()

    results = {
        "period": period,
        "entity": entity,
        "total_balance": total_balance,
        "mean_balance": mean_balance,
        "account_count": len(df),
        "total_accounts": len(df),
        "pending_reviews": pending_reviews,
        "approved_reviews": approved_reviews,
        "flagged_count": flagged_reviews,
        "by_status": by_status,
        "entity_summary": entity_summary,
    }

    # Cache results
    save_processed_parquet(df, f"analytics_{entity}_{period}")

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


def calculate_variance_analysis(entity: str, current_period: str, previous_period: str) -> dict:
    """
    Calculate period-over-period variance analysis for GL accounts.

    Args:
        entity: Entity code (e.g., 'ABEX', 'AGEL', 'APL')
        current_period: Current period (e.g., '2024-03')
        previous_period: Previous period (e.g., '2024-02')

    Returns:
        dict: Variance analysis with summary statistics and significant accounts
    """

    try:
        # Get accounts for both periods
        current_accounts = get_gl_accounts_by_period(current_period)
        previous_accounts = get_gl_accounts_by_period(previous_period)

        # Filter by entity
        current_df = pd.DataFrame(
            [
                {
                    "account_code": acc.account_code,
                    "account_name": acc.account_name,
                    "balance": float(acc.balance),
                    "category": acc.account_category,
                    "department": acc.department,
                }
                for acc in current_accounts
                if acc.entity == entity
            ]
        )

        previous_df = pd.DataFrame(
            [
                {
                    "account_code": acc.account_code,
                    "account_name": acc.account_name,
                    "balance": float(acc.balance),
                    "category": acc.account_category,
                    "department": acc.department,
                }
                for acc in previous_accounts
                if acc.entity == entity
            ]
        )

        if current_df.empty or previous_df.empty:
            return {
                "entity": entity,
                "current_period": current_period,
                "previous_period": previous_period,
                "error": "Insufficient data for variance analysis",
            }

        # Merge on account_code
        merged = current_df.merge(
            previous_df, on="account_code", suffixes=("_current", "_previous"), how="outer"
        )

        # Fill missing balances with 0
        merged["balance_current"] = merged["balance_current"].fillna(0)
        merged["balance_previous"] = merged["balance_previous"].fillna(0)

        # Calculate variance
        merged["variance"] = merged["balance_current"] - merged["balance_previous"]
        merged["variance_pct"] = (
            ((merged["variance"] / merged["balance_previous"].abs()) * 100)
            .replace([float("inf"), -float("inf")], 0)
            .fillna(0)
        )

        # Identify significant variances (>10% or >₹50,000)
        significant = merged[
            (merged["variance_pct"].abs() > 10) | (merged["variance"].abs() > 50000)
        ].copy()

        # Summary statistics
        total_variance = merged["variance"].sum()
        variance_pct = (
            (total_variance / merged["balance_previous"].sum()) * 100
            if merged["balance_previous"].sum() != 0
            else 0
        )

        return {
            "entity": entity,
            "current_period": current_period,
            "previous_period": previous_period,
            "total_accounts": len(merged),
            "total_current_balance": float(merged["balance_current"].sum()),
            "total_previous_balance": float(merged["balance_previous"].sum()),
            "total_variance": float(total_variance),
            "variance_pct": float(variance_pct),
            "significant_accounts": len(significant),
            "variance_summary": f"Total variance: ₹{total_variance:,.2f} ({variance_pct:.1f}%)",
            "significant_variances": significant.nlargest(10, "variance", keep="all").to_dict(
                "records"
            ),
        }

    except Exception as e:
        return {"error": str(e)}


def calculate_review_status_summary(entity: str, period: str) -> dict:
    """
    Calculate review status summary for GL accounts.

    Args:
        entity: Entity code
        period: Period (e.g., '2024-03')

    Returns:
        dict: Review status statistics grouped by various dimensions
    """
    try:
        accounts = get_gl_accounts_by_period(period)

        # Filter by entity and convert to DataFrame
        df = pd.DataFrame(
            [
                {
                    "account_code": acc.account_code,
                    "account_name": acc.account_name,
                    "balance": float(acc.balance),
                    "review_status": acc.review_status or "Pending",
                    "criticality": acc.criticality or "Medium",
                    "category": acc.account_category,
                    "department": acc.department,
                }
                for acc in accounts
                if acc.entity == entity
            ]
        )

        if df.empty:
            return {"entity": entity, "period": period, "error": "No data found"}

        # Overall status counts (case-insensitive)
        df["review_status_lower"] = df["review_status"].str.lower()
        status_counts = df["review_status"].value_counts().to_dict()
        total = len(df)
        reviewed = sum(df["review_status_lower"].isin(["reviewed", "approved"]))
        pending = sum(df["review_status_lower"] == "pending")
        flagged = sum(df["review_status_lower"] == "flagged")

        # By criticality
        criticality_summary = (
            df.groupby("criticality")["review_status"]
            .value_counts()
            .unstack(fill_value=0)
            .to_dict("index")
        )

        # By category
        category_summary = (
            df.groupby("category")["review_status"]
            .value_counts()
            .unstack(fill_value=0)
            .to_dict("index")
        )

        # By department
        department_summary = (
            df.groupby("department")["review_status"]
            .value_counts()
            .unstack(fill_value=0)
            .to_dict("index")
        )

        completion_rate = (reviewed / total * 100) if total > 0 else 0

        return {
            "entity": entity,
            "period": period,
            "overall": {
                "total_accounts": total,
                "reviewed": reviewed,
                "pending": pending,
                "flagged": flagged,
                "completion_pct": completion_rate,
            },
            "overall_completion_rate": completion_rate,  # Also at top level for compatibility
            "pending_count": pending,
            "reviewed_count": reviewed,
            "by_criticality": criticality_summary,
            "by_category": category_summary,
            "by_department": department_summary,
            "status_distribution": status_counts,
        }

    except Exception as e:
        return {"error": str(e)}


def calculate_gl_hygiene_score(entity: str, period: str) -> dict:
    """
    Calculate GL hygiene score based on multiple quality factors.

    Args:
        entity: Entity code
        period: Period (e.g., '2024-03')

    Returns:
        dict: Hygiene score (0-100) with component breakdown
    """

    from .db.mongodb import get_mongo_database

    mongo_db = get_mongo_database()

    try:
        accounts = get_gl_accounts_by_period(period)
        entity_accounts = [acc for acc in accounts if acc.entity == entity]

        if not entity_accounts:
            return {"entity": entity, "period": period, "error": "No data found"}

        total = len(entity_accounts)

        # Component 1: Review Completion (30 points)
        reviewed = len(
            [acc for acc in entity_accounts if acc.review_status in ["Reviewed", "Approved"]]
        )
        review_completion_score = (reviewed / total) * 30

        # Component 2: Documentation Completeness (25 points)
        docs_collection = mongo_db["supporting_docs"]
        accounts_with_docs = docs_collection.count_documents({"entity": entity, "period": period})
        doc_completeness_score = min((accounts_with_docs / total) * 25, 25)

        # Component 3: SLA Compliance (25 points)
        # Assume SLA is based on review_deadline (simplified)
        on_time = len([acc for acc in entity_accounts if acc.review_status == "Reviewed"])
        sla_compliance_score = (on_time / total) * 25

        # Component 4: Variance Resolution (20 points)
        # Simplified: accounts with no flags
        no_flags = len([acc for acc in entity_accounts if acc.review_status != "Flagged"])
        variance_resolution_score = (no_flags / total) * 20

        # Calculate overall score
        overall_score = (
            review_completion_score
            + doc_completeness_score
            + sla_compliance_score
            + variance_resolution_score
        )

        # Determine grade
        if overall_score >= 90:
            grade = "A+"
        elif overall_score >= 85:
            grade = "A"
        elif overall_score >= 80:
            grade = "B+"
        elif overall_score >= 75:
            grade = "B"
        elif overall_score >= 70:
            grade = "C+"
        elif overall_score >= 60:
            grade = "C"
        elif overall_score >= 50:
            grade = "D"
        else:
            grade = "F"

        return {
            "entity": entity,
            "period": period,
            "overall_score": round(overall_score, 2),
            "grade": grade,
            "components": {
                "review_completion": round(review_completion_score, 2),
                "documentation_completeness": round(doc_completeness_score, 2),
                "sla_compliance": round(sla_compliance_score, 2),
                "variance_resolution": round(variance_resolution_score, 2),
            },
            "details": {
                "total_accounts": total,
                "reviewed_accounts": reviewed,
                "accounts_with_docs": accounts_with_docs,
                "on_time_reviews": on_time,
                "unflagged_accounts": no_flags,
            },
        }

    except Exception as e:
        return {"error": str(e)}


def get_pending_items_report(entity: str, period: str) -> dict:
    """
    Get report of pending items requiring action.

    Args:
        entity: Entity code
        period: Period (e.g., '2024-03')

    Returns:
        dict: List of pending items with details and priorities
    """
    from .db.mongodb import get_mongo_database

    mongo_db = get_mongo_database()

    try:
        accounts = get_gl_accounts_by_period(period)
        entity_accounts = [acc for acc in accounts if acc.entity == entity]

        # Pending reviews
        pending_reviews = [
            {
                "account_code": acc.account_code,
                "account_name": acc.account_name,
                "balance": float(acc.balance),
                "criticality": acc.criticality,
                "department": acc.department,
                "issue": "Pending Review",
                "priority": "High" if acc.criticality == "Critical" else "Medium",
            }
            for acc in entity_accounts
            if acc.review_status == "Pending"
        ]

        # Missing documentation
        docs_collection = mongo_db["supporting_docs"]
        accounts_with_docs = set(
            doc["account_code"]
            for doc in docs_collection.find(
                {"entity": entity, "period": period}, {"account_code": 1}
            )
        )

        missing_docs = [
            {
                "account_code": acc.account_code,
                "account_name": acc.account_name,
                "balance": float(acc.balance),
                "criticality": acc.criticality,
                "department": acc.department,
                "issue": "Missing Supporting Documents",
                "priority": "High" if acc.criticality == "Critical" else "Medium",
            }
            for acc in entity_accounts
            if acc.account_code not in accounts_with_docs
        ]

        # Flagged items
        flagged_items = [
            {
                "account_code": acc.account_code,
                "account_name": acc.account_name,
                "balance": float(acc.balance),
                "criticality": acc.criticality,
                "department": acc.department,
                "issue": "Flagged for Review",
                "priority": "Critical",
            }
            for acc in entity_accounts
            if acc.review_status == "Flagged"
        ]

        all_pending = pending_reviews + missing_docs + flagged_items

        return {
            "entity": entity,
            "period": period,
            "total_pending": len(all_pending),
            "pending_reviews": len(pending_reviews),
            "missing_docs": len(missing_docs),
            "flagged_items": len(flagged_items),
            "items": sorted(
                all_pending,
                key=lambda x: (
                    0 if x["priority"] == "Critical" else 1 if x["priority"] == "High" else 2
                ),
            ),
        }

    except Exception as e:
        return {"error": str(e)}


def identify_anomalies_ml(entity: str, period: str, threshold: float = 2.0) -> dict:
    """
    Identify anomalous GL account balances using statistical methods.

    Args:
        entity: Entity code
        period: Period (e.g., '2024-03')
        threshold: Z-score threshold for anomaly detection (default: 2.0)

    Returns:
        dict: List of anomalous accounts with scores
    """
    import numpy as np
    from scipy import stats

    try:
        accounts = get_gl_accounts_by_period(period)
        entity_accounts = [acc for acc in accounts if acc.entity == entity]

        if not entity_accounts:
            return {"entity": entity, "period": period, "anomalies": []}

        # Convert to DataFrame
        df = pd.DataFrame(
            [
                {
                    "account_code": acc.account_code,
                    "account_name": acc.account_name,
                    "balance": float(acc.balance),
                    "category": acc.account_category,
                    "department": acc.department,
                }
                for acc in entity_accounts
            ]
        )

        # Group by category and detect anomalies within each category
        anomalies = []

        for category in df["category"].unique():
            category_df = df[df["category"] == category].copy()

            if len(category_df) < 3:  # Need at least 3 samples
                continue

            # Calculate Z-scores
            category_df["z_score"] = np.abs(stats.zscore(category_df["balance"]))

            # Identify anomalies
            category_anomalies = category_df[category_df["z_score"] > threshold]

            for _, row in category_anomalies.iterrows():
                anomalies.append(
                    {
                        "account_code": row["account_code"],
                        "account_name": row["account_name"],
                        "balance": float(row["balance"]),
                        "category": row["category"],
                        "department": row["department"],
                        "z_score": float(row["z_score"]),
                        "anomaly_type": "Statistical Outlier",
                        "severity": "High" if row["z_score"] > 3.0 else "Medium",
                    }
                )

        return {
            "entity": entity,
            "period": period,
            "threshold": threshold,
            "total_accounts": len(df),
            "anomalies_detected": len(anomalies),
            "anomalies": sorted(anomalies, key=lambda x: x["z_score"], reverse=True),
        }

    except Exception as e:
        return {"error": str(e)}


def export_analytics_to_csv(analytics_dict: dict, output_path: str) -> str:
    """
    Export analytics results to CSV file.

    Args:
        analytics_dict: Analytics results dictionary
        output_path: Output file path

    Returns:
        str: Path to exported file
    """
    from pathlib import Path

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Convert nested dict to flat DataFrame
    if "items" in analytics_dict:
        # Pending items report
        df = pd.DataFrame(analytics_dict["items"])
    elif "anomalies" in analytics_dict:
        # Anomaly detection results
        df = pd.DataFrame(analytics_dict["anomalies"])
    elif "significant_variances" in analytics_dict:
        # Variance analysis
        df = pd.DataFrame(analytics_dict["significant_variances"])
    else:
        # Generic key-value export
        df = pd.DataFrame([analytics_dict])

    df.to_csv(output_path, index=False)
    return output_path


def export_analytics_to_excel(analytics_dict: dict, output_path: str) -> str:
    """
    Export analytics results to Excel file with multiple sheets.

    Args:
        analytics_dict: Analytics results dictionary
        output_path: Output file path

    Returns:
        str: Path to exported file
    """
    from pathlib import Path

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Summary sheet
        summary_data = {
            k: v
            for k, v in analytics_dict.items()
            if not isinstance(v, (list, dict)) or k in ["overall", "components"]
        }
        pd.DataFrame([summary_data]).to_excel(writer, sheet_name="Summary", index=False)

        # Detail sheets
        if "items" in analytics_dict:
            pd.DataFrame(analytics_dict["items"]).to_excel(writer, sheet_name="Items", index=False)

        if "anomalies" in analytics_dict:
            pd.DataFrame(analytics_dict["anomalies"]).to_excel(
                writer, sheet_name="Anomalies", index=False
            )

        if "significant_variances" in analytics_dict:
            pd.DataFrame(analytics_dict["significant_variances"]).to_excel(
                writer, sheet_name="Variances", index=False
            )

        if "by_criticality" in analytics_dict:
            pd.DataFrame(analytics_dict["by_criticality"]).T.to_excel(
                writer, sheet_name="By Criticality"
            )

        if "by_category" in analytics_dict:
            pd.DataFrame(analytics_dict["by_category"]).T.to_excel(writer, sheet_name="By Category")

    return output_path


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
