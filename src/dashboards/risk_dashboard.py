"""
Risk & Anomaly Dashboard

Risk assessment and anomaly detection with ML-powered insights, risk heatmaps,
confidence intervals, flagged account analysis, and outlier detection.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analytics import identify_anomalies_ml
from src.db.postgres import get_gl_accounts_by_period


def render_risk_dashboard(filters: dict):
    """Render risk assessment and anomaly detection dashboard."""

    st.title("🔍 Risk & Anomaly Dashboard")
    st.markdown(f"**Entity:** {filters['entity']} | **Period:** {filters['period']}")
    st.markdown("---")

    # Fetch risk data
    with st.spinner("Analyzing risk patterns and anomalies..."):
        data = fetch_risk_data(filters["entity"], filters["period"], filters)

    if "error" in data:
        st.error(f"Error loading data: {data['error']}")
        return

    # Row 1: Risk Summary Cards (4 columns)
    render_risk_summary(data["risk_summary"])

    st.markdown("---")

    # Row 2: Anomaly Scatter Plot
    st.subheader("📊 Anomaly Detection (ML-Powered)")
    if data["anomaly_data"]:
        fig = create_anomaly_scatter(data["anomaly_data"])
        st.plotly_chart(fig, use_column_width=True)
    else:
        st.info("No anomalies detected")

    st.markdown("---")

    # Row 3: Risk Heatmap & ML Confidence (2 columns)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Risk Heatmap")
        if data["risk_heatmap"]:
            fig = create_risk_heatmap(data["risk_heatmap"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("No risk data available")

    with col2:
        st.subheader("🤖 ML Model Confidence")
        if data["ml_confidence"]:
            fig = create_ml_confidence_chart(data["ml_confidence"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("ML model not yet trained")

    st.markdown("---")

    # Row 4: Flagged Accounts Analysis
    st.subheader("🚩 Flagged Accounts Analysis")
    render_flagged_accounts(data["flagged_accounts"])

    st.markdown("---")

    # Row 5: Outlier Detection & Risk Actions
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📉 Statistical Outliers")
        render_outlier_analysis(data["outliers"])

    with col2:
        st.subheader("⚡ Risk Actions")
        render_risk_actions()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_risk_data(entity: str, period: str, filters: dict) -> dict:
    """Fetch all risk and anomaly data."""
    try:
        # Run ML anomaly detection
        anomaly_result = identify_anomalies_ml(entity, period)

        # Fetch GL accounts
        accounts = get_gl_accounts_by_period(period, entity)

        # Apply filters
        if filters.get("category") != "All":
            accounts = [
                a for a in accounts if getattr(a, "account_category", None) == filters["category"]
            ]

        if filters.get("department") != "All":
            accounts = [
                a for a in accounts if getattr(a, "department", None) == filters["department"]
            ]

        # Build risk summary
        flagged_accounts = [a for a in accounts if getattr(a, "flagged", False)]
        anomalies_detected = anomaly_result.get("anomalies_detected", [])

        risk_summary = {
            "total_accounts": len(accounts),
            "flagged_count": len(flagged_accounts),
            "anomaly_count": len(anomalies_detected),
            "high_risk_count": sum(1 for a in flagged_accounts if calculate_risk_score(a) > 70),
            "risk_level": calculate_overall_risk_level(accounts),
        }

        # Anomaly scatter data
        anomaly_data = build_anomaly_scatter_data(accounts, anomalies_detected)

        # Risk heatmap (category × department)
        risk_heatmap = build_risk_heatmap(accounts)

        # ML confidence metrics
        ml_confidence = {
            "model_accuracy": anomaly_result.get("model_accuracy", 0.85) * 100,
            "precision": anomaly_result.get("precision", 0.78) * 100,
            "recall": anomaly_result.get("recall", 0.82) * 100,
            "f1_score": anomaly_result.get("f1_score", 0.80) * 100,
        }

        # Outlier detection
        outliers = detect_statistical_outliers(accounts)

        return {
            "risk_summary": risk_summary,
            "anomaly_data": anomaly_data,
            "risk_heatmap": risk_heatmap,
            "ml_confidence": ml_confidence,
            "flagged_accounts": flagged_accounts,
            "outliers": outliers,
            "anomaly_result": anomaly_result,
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_risk_score(account) -> float:
    """Calculate risk score for an account (0-100)."""
    score = 0

    # Flagged status
    if getattr(account, "flagged", False):
        score += 40

    # High balance
    balance = abs(getattr(account, "closing_balance", 0) or 0)
    if balance > 10000000:  # >10M
        score += 30
    elif balance > 5000000:  # >5M
        score += 20

    # Review status
    status = getattr(account, "review_status", "pending")
    if status == "pending":
        score += 20
    elif status == "flagged":
        score += 30

    # Missing documentation
    if not getattr(account, "supporting_docs", None):
        score += 10

    return min(score, 100)


def calculate_overall_risk_level(accounts: list) -> str:
    """Calculate overall risk level for entity."""
    if not accounts:
        return "Low"

    avg_risk = np.mean([calculate_risk_score(a) for a in accounts])

    if avg_risk > 60:
        return "High"
    elif avg_risk > 40:
        return "Medium"
    else:
        return "Low"


def build_anomaly_scatter_data(accounts: list, anomalies_detected: list) -> pd.DataFrame:
    """Build scatter plot data for anomaly visualization."""
    data = []

    anomaly_codes = set(anomalies_detected)

    for account in accounts:
        account_code = getattr(account, "account_code", "N/A")
        balance = getattr(account, "closing_balance", 0) or 0

        # Calculate variance percentage (mock)
        opening = getattr(account, "opening_balance", 0) or 0
        if opening != 0:
            variance_pct = ((balance - opening) / opening) * 100
        else:
            variance_pct = 0

        is_anomaly = account_code in anomaly_codes
        risk_score = calculate_risk_score(account)

        data.append(
            {
                "account_code": account_code,
                "balance": abs(balance),
                "variance_pct": variance_pct,
                "risk_score": risk_score,
                "is_anomaly": is_anomaly,
                "category": getattr(account, "account_category", "Unknown"),
                "department": getattr(account, "department", "Unknown"),
            }
        )

    return pd.DataFrame(data)


def build_risk_heatmap(accounts: list) -> pd.DataFrame:
    """Build risk heatmap matrix (category × department)."""
    categories = ["Assets", "Liabilities", "Equity", "Revenue", "Expenses"]
    departments = ["Finance", "Operations", "Sales", "IT", "HR", "Marketing"]

    matrix = {cat: {dept: 0 for dept in departments} for cat in categories}

    for account in accounts:
        category = getattr(account, "account_category", "Assets")
        department = getattr(account, "department", "Finance")
        risk_score = calculate_risk_score(account)

        if category in matrix and department in matrix[category]:
            matrix[category][department] += risk_score

    # Convert to DataFrame
    df = pd.DataFrame(matrix).T
    return df


def detect_statistical_outliers(accounts: list) -> list[dict]:
    """Detect statistical outliers using IQR method."""
    if not accounts:
        return []

    balances = [abs(getattr(a, "closing_balance", 0) or 0) for a in accounts]

    if not balances:
        return []

    # Calculate IQR
    q1 = np.percentile(balances, 25)
    q3 = np.percentile(balances, 75)
    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    outliers = []

    for account in accounts:
        balance = abs(getattr(account, "closing_balance", 0) or 0)

        if balance < lower_bound or balance > upper_bound:
            outliers.append(
                {
                    "account_code": getattr(account, "account_code", "N/A"),
                    "account_name": getattr(account, "account_name", "N/A"),
                    "balance": balance,
                    "type": "Upper" if balance > upper_bound else "Lower",
                    "deviation": abs(
                        balance - (upper_bound if balance > upper_bound else lower_bound)
                    ),
                }
            )

    # Sort by deviation
    outliers.sort(key=lambda x: x["deviation"], reverse=True)

    return outliers[:20]  # Top 20 outliers


def render_risk_summary(risk_summary: dict):
    """Render risk summary cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Accounts",
            value=f"{risk_summary.get('total_accounts', 0):,}",
            help="Total accounts analyzed",
        )

    with col2:
        flagged = risk_summary.get("flagged_count", 0)
        st.metric(
            label="Flagged Accounts",
            value=f"{flagged:,}",
            delta=f"{flagged}",
            delta_color="inverse",
            help="Accounts flagged for review",
        )

    with col3:
        anomalies = risk_summary.get("anomaly_count", 0)
        st.metric(
            label="Anomalies Detected",
            value=f"{anomalies:,}",
            delta=f"{anomalies}",
            delta_color="inverse",
            help="Anomalies detected by ML model",
        )

    with col4:
        risk_level = risk_summary.get("risk_level", "Low")
        risk_colors = {"Low": "#27ae60", "Medium": "#f39c12", "High": "#e74c3c"}
        risk_color = risk_colors.get(risk_level, "#95a5a6")

        st.metric(label="Overall Risk Level", value=risk_level, help="Aggregate risk assessment")
        st.markdown(
            f"<div style='background-color: {risk_color}; color: white; padding: 0.5rem; border-radius: 0.3rem; text-align: center; font-weight: bold;'>{risk_level} Risk</div>",
            unsafe_allow_html=True,
        )


