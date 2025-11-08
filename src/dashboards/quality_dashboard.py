"""
Quality & Hygiene Dashboard

GL data quality assessment with hygiene scores, component radar charts,
quality trends, issue breakdowns, and completeness metrics.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analytics import calculate_gl_hygiene_score
from src.db.postgres import get_gl_accounts_by_period


def render_quality_dashboard(filters: dict):
    """Render quality and hygiene assessment dashboard."""

    st.title("✨ Quality & Hygiene Dashboard")
    st.markdown(f"**Entity:** {filters['entity']} | **Period:** {filters['period']}")
    st.markdown("---")

    # Fetch quality data
    with st.spinner("Analyzing data quality..."):
        data = fetch_quality_data(filters["entity"], filters["period"], filters)

    if "error" in data:
        st.error(f"Error loading data: {data['error']}")
        return

    # Row 1: Overall Hygiene Gauge & Score Breakdown
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Overall Hygiene Score")
        fig = create_hygiene_gauge(data["hygiene_score"])
        st.plotly_chart(fig, use_column_width=True)

    with col2:
        st.subheader("📊 Component Scores")
        render_component_scores(data["component_scores"])

    st.markdown("---")

    # Row 2: Component Radar Chart
    st.subheader("🕸️ Quality Component Radar")
    if data["component_scores"]:
        fig = create_component_radar_chart(data["component_scores"])
        st.plotly_chart(fig, use_column_width=True)
    else:
        st.info("No component data available")

    st.markdown("---")

    # Row 3: Quality Trends & Issue Breakdown (2 columns)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Quality Trends")
        if data["trend_data"]:
            fig = create_quality_trend_chart(data["trend_data"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("Insufficient historical data")

    with col2:
        st.subheader("🌻 Issue Breakdown (Sunburst)")
        if data["issue_data"]:
            fig = create_issue_sunburst(data["issue_data"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("No quality issues detected")

    st.markdown("---")

    # Row 4: Completeness Metrics
    st.subheader("✅ Data Completeness Analysis")
    render_completeness_metrics(data["completeness"])

    st.markdown("---")

    # Row 5: Quality Recommendations
    st.subheader("💡 Quality Improvement Recommendations")
    render_quality_recommendations(data["recommendations"])


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_quality_data(entity: str, period: str, filters: dict) -> dict:
    """Fetch all quality assessment data."""
    try:
        # Calculate hygiene score
        hygiene_result = calculate_gl_hygiene_score(entity, period)

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

        # Extract component scores
        component_scores = hygiene_result.get("component_scores", {})

        # Analyze completeness
        completeness = analyze_completeness(accounts)

        # Detect quality issues
        issue_data = detect_quality_issues(accounts)

        # Generate quality trends (mock - would query historical data)
        trend_data = generate_quality_trends(entity, period)

        # Generate recommendations
        recommendations = generate_quality_recommendations(hygiene_result, completeness, issue_data)

        return {
            "hygiene_score": hygiene_result,
            "component_scores": component_scores,
            "completeness": completeness,
            "issue_data": issue_data,
            "trend_data": trend_data,
            "recommendations": recommendations,
        }
    except Exception as e:
        return {"error": str(e)}


def analyze_completeness(accounts: list) -> dict:
    """Analyze data completeness across fields."""
    total_accounts = len(accounts)

    if total_accounts == 0:
        return {}

    # Check critical fields
    fields = {
        "account_code": 0,
        "account_name": 0,
        "account_category": 0,
        "department": 0,
        "opening_balance": 0,
        "closing_balance": 0,
        "reviewer": 0,
        "supporting_docs": 0,
    }

    for account in accounts:
        for field in fields:
            value = getattr(account, field, None)

            # Check if field is complete
            if value is not None and value != "" and value != 0:
                fields[field] += 1

    # Calculate percentages
    completeness = {}
    for field, count in fields.items():
        completeness[field] = {
            "count": count,
            "percentage": (count / total_accounts * 100) if total_accounts > 0 else 0,
        }

    return completeness


def detect_quality_issues(accounts: list) -> dict:
    """Detect and categorize quality issues."""
    issues = {
        "Missing Data": {
            "Missing Account Name": 0,
            "Missing Category": 0,
            "Missing Department": 0,
            "Missing Reviewer": 0,
        },
        "Data Inconsistency": {"Balance Mismatch": 0, "Invalid Category": 0, "Duplicate Code": 0},
        "Documentation": {"Missing Supporting Docs": 0, "Incomplete Documentation": 0},
    }

    account_codes_seen = set()

    for account in accounts:
        # Missing data checks
        if not getattr(account, "account_name", None):
            issues["Missing Data"]["Missing Account Name"] += 1

        if not getattr(account, "account_category", None):
            issues["Missing Data"]["Missing Category"] += 1

        if not getattr(account, "department", None):
            issues["Missing Data"]["Missing Department"] += 1

        if not getattr(account, "reviewer", None):
            issues["Missing Data"]["Missing Reviewer"] += 1

        # Inconsistency checks
        opening = getattr(account, "opening_balance", 0) or 0
        debit = getattr(account, "debit_amount", 0) or 0
        credit = getattr(account, "credit_amount", 0) or 0
        closing = getattr(account, "closing_balance", 0) or 0

        expected_closing = opening + debit - credit
        if abs(closing - expected_closing) > 0.01:  # Tolerance for rounding
            issues["Data Inconsistency"]["Balance Mismatch"] += 1

        # Duplicate code check
        account_code = getattr(account, "account_code", None)
        if account_code in account_codes_seen:
            issues["Data Inconsistency"]["Duplicate Code"] += 1
        else:
            account_codes_seen.add(account_code)

        # Documentation checks
        if not getattr(account, "supporting_docs", None):
            issues["Documentation"]["Missing Supporting Docs"] += 1

    return issues


def generate_quality_trends(entity: str, period: str) -> list[dict]:
    """Generate quality score trends over time (mock)."""
    # In production, would query historical hygiene scores
    # For now, generate sample trend data

    try:
        year, month = map(int, period.split("-"))
    except:
        return []

    trends = []
    base_score = 75

    for i in range(6):
        month_offset = month - i
        year_offset = year

        while month_offset <= 0:
            month_offset += 12
            year_offset -= 1

        # Mock score with slight improvement over time
        score = base_score + (i * 2) + (i % 2)  # Gradually improving

        trends.append(
            {
                "period": f"{year_offset}-{month_offset:02d}",
                "score": min(score, 100),  # Cap at 100
            }
        )

    return list(reversed(trends))


def generate_quality_recommendations(
    hygiene_result: dict, completeness: dict, issue_data: dict
) -> list[dict]:
    """Generate quality improvement recommendations."""
    recommendations = []

    # Overall score check
    overall_score = hygiene_result.get("overall_score", 0)
    if overall_score < 80:
        recommendations.append(
            {
                "priority": "High",
                "category": "Overall Quality",
                "issue": f"Overall hygiene score is {overall_score:.1f}% (below 80% threshold)",
                "action": "Focus on improving low-scoring components to boost overall quality",
            }
        )

    # Component scores check
    component_scores = hygiene_result.get("component_scores", {})
    for component, score in component_scores.items():
        if score < 70:
            recommendations.append(
                {
                    "priority": "High",
                    "category": "Component Quality",
                    "issue": f"{component} score is {score:.1f}% (below 70%)",
                    "action": f"Review and improve {component} data quality",
                }
            )

    # Completeness checks
    for field, data in completeness.items():
        percentage = data.get("percentage", 0)
        if percentage < 90:
            recommendations.append(
                {
                    "priority": "Medium",
                    "category": "Data Completeness",
                    "issue": f"{field} is only {percentage:.1f}% complete",
                    "action": f"Fill in missing {field} values for all accounts",
                }
            )

    # Issue checks
    for category, subcategories in issue_data.items():
        for issue_type, count in subcategories.items():
            if count > 10:
                recommendations.append(
                    {
                        "priority": "High" if count > 25 else "Medium",
                        "category": category,
                        "issue": f"{count} accounts have {issue_type}",
                        "action": f"Address {issue_type} issues systematically",
                    }
                )

    # Sort by priority
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recommendations[:10]  # Top 10 recommendations


def create_hygiene_gauge(hygiene_score: dict) -> go.Figure:
    """Create gauge chart for overall hygiene score."""
    overall_score = hygiene_score.get("overall_score", 0)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=overall_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Overall Hygiene Score", "font": {"size": 24}},
            delta={"reference": 80, "increasing": {"color": "#27ae60"}},
            gauge={
                "axis": {"range": [None, 100], "tickwidth": 1},
                "bar": {"color": "#3498db"},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, 50], "color": "#e74c3c"},
                    {"range": [50, 70], "color": "#f39c12"},
                    {"range": [70, 85], "color": "#f1c40f"},
                    {"range": [85, 100], "color": "#27ae60"},
                ],
                "threshold": {
                    "line": {"color": "darkgreen", "width": 4},
                    "thickness": 0.75,
                    "value": 90,
                },
            },
        )
    )

    fig.update_layout(height=350, margin=dict(t=50, b=50, l=50, r=50))

    return fig


def render_component_scores(component_scores: dict):
    """Render component scores as progress bars."""
    if not component_scores:
        st.info("No component scores available")
        return

    for component, score in component_scores.items():
        # Color based on score
        if score >= 85:
            color = "#27ae60"  # Green
        elif score >= 70:
            color = "#f39c12"  # Orange
        else:
            color = "#e74c3c"  # Red

        st.markdown(f"**{component}**")
        st.progress(score / 100)
        st.caption(f"{score:.1f}%")


def create_component_radar_chart(component_scores: dict) -> go.Figure:
    """Create radar chart for component scores."""
    if not component_scores:
        return go.Figure()

    categories = list(component_scores.keys())
    values = list(component_scores.values())

    # Close the radar
    categories += [categories[0]]
    values += [values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(52, 152, 219, 0.3)",
            line=dict(color="#3498db", width=3),
            name="Current Score",
        )
    )

    # Add target line at 90%
    target_values = [90] * len(categories)

    fig.add_trace(
        go.Scatterpolar(
            r=target_values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(46, 204, 113, 0.1)",
            line=dict(color="#27ae60", width=2, dash="dash"),
            name="Target (90%)",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )

    return fig


def create_quality_trend_chart(trend_data: list[dict]) -> go.Figure:
    """Create line chart for quality trends over time."""
    if not trend_data:
        return go.Figure()

    periods = [t["period"] for t in trend_data]
    scores = [t["score"] for t in trend_data]

    fig = go.Figure()

    # Add line
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=scores,
            mode="lines+markers",
            name="Hygiene Score",
            line=dict(color="#3498db", width=3),
            marker=dict(size=10),
            hovertemplate="<b>Period: %{x}</b><br>Score: %{y:.1f}%<extra></extra>",
        )
    )

    # Add target line
    fig.add_hline(
        y=90,
        line_dash="dash",
        line_color="#27ae60",
        annotation_text="Target (90%)",
        annotation_position="right",
    )

    fig.update_layout(
        xaxis_title="Period",
        yaxis_title="Hygiene Score (%)",
        yaxis=dict(range=[0, 105]),
        height=350,
        showlegend=False,
    )

    return fig


def create_issue_sunburst(issue_data: dict) -> go.Figure:
    """Create sunburst chart for issue hierarchy."""
    if not issue_data:
        return go.Figure()

    # Build sunburst data
    labels = ["All Issues"]
    parents = [""]
    values = [0]

    for category, subcategories in issue_data.items():
        category_total = sum(subcategories.values())

        if category_total == 0:
            continue

        labels.append(category)
        parents.append("All Issues")
        values.append(category_total)

        for issue_type, count in subcategories.items():
            if count > 0:
                labels.append(issue_type)
                parents.append(category)
                values.append(count)

    # Update total
    values[0] = sum(v for i, v in enumerate(values) if i > 0 and parents[i] == "All Issues")

    fig = go.Figure(
        go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=["#3498db", "#e74c3c", "#f39c12", "#9b59b6"] * 10,
                line=dict(color="white", width=2),
            ),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
        )
    )

    fig.update_layout(height=400, margin=dict(t=10, b=10, l=10, r=10))

    return fig


def render_completeness_metrics(completeness: dict):
    """Render completeness metrics table."""
    if not completeness:
        st.info("No completeness data available")
        return

    # Build DataFrame
    data = []
    for field, stats in completeness.items():
        percentage = stats.get("percentage", 0)
        count = stats.get("count", 0)

        # Status icon
        if percentage >= 95:
            status = "✅"
        elif percentage >= 80:
            status = "⚠️"
        else:
            status = "❌"

        data.append(
            {
                "Status": status,
                "Field": field.replace("_", " ").title(),
                "Complete": count,
                "Percentage": f"{percentage:.1f}%",
            }
        )

    df = pd.DataFrame(data)

    st.dataframe(df, use_column_width=True, hide_index=True)


def render_quality_recommendations(recommendations: list[dict]):
    """Render quality improvement recommendations."""
    if not recommendations:
        st.success("✅ No quality issues detected! Data quality is excellent.")
        return

    st.warning(f"⚠️ {len(recommendations)} recommendation(s) for quality improvement")

    for i, rec in enumerate(recommendations[:5], 1):  # Top 5
        priority = rec.get("priority", "Medium")
        category = rec.get("category", "General")
        issue = rec.get("issue", "N/A")
        action = rec.get("action", "N/A")

        # Priority color
        priority_colors = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#3498db"}
        color = priority_colors.get(priority, "#95a5a6")

        # Priority icon
        priority_icons = {"High": "🔴", "Medium": "⚠️", "Low": "💡"}
        icon = priority_icons.get(priority, "•")

        with st.expander(f"{i}. {icon} {category} ({priority} Priority)"):
            st.markdown(f"**Issue:** {issue}")
            st.markdown(f"**Recommended Action:** {action}")

            # Action button
            if st.button(f"Mark as Addressed #{i}", key=f"rec_{i}"):
                st.success(f"Recommendation #{i} marked as addressed!")
