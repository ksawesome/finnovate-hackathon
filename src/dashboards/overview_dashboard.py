"""
Overview Dashboard

Executive summary view with key metrics, status distribution, department performance,
pending items, critical alerts, activity timeline, and proactive insights.
"""

from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from src.analytics import (
    calculate_gl_hygiene_score,
    calculate_review_status_summary,
    get_pending_items_report,
    perform_analytics,
)
from src.db.mongodb import get_audit_trail_collection
from src.db.postgres import get_gl_accounts_by_period
from src.insights import generate_executive_summary, generate_proactive_insights


def render_overview_dashboard(filters: dict):
    """Render main overview dashboard with executive summary."""

    st.title("📊 Overview Dashboard")
    st.markdown(f"**Entity:** {filters['entity']} | **Period:** {filters['period']}")
    st.markdown("---")

    # Fetch all data
    with st.spinner("Loading dashboard data..."):
        data = fetch_overview_data(filters["entity"], filters["period"], filters)

    if "error" in data:
        st.error(f"Error loading data: {data['error']}")
        return

    # Check if data has required keys
    if not data or "kpis" not in data:
        st.warning("No data available for the selected filters.")
        return

    # Row 1: KPI Cards (4 columns)
    render_kpi_cards(data.get("kpis", {}))

    st.markdown("---")

    # Row 2: Charts (2 columns)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Review Status Distribution")
        if data["status_data"]:
            fig = create_status_distribution_chart(data["status_data"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("No status data available")

    with col2:
        st.subheader("🏢 Department Performance")
        if data["dept_stats"]:
            fig = create_department_performance_chart(data["dept_stats"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("No department data available")

    st.markdown("---")

    # Row 3: Pending Items & Critical Alerts (2 columns)
    col1, col2 = st.columns(2)

    with col1:
        render_pending_card("Pending Reviews", data["pending_items"].get("pending_reviews", []))

    with col2:
        render_critical_card(data["kpis"].get("flagged_count", 0))

    st.markdown("---")

    # Row 4: Activity Timeline & Insights (2 columns)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Recent Activity")
        render_activity_timeline(data["recent_activities"])

    with col2:
        st.subheader("💡 Proactive Insights")
        render_insights_cards(data["insights"])

    st.markdown("---")

    # Row 5: Quick Actions
    render_quick_actions()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_overview_data(entity: str, period: str, filters: dict) -> dict:
    """Fetch all data needed for overview dashboard."""
    try:
        # Analytics data
        analytics = perform_analytics(entity, period)

        # Review status summary
        review_status = calculate_review_status_summary(entity, period)

        # Hygiene score
        hygiene_score = calculate_gl_hygiene_score(entity, period)

        # Pending items
        pending_items = get_pending_items_report(entity, period)

        # Proactive insights
        insights = generate_proactive_insights(entity, period)

        # Executive summary
        exec_summary = generate_executive_summary(entity, period)

        # Recent activities from MongoDB
        recent_activities = fetch_recent_activities(entity, period)

        # Department statistics
        dept_stats = calculate_department_stats(entity, period, filters.get("department", "All"))

        # Build KPIs
        kpis = {
            "total_accounts": analytics.get("account_count", 0),
            "total_balance": analytics.get("total_balance", 0),
            "completion_rate": review_status.get("overall_completion_rate", 0),
            "hygiene_score": hygiene_score.get("overall_score", 0),
            "pending_count": review_status.get("pending_count", 0),
            "flagged_count": analytics.get("flagged_count", 0),
            "reviewed_count": review_status.get("reviewed_count", 0),
        }

        # Status data for pie chart
        status_data = analytics.get("by_status", {})

        return {
            "kpis": kpis,
            "status_data": status_data,
            "dept_stats": dept_stats,
            "pending_items": pending_items,
            "recent_activities": recent_activities,
            "insights": insights,
            "exec_summary": exec_summary,
            "analytics": analytics,
            "hygiene_score": hygiene_score,
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_recent_activities(entity: str, period: str, limit: int = 10) -> list[dict]:
    """Fetch recent activities from MongoDB audit trail."""
    try:
        collection = get_audit_trail_collection()

        # Query recent activities
        activities = collection.find(
            {"entity": entity, "period": period}, sort=[("timestamp", -1)], limit=limit
        )

        return [
            {
                "timestamp": act.get("timestamp", datetime.now()),
                "action": act.get("action", "Unknown"),
                "user": act.get("user", "System"),
                "details": act.get("details", ""),
            }
            for act in activities
        ]
    except Exception:
        return []


def calculate_department_stats(entity: str, period: str, department_filter: str) -> dict:
    """Calculate department-wise statistics."""
    try:
        accounts = get_gl_accounts_by_period(period, entity)

        # Group by department
        dept_data = {}
        for account in accounts:
            dept = getattr(account, "department", "Unassigned")

            # Apply department filter
            if department_filter != "All" and dept != department_filter:
                continue

            if dept not in dept_data:
                dept_data[dept] = {"total": 0, "reviewed": 0, "pending": 0, "flagged": 0}

            dept_data[dept]["total"] += 1

            status = getattr(account, "review_status", "pending")
            if status == "reviewed":
                dept_data[dept]["reviewed"] += 1
            elif status == "pending":
                dept_data[dept]["pending"] += 1

            if getattr(account, "flagged", False):
                dept_data[dept]["flagged"] += 1

        # Calculate completion rates
        for dept, stats in dept_data.items():
            if stats["total"] > 0:
                stats["completion_rate"] = (stats["reviewed"] / stats["total"]) * 100
            else:
                stats["completion_rate"] = 0

        return dept_data
    except Exception:
        return {}


def render_kpi_cards(kpis: dict):
    """Render top-row KPI metric cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Accounts",
            value=f"{kpis.get('total_accounts', 0):,}",
            delta=None,
            help="Total GL accounts in this entity and period",
        )
        st.metric(
            label="Total Balance",
            value=f"₹{kpis.get('total_balance', 0):,.0f}",
            delta=None,
            help="Sum of all GL account balances",
        )

    with col2:
        completion_rate = kpis.get("completion_rate", 0)
        st.metric(
            label="Completion Rate",
            value=f"{completion_rate:.1f}%",
            delta=f"{completion_rate - 75:.1f}%" if completion_rate != 0 else None,
            help="Percentage of accounts reviewed",
        )
        st.metric(
            label="Reviewed",
            value=f"{kpis.get('reviewed_count', 0):,}",
            delta=None,
            help="Number of reviewed accounts",
        )

    with col3:
        hygiene_score = kpis.get("hygiene_score", 0)
        st.metric(
            label="Hygiene Score",
            value=f"{hygiene_score:.0f}%",
            delta=f"{hygiene_score - 80:.0f}%" if hygiene_score != 0 else None,
            help="Overall data quality score",
        )
        st.metric(
            label="Pending",
            value=f"{kpis.get('pending_count', 0):,}",
            delta=None,
            help="Number of pending reviews",
        )

    with col4:
        flagged_count = kpis.get("flagged_count", 0)
        st.metric(
            label="Flagged Items",
            value=f"{flagged_count:,}",
            delta=f"-{flagged_count}" if flagged_count > 0 else "0",
            delta_color="inverse",
            help="Number of flagged accounts requiring attention",
        )
        # Calculate risk level
        risk_level = "Low" if flagged_count < 10 else "Medium" if flagged_count < 25 else "High"
        risk_color = (
            "#27ae60" if risk_level == "Low" else "#f39c12" if risk_level == "Medium" else "#e74c3c"
        )
        st.markdown(
            f"**Risk Level:** <span style='color: {risk_color}; font-weight: bold;'>{risk_level}</span>",
            unsafe_allow_html=True,
        )


def create_status_distribution_chart(status_data: dict) -> go.Figure:
    """Create pie chart for review status distribution."""
    if not status_data:
        return go.Figure()

    labels = [status.title() for status in status_data]
    values = list(status_data.values())

    # Color scheme
    colors = {
        "reviewed": "#27ae60",
        "pending": "#f39c12",
        "flagged": "#e74c3c",
        "in_review": "#3498db",
    }

    pie_colors = [colors.get(status, "#95a5a6") for status in status_data]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=pie_colors),
                textinfo="label+percent",
                textposition="outside",
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        showlegend=True,
        height=350,
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )

    return fig


def create_department_performance_chart(dept_stats: dict) -> go.Figure:
    """Create horizontal bar chart for department completion rates."""
    if not dept_stats:
        return go.Figure()

    departments = list(dept_stats.keys())
    completion_rates = [stats["completion_rate"] for stats in dept_stats.values()]

    # Color based on completion rate
    colors = [
        "#27ae60" if rate >= 80 else "#f39c12" if rate >= 60 else "#e74c3c"
        for rate in completion_rates
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                y=departments,
                x=completion_rates,
                orientation="h",
                marker=dict(color=colors),
                text=[f"{rate:.1f}%" for rate in completion_rates],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Completion: %{x:.1f}%<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        xaxis_title="Completion Rate (%)",
        yaxis_title="Department",
        height=350,
        margin=dict(t=20, b=40, l=100, r=20),
        xaxis=dict(range=[0, 105]),
    )

    return fig


def render_pending_card(title: str, items: list):
    """Render pending items card with count and preview."""
    st.markdown(f"### {title}")

    if not items:
        st.success("✅ No pending items. All accounts are up to date!")
        return

    count = len(items)
    st.markdown(f"**Count:** {count} items")

    # Show top 5 items
    with st.expander(f"View Top {min(5, count)} Items"):
        for i, item in enumerate(items[:5], 1):
            account_code = item.get("account_code", "N/A")
            account_name = item.get("account_name", "N/A")
            criticality = item.get("criticality", "Medium")

            # Color code by criticality
            crit_color = (
                "#e74c3c"
                if criticality == "High"
                else "#f39c12" if criticality == "Medium" else "#95a5a6"
            )

            st.markdown(
                f"""
            <div style="background-color: #f0f2f6; padding: 0.5rem; border-radius: 0.3rem; margin-bottom: 0.5rem; border-left: 4px solid {crit_color};">
                <b>{i}. {account_code}</b> - {account_name}<br/>
                <small>Criticality: {criticality}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )


def render_critical_card(critical_items: int):
    """Render critical items alert card."""
    st.markdown("### 🚨 Critical Alerts")

    if critical_items == 0:
        st.success("✅ No critical alerts!")
        st.caption("All accounts are within acceptable parameters.")
    else:
        st.error(f"⚠️ {critical_items} items flagged for immediate attention")

        # Action button
        if st.button("🔍 View Flagged Items"):
            st.info("Navigate to Analytics page to view detailed flagged items report.")

        # Quick stats
        st.caption("**Flagged Reasons:**")
        st.caption("• Unusual variance detected")
        st.caption("• Missing supporting documentation")
        st.caption("• SLA breach detected")


def render_activity_timeline(activities: list[dict]):
    """Render recent activity timeline."""
    if not activities:
        st.info("No recent activities recorded.")
        return

    for activity in activities[:5]:
        timestamp = activity.get("timestamp", datetime.now())
        action = activity.get("action", "Unknown")
        user = activity.get("user", "System")

        # Format timestamp
        time_str = (
            timestamp.strftime("%H:%M") if isinstance(timestamp, datetime) else str(timestamp)
        )

        # Action icon
        icon_map = {"review": "✓", "upload": "📤", "flag": "⚠️", "approve": "✅", "assign": "👤"}
        icon = icon_map.get(action.lower(), "•")

        st.markdown(
            f"""
        <div style="background-color: #f0f2f6; padding: 0.5rem; border-radius: 0.3rem; margin-bottom: 0.5rem;">
            <b>{icon} {action}</b> <small style="color: #7f8c8d;">by {user} at {time_str}</small>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_insights_cards(insights: list[dict]):
    """Render proactive insight cards."""
    if not insights or "recommendations" not in insights:
        st.info("No insights available at this time.")
        return

    recommendations = insights.get("recommendations", [])[:3]  # Top 3

    for rec in recommendations:
        priority = rec.get("priority", "Medium")
        action = rec.get("action", "No action specified")
        category = rec.get("category", "General")

        # Priority color
        priority_colors = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#3498db"}
        color = priority_colors.get(priority, "#95a5a6")

        # Priority icon
        priority_icons = {"High": "🔴", "Medium": "⚠️", "Low": "💡"}
        icon = priority_icons.get(priority, "•")

        st.markdown(
            f"""
        <div style="background-color: #f0f2f6; padding: 0.75rem; border-radius: 0.3rem; margin-bottom: 0.5rem; border-left: 4px solid {color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span><b>{icon} {priority} Priority</b></span>
                <span style="font-size: 0.8rem; color: #7f8c8d;">{category}</span>
            </div>
            <p style="margin-top: 0.5rem; margin-bottom: 0;">{action}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_quick_actions():
    """Render quick action buttons."""
    st.subheader("⚡ Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📊 Generate Report"):
            st.info("Navigate to Reports page to generate detailed reports.")

    with col2:
        if st.button("🔍 Run Analytics"):
            st.info("Navigate to Analytics page for advanced analysis.")

    with col3:
        if st.button("📤 Upload Documents"):
            st.info("Navigate to Lookup page to upload supporting documents.")

    with col4:
        if st.button("🤖 Ask AI Assistant"):
            st.info("Navigate to AI Assistant page for natural language queries.")