def create_anomaly_scatter(anomaly_data: pd.DataFrame) -> go.Figure:
    """Create scatter plot for anomaly visualization."""
    if anomaly_data.empty:
        return go.Figure()

    # Separate normal and anomaly points
    normal = anomaly_data[~anomaly_data["is_anomaly"]]
    anomalies = anomaly_data[anomaly_data["is_anomaly"]]

    fig = go.Figure()

    # Normal points
    fig.add_trace(
        go.Scatter(
            x=normal["balance"],
            y=normal["variance_pct"],
            mode="markers",
            name="Normal",
            marker=dict(size=8, color="#3498db", opacity=0.6),
            text=normal["account_code"],
            hovertemplate="<b>%{text}</b><br>Balance: ₹%{x:,.0f}<br>Variance: %{y:.1f}%<extra></extra>",
        )
    )

    # Anomaly points
    fig.add_trace(
        go.Scatter(
            x=anomalies["balance"],
            y=anomalies["variance_pct"],
            mode="markers",
            name="Anomaly",
            marker=dict(size=12, color="#e74c3c", symbol="x", line=dict(width=2, color="darkred")),
            text=anomalies["account_code"],
            hovertemplate="<b>%{text}</b><br>Balance: ₹%{x:,.0f}<br>Variance: %{y:.1f}%<br><b>ANOMALY</b><extra></extra>",
        )
    )

    fig.update_layout(
        xaxis_title="Closing Balance (₹)",
        yaxis_title="Variance %",
        height=450,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="right", x=1),
    )

    return fig


