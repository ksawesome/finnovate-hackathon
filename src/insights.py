"""Insights generation module."""

from datetime import datetime

import pandas as pd


def generate_insights(df: pd.DataFrame) -> list:
    """
    Generate key insights from data.

    Args:
        df: Analyzed DataFrame.

    Returns:
        list: List of insight strings.
    """
    insights = []
    # Placeholder logic
    total_balance = df.get("balance", pd.Series()).sum()
    insights.append(f"Total balance: {total_balance}")
    return insights


def drill_down_analysis(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Perform drill-down analysis.

    Args:
        df: DataFrame.
        filters: Dict of filters.

    Returns:
        pd.DataFrame: Filtered data.
    """
    for col, val in filters.items():
        df = df[df[col] == val]
    return df


def generate_proactive_insights(entity: str, period: str) -> list[dict]:
    """
    Generate proactive insights based on analytics and patterns.

    Args:
        entity: Entity code
        period: Period (e.g., '2024-03')

    Returns:
        list: List of insight dictionaries with type, priority, and message
    """
    from .analytics import (
        calculate_gl_hygiene_score,
        calculate_review_status_summary,
        get_pending_items_report,
        identify_anomalies_ml,
    )

    insights = []

    try:
        # Insight 1: Hygiene Score Assessment
        hygiene_data = calculate_gl_hygiene_score(entity, period)
        if "overall_score" in hygiene_data:
            score = hygiene_data["overall_score"]
            grade = hygiene_data["grade"]

            if score < 60:
                insights.append(
                    {
                        "type": "quality_alert",
                        "priority": "critical",
                        "title": "Low GL Hygiene Score",
                        "message": f"GL hygiene score is {score:.0f}/100 (Grade: {grade}). Immediate action required to improve review completion and documentation.",
                        "action": "Review pending items and ensure all supporting documents are uploaded.",
                    }
                )
            elif score < 80:
                insights.append(
                    {
                        "type": "quality_warning",
                        "priority": "high",
                        "title": "Moderate GL Hygiene Score",
                        "message": f"GL hygiene score is {score:.0f}/100 (Grade: {grade}). Consider improving documentation and SLA compliance.",
                        "action": "Focus on accounts with missing documentation.",
                    }
                )
            else:
                insights.append(
                    {
                        "type": "quality_good",
                        "priority": "info",
                        "title": "Good GL Hygiene Score",
                        "message": f"GL hygiene score is {score:.0f}/100 (Grade: {grade}). Maintain current practices.",
                        "action": "Continue monitoring and addressing flagged items promptly.",
                    }
                )

        # Insight 2: Review Status
        review_data = calculate_review_status_summary(entity, period)
        if "overall" in review_data:
            completion = review_data["overall"]["completion_pct"]
            pending = review_data["overall"]["pending"]

            if completion < 50:
                insights.append(
                    {
                        "type": "completion_alert",
                        "priority": "critical",
                        "title": "Low Review Completion Rate",
                        "message": f"Only {completion:.1f}% of accounts reviewed. {pending} accounts still pending.",
                        "action": "Assign additional reviewers or prioritize critical accounts.",
                    }
                )
            elif pending > 0:
                insights.append(
                    {
                        "type": "completion_progress",
                        "priority": "medium",
                        "title": "Reviews In Progress",
                        "message": f"{completion:.1f}% complete with {pending} accounts remaining.",
                        "action": f"Focus on completing reviews for the remaining {pending} accounts.",
                    }
                )

        # Insight 3: Anomaly Detection
        anomaly_data = identify_anomalies_ml(entity, period, threshold=2.0)
        if anomaly_data.get("anomalies_detected", 0) > 0:
            count = anomaly_data["anomalies_detected"]
            top_anomaly = anomaly_data["anomalies"][0] if anomaly_data["anomalies"] else None

            if top_anomaly:
                insights.append(
                    {
                        "type": "anomaly_detected",
                        "priority": "high",
                        "title": f"{count} Anomalous Account(s) Detected",
                        "message": f"Account {top_anomaly['account_code']} ({top_anomaly['account_name']}) shows unusual balance (Z-score: {top_anomaly['z_score']:.2f}).",
                        "action": "Investigate anomalous accounts for potential errors or irregularities.",
                    }
                )

        # Insight 4: Pending Items
        pending_data = get_pending_items_report(entity, period)
        critical_pending = len(
            [item for item in pending_data.get("items", []) if item["priority"] == "Critical"]
        )

        if critical_pending > 0:
            insights.append(
                {
                    "type": "critical_items",
                    "priority": "critical",
                    "title": f"{critical_pending} Critical Item(s) Pending",
                    "message": f"There are {critical_pending} critical items requiring immediate attention.",
                    "action": "Address critical flagged accounts and missing documentation immediately.",
                }
            )

        # Insight 5: Documentation Gaps
        missing_docs = pending_data.get("missing_docs", 0)
        if missing_docs > 10:
            insights.append(
                {
                    "type": "documentation_gap",
                    "priority": "high",
                    "title": "Significant Documentation Gaps",
                    "message": f"{missing_docs} accounts missing supporting documentation.",
                    "action": "Coordinate with department heads to ensure timely document uploads.",
                }
            )

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "info": 3}
        insights.sort(key=lambda x: priority_order.get(x["priority"], 4))

    except Exception as e:
        insights.append(
            {
                "type": "error",
                "priority": "medium",
                "title": "Insight Generation Error",
                "message": f"Error generating insights: {e!s}",
                "action": "Check data availability and try again.",
            }
        )

    return insights


def generate_executive_summary(entity: str, period: str) -> dict:
    """
    Generate executive summary for leadership.

    Args:
        entity: Entity code
        period: Period (e.g., '2024-03')

    Returns:
        dict: Executive summary with key metrics and recommendations
    """
    from .analytics import (
        calculate_gl_hygiene_score,
        calculate_review_status_summary,
        get_pending_items_report,
        identify_anomalies_ml,
    )
    from .db import get_postgres_session
    from .db.postgres import get_gl_accounts_by_period

    session = get_postgres_session()

    try:
        # Get all accounts for entity
        accounts = get_gl_accounts_by_period(period, session=session)
        entity_accounts = [acc for acc in accounts if acc.entity == entity]

        # Calculate key metrics
        total_balance = sum(float(acc.balance) for acc in entity_accounts)
        total_accounts = len(entity_accounts)

        # Category breakdown
        categories = {}
        for acc in entity_accounts:
            cat = acc.category
            categories[cat] = categories.get(cat, 0) + float(acc.balance)

        # Get comprehensive metrics
        hygiene = calculate_gl_hygiene_score(entity, period)
        review_status = calculate_review_status_summary(entity, period)
        anomalies = identify_anomalies_ml(entity, period)
        pending = get_pending_items_report(entity, period)

        # Determine overall status
        hygiene_score = hygiene.get("overall_score", 0)
        completion_pct = review_status.get("overall", {}).get("completion_pct", 0)

        if hygiene_score >= 85 and completion_pct >= 90:
            overall_status = "Excellent"
            status_color = "green"
        elif hygiene_score >= 70 and completion_pct >= 75:
            overall_status = "Good"
            status_color = "blue"
        elif hygiene_score >= 60 and completion_pct >= 60:
            overall_status = "Fair"
            status_color = "yellow"
        else:
            overall_status = "Needs Attention"
            status_color = "red"

        # Key highlights
        highlights = []
        if completion_pct >= 90:
            highlights.append(f"✅ {completion_pct:.0f}% review completion rate")
        if hygiene_score >= 80:
            highlights.append(f"✅ Strong GL hygiene score ({hygiene_score:.0f}/100)")
        if anomalies.get("anomalies_detected", 0) == 0:
            highlights.append("✅ No anomalies detected")

        # Areas of concern
        concerns = []
        if completion_pct < 70:
            concerns.append(f"⚠️ Low review completion ({completion_pct:.0f}%)")
        if hygiene_score < 70:
            concerns.append(f"⚠️ Below-target hygiene score ({hygiene_score:.0f}/100)")
        if pending.get("flagged_items", 0) > 0:
            concerns.append(f"⚠️ {pending['flagged_items']} flagged items need resolution")
        if anomalies.get("anomalies_detected", 0) > 0:
            concerns.append(f"⚠️ {anomalies['anomalies_detected']} anomalous accounts detected")

        # Recommendations
        recommendations = []
        if completion_pct < 80:
            recommendations.append("Accelerate review process for pending accounts")
        if pending.get("missing_docs", 0) > 5:
            recommendations.append("Prioritize uploading missing supporting documentation")
        if pending.get("flagged_items", 0) > 0:
            recommendations.append("Resolve all flagged items before period close")
        if anomalies.get("anomalies_detected", 0) > 0:
            recommendations.append("Investigate anomalous accounts for potential errors")
        if hygiene_score < 80:
            recommendations.append("Improve SLA compliance and documentation completeness")

        return {
            "entity": entity,
            "period": period,
            "generated_at": datetime.utcnow().isoformat(),
            "overall_status": overall_status,
            "status_color": status_color,
            "key_metrics": {
                "total_accounts": total_accounts,
                "total_balance": total_balance,
                "hygiene_score": hygiene_score,
                "completion_rate": completion_pct,
                "pending_reviews": review_status.get("overall", {}).get("pending", 0),
                "flagged_items": pending.get("flagged_items", 0),
                "anomalies": anomalies.get("anomalies_detected", 0),
            },
            "category_breakdown": categories,
            "highlights": highlights,
            "concerns": concerns,
            "recommendations": recommendations,
            "summary_text": f"{entity} for {period}: {overall_status}. {len(highlights)} positive indicators, {len(concerns)} areas needing attention.",
        }

    finally:
        session.close()


def generate_drill_down_report(
    entity: str,
    period: str,
    dimension: str,  # 'category', 'department', 'criticality', 'review_status'
    value: str,
) -> dict:
    """
    Generate drill-down report for specific dimension and value.

    Args:
        entity: Entity code
        period: Period
        dimension: Dimension to drill down on
        value: Specific value within dimension

    Returns:
        dict: Drill-down analysis with filtered accounts and metrics
    """
    from .db import get_postgres_session
    from .db.postgres import get_gl_accounts_by_period

    session = get_postgres_session()

    try:
        accounts = get_gl_accounts_by_period(period, session=session)

        # Filter by entity and dimension
        filtered_accounts = [
            acc
            for acc in accounts
            if acc.entity == entity and getattr(acc, dimension, None) == value
        ]

        if not filtered_accounts:
            return {
                "entity": entity,
                "period": period,
                "dimension": dimension,
                "value": value,
                "error": "No accounts found matching criteria",
            }

        # Convert to DataFrame
        df = pd.DataFrame(
            [
                {
                    "account_code": acc.account_code,
                    "account_name": acc.account_name,
                    "balance": float(acc.balance),
                    "review_status": acc.review_status,
                    "criticality": acc.criticality,
                    "category": acc.category,
                    "department": acc.department,
                }
                for acc in filtered_accounts
            ]
        )

        # Calculate metrics
        total_balance = df["balance"].sum()
        account_count = len(df)
        avg_balance = df["balance"].mean()

        # Status distribution
        status_counts = df["review_status"].value_counts().to_dict()

        # Top accounts by balance
        top_accounts = df.nlargest(10, "balance")[
            ["account_code", "account_name", "balance", "review_status"]
        ].to_dict("records")

        return {
            "entity": entity,
            "period": period,
            "dimension": dimension,
            "value": value,
            "metrics": {
                "account_count": account_count,
                "total_balance": float(total_balance),
                "average_balance": float(avg_balance),
                "reviewed_count": status_counts.get("Reviewed", 0)
                + status_counts.get("Approved", 0),
                "pending_count": status_counts.get("Pending", 0),
                "flagged_count": status_counts.get("Flagged", 0),
            },
            "status_distribution": status_counts,
            "top_accounts": top_accounts,
            "all_accounts": df.to_dict("records"),
        }

    finally:
        session.close()


def compare_multi_period(
    entity: str,
    periods: list[str],  # e.g., ['2024-01', '2024-02', '2024-03']
) -> dict:
    """
    Compare metrics across multiple periods to identify trends.

    Args:
        entity: Entity code
        periods: List of periods to compare

    Returns:
        dict: Multi-period comparison with trends
    """
    from .analytics import calculate_gl_hygiene_score, calculate_review_status_summary
    from .db import get_postgres_session
    from .db.postgres import get_gl_accounts_by_period

    session = get_postgres_session()

    try:
        results = []

        for period in periods:
            accounts = get_gl_accounts_by_period(period, session=session)
            entity_accounts = [acc for acc in accounts if acc.entity == entity]

            if not entity_accounts:
                results.append(
                    {
                        "period": period,
                        "total_accounts": 0,
                        "total_balance": 0,
                        "hygiene_score": 0,
                        "completion_rate": 0,
                    }
                )
                continue

            total_balance = sum(float(acc.balance) for acc in entity_accounts)
            total_accounts = len(entity_accounts)

            # Get metrics
            hygiene = calculate_gl_hygiene_score(entity, period)
            review_status = calculate_review_status_summary(entity, period)

            results.append(
                {
                    "period": period,
                    "total_accounts": total_accounts,
                    "total_balance": float(total_balance),
                    "hygiene_score": hygiene.get("overall_score", 0),
                    "completion_rate": review_status.get("overall", {}).get("completion_pct", 0),
                }
            )

        # Calculate trends
        df = pd.DataFrame(results)

        trends = {}
        for metric in ["total_balance", "hygiene_score", "completion_rate"]:
            if len(df) >= 2:
                values = df[metric].tolist()
                trend = (
                    "increasing"
                    if values[-1] > values[0]
                    else "decreasing" if values[-1] < values[0] else "stable"
                )
                change = values[-1] - values[0] if len(values) > 0 else 0
                change_pct = (change / values[0] * 100) if values[0] != 0 else 0
            else:
                trend = "insufficient_data"
                change = 0
                change_pct = 0

            trends[metric] = {
                "trend": trend,
                "change": float(change),
                "change_pct": float(change_pct),
            }

        return {
            "entity": entity,
            "periods": periods,
            "period_count": len(periods),
            "period_data": results,
            "trends": trends,
            "summary": f"Multi-period analysis for {entity}: Balance {trends['total_balance']['trend']}, Hygiene {trends['hygiene_score']['trend']}, Completion {trends['completion_rate']['trend']}",
        }

    finally:
        session.close()