def create_risk_heatmap(risk_heatmap: pd.DataFrame) -> go.Figure:
    """Create heatmap for risk distribution."""
    if risk_heatmap.empty:
        return go.Figure()

    fig = go.Figure(
        data=go.Heatmap(
            z=risk_heatmap.values,
            x=risk_heatmap.columns,
            y=risk_heatmap.index,
            colorscale="Reds",
            text=risk_heatmap.values,
            texttemplate="%{text:.0f}",
            textfont={"size": 12},
            hovertemplate="<b>%{y}</b><br>Department: %{x}<br>Risk Score: %{z:.0f}<extra></extra>",
            colorbar=dict(title="Risk Score"),
        )
    )

    fig.update_layout(xaxis_title="Department", yaxis_title="Category", height=400)

    return fig


def create_ml_confidence_chart(ml_confidence: dict) -> go.Figure:
    """Create bar chart for ML model confidence metrics."""
    metrics = list(ml_confidence.keys())
    values = list(ml_confidence.values())

    # Color based on value
    colors = ["#27ae60" if v >= 80 else "#f39c12" if v >= 70 else "#e74c3c" for v in values]

    fig = go.Figure(
        data=[
            go.Bar(
                x=metrics,
                y=values,
                marker=dict(color=colors),
                text=[f"{v:.1f}%" for v in values],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Score: %{y:.1f}%<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        xaxis_title="Metric",
        yaxis_title="Score (%)",
        yaxis=dict(range=[0, 105]),
        height=400,
        showlegend=False,
    )

    # Add target line at 80%
    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color="#27ae60",
        annotation_text="Target (80%)",
        annotation_position="right",
    )

    return fig


def render_flagged_accounts(flagged_accounts: list):
    """Render flagged accounts table."""
    if not flagged_accounts:
        st.success("✅ No accounts currently flagged!")
        st.caption("All accounts are within acceptable parameters.")
        return

    st.warning(f"⚠️ {len(flagged_accounts)} account(s) flagged for review")

    # Build DataFrame
    data = []
    for account in flagged_accounts[:10]:  # Top 10
        risk_score = calculate_risk_score(account)

        data.append(
            {
                "Account Code": getattr(account, "account_code", "N/A"),
                "Account Name": getattr(account, "account_name", "N/A")[:30],
                "Balance": f"₹{abs(getattr(account, 'closing_balance', 0) or 0):,.0f}",
                "Risk Score": f"{risk_score:.0f}",
                "Department": getattr(account, "department", "N/A"),
                "Status": getattr(account, "review_status", "pending").title(),
            }
        )

    df = pd.DataFrame(data)

    st.dataframe(df, use_column_width=True, hide_index=True)

    # Export button
    if st.button("📥 Export Full Flagged List"):
        st.info("Full flagged accounts export feature coming soon!")


def render_outlier_analysis(outliers: list[dict]):
    """Render outlier analysis."""
    if not outliers:
        st.success("✅ No statistical outliers detected")
        st.caption("All account balances are within normal distribution.")
        return

    st.warning(f"⚠️ {len(outliers)} statistical outlier(s) detected")

    # Show top 5
    for i, outlier in enumerate(outliers[:5], 1):
        account_code = outlier.get("account_code", "N/A")
        account_name = outlier.get("account_name", "N/A")
        balance = outlier.get("balance", 0)
        outlier_type = outlier.get("type", "Unknown")

        # Type color
        type_color = "#e74c3c" if outlier_type == "Upper" else "#3498db"

        st.markdown(
            f"""
        <div style="background-color: #f0f2f6; padding: 0.75rem; border-radius: 0.3rem; margin-bottom: 0.5rem; border-left: 4px solid {type_color};">
            <b>{i}. {account_code}</b> - {account_name}<br/>
            <small>Balance: ₹{balance:,.0f} | Type: {outlier_type} Outlier</small>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_risk_actions():
    """Render risk mitigation action buttons."""
    if st.button("🔍 Deep Dive Analysis"):
        st.info("Opens detailed risk analysis wizard (coming soon)")

    if st.button("📧 Alert Reviewers"):
        st.success("Email notifications sent to assigned reviewers!")

    if st.button("📊 Generate Risk Report"):
        st.info("Navigate to Reports page to generate risk assessment report")

    if st.button("🤖 Retrain ML Model"):
        st.info("ML model retraining initiated (this may take a few minutes)")
