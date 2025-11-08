"""
Review Status Dashboard

Workflow tracking with reviewer assignments, SLA monitoring, pending item heatmaps,
and bottleneck detection.
"""

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics import calculate_review_status_summary, get_pending_items_report
from src.db.postgres import get_gl_accounts_by_period


def render_review_dashboard(filters: dict):
    """Render review workflow tracking dashboard."""

    st.title("📋 Review Status Dashboard")
    st.markdown(f"**Entity:** {filters['entity']} | **Period:** {filters['period']}")
    st.markdown("---")

    # Fetch review data
    with st.spinner("Loading review workflow data..."):
        data = fetch_review_data(filters["entity"], filters["period"], filters)

    if "error" in data:
        st.error(f"Error loading data: {data['error']}")
        return

    # Row 1: Progress Metrics (4 cards)
    render_progress_metrics(data["progress"])

    st.markdown("---")

    # Row 2: Reviewer Workload & SLA Status (2 columns)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👥 Reviewer Workload")
        if data["workload_data"]:
            fig = create_reviewer_workload_chart(data["workload_data"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("No reviewer data available")

    with col2:
        st.subheader("⏱️ SLA Status")
        if data["sla_data"]:
            fig = create_sla_status_chart(data["sla_data"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("No SLA data available")

    st.markdown("---")

    # Row 3: Pending Items Heatmap
    st.subheader("🔥 Pending Items Heatmap (Department × Priority)")
    if data["heatmap_data"]:
        fig = create_pending_heatmap(data["heatmap_data"])
        st.plotly_chart(fig, use_column_width=True)
    else:
        st.info("No pending items data available")

    st.markdown("---")

    # Row 4: SLA Timeline (Gantt)
    st.subheader("📅 Review Timeline (SLA Tracking)")
    if data["timeline_data"]:
        fig = create_sla_timeline_gantt(data["timeline_data"])
        st.plotly_chart(fig, use_column_width=True)
    else:
        st.info("No timeline data available")

    st.markdown("---")

    # Row 5: Bottleneck Detection
    st.subheader("🚧 Bottleneck Analysis")
    render_bottleneck_detection(data["bottlenecks"])


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_review_data(entity: str, period: str, filters: dict) -> dict:
    """Fetch all review workflow data."""
    try:
        # Review status summary
        review_status = calculate_review_status_summary(entity, period)

        # Pending items
        pending_items = get_pending_items_report(entity, period)

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

        # Get reviewer assignments (simplified - extract from accounts)
        assignments = []

        # Build progress metrics
        total_accounts = len(accounts)
        reviewed_count = sum(1 for a in accounts if getattr(a, "review_status", "") == "reviewed")
        pending_count = sum(1 for a in accounts if getattr(a, "review_status", "") == "pending")
        flagged_count = sum(1 for a in accounts if getattr(a, "flagged", False))

        completion_rate = (reviewed_count / total_accounts * 100) if total_accounts > 0 else 0

        progress = {
            "total": total_accounts,
            "reviewed": reviewed_count,
            "pending": pending_count,
            "flagged": flagged_count,
            "completion_rate": completion_rate,
            "on_track": reviewed_count >= (total_accounts * 0.75),  # 75% threshold
        }

        # Workload data (by reviewer)
        workload_data = calculate_reviewer_workload(accounts, assignments)

        # SLA data
        sla_data = calculate_sla_status(accounts)

        # Heatmap data (department × priority)
        heatmap_data = calculate_pending_heatmap(accounts)

        # Timeline data for Gantt
        timeline_data = generate_review_timeline(accounts)

        # Bottleneck detection
        bottlenecks = detect_bottlenecks(accounts, workload_data)

        return {
            "progress": progress,
            "workload_data": workload_data,
            "sla_data": sla_data,
            "heatmap_data": heatmap_data,
            "timeline_data": timeline_data,
            "bottlenecks": bottlenecks,
            "review_status": review_status,
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_reviewer_workload(accounts: list, assignments: list) -> list[dict]:
    """Calculate workload per reviewer."""
    workload = {}

    # Build assignment map
    assignment_map = {}
    for assign in assignments:
        account_code = getattr(assign, "account_code", None)
        reviewer = getattr(assign, "reviewer_email", "Unassigned")
        assignment_map[account_code] = reviewer

    # Count accounts per reviewer
    for account in accounts:
        account_code = getattr(account, "account_code", None)
        reviewer = assignment_map.get(account_code, "Unassigned")
        status = getattr(account, "review_status", "pending")

        if reviewer not in workload:
            workload[reviewer] = {
                "reviewer": reviewer,
                "total": 0,
                "reviewed": 0,
                "pending": 0,
                "in_review": 0,
            }

        workload[reviewer]["total"] += 1

        if status == "reviewed":
            workload[reviewer]["reviewed"] += 1
        elif status == "pending":
            workload[reviewer]["pending"] += 1
        elif status == "in_review":
            workload[reviewer]["in_review"] += 1

    return list(workload.values())


def calculate_sla_status(accounts: list) -> dict:
    """Calculate SLA compliance status."""
    sla_days = 5  # 5 business days SLA

    now = datetime.now()

    on_time = 0
    at_risk = 0
    breached = 0

    for account in accounts:
        status = getattr(account, "review_status", "pending")

        if status == "reviewed":
            on_time += 1
            continue

        # Check review_date or use created_at as baseline
        review_date = getattr(account, "review_date", None)
        created_at = getattr(account, "created_at", now)

        base_date = review_date if review_date else created_at

        if isinstance(base_date, str):
            try:
                base_date = datetime.fromisoformat(base_date)
            except:
                base_date = now

        days_pending = (now - base_date).days

        if days_pending > sla_days:
            breached += 1
        elif days_pending > (sla_days * 0.8):  # 80% of SLA
            at_risk += 1
        else:
            on_time += 1

    return {"on_time": on_time, "at_risk": at_risk, "breached": breached, "total": len(accounts)}


def calculate_pending_heatmap(accounts: list) -> pd.DataFrame:
    """Calculate pending items by department and priority."""
    # Build matrix
    departments = ["Finance", "Operations", "Sales", "IT", "HR", "Marketing"]
    priorities = ["High", "Medium", "Low"]

    matrix = {dept: {pri: 0 for pri in priorities} for dept in departments}

    for account in accounts:
        status = getattr(account, "review_status", "pending")

        if status != "pending":
            continue

        dept = getattr(account, "department", "Finance")

        # Determine priority based on balance and flagged status
        balance = abs(getattr(account, "closing_balance", 0) or 0)
        flagged = getattr(account, "flagged", False)

        if flagged or balance > 5000000:  # High: Flagged or >5M
            priority = "High"
        elif balance > 1000000:  # Medium: >1M
            priority = "Medium"
        else:
            priority = "Low"

        if dept in matrix:
            matrix[dept][priority] += 1

    # Convert to DataFrame
    df = pd.DataFrame(matrix).T
    return df


def generate_review_timeline(accounts: list) -> list[dict]:
    """Generate timeline data for Gantt chart."""
    timeline = []

    # Sample top 20 accounts for timeline
    for i, account in enumerate(accounts[:20]):
        account_code = getattr(account, "account_code", f"ACC{i}")
        status = getattr(account, "review_status", "pending")
        reviewer = getattr(account, "reviewer", "Unassigned")

        # Calculate dates (mock)
        start_date = datetime.now() - timedelta(days=7)

        if status == "reviewed":
            end_date = start_date + timedelta(days=3)
            task_status = "Completed"
        elif status == "in_review":
            end_date = datetime.now() + timedelta(days=1)
            task_status = "In Progress"
        else:
            end_date = start_date + timedelta(days=5)
            task_status = "Pending"

        timeline.append(
            {
                "Task": f"{account_code}",
                "Start": start_date,
                "Finish": end_date,
                "Resource": reviewer,
                "Status": task_status,
            }
        )

    return timeline


def detect_bottlenecks(accounts: list, workload_data: list[dict]) -> list[dict]:
    """Detect workflow bottlenecks."""
    bottlenecks = []

    # 1. Overloaded reviewers
    for workload in workload_data:
        reviewer = workload["reviewer"]
        total = workload["total"]
        pending = workload["pending"]

        if pending > 50:  # More than 50 pending
            bottlenecks.append(
                {
                    "type": "Overloaded Reviewer",
                    "description": f"{reviewer} has {pending} pending reviews",
                    "severity": "High",
                    "recommendation": f"Reassign some accounts from {reviewer} to other reviewers",
                }
            )

    # 2. Department backlogs
    dept_pending = {}
    for account in accounts:
        if getattr(account, "review_status", "") == "pending":
            dept = getattr(account, "department", "Unknown")
            dept_pending[dept] = dept_pending.get(dept, 0) + 1

    for dept, count in dept_pending.items():
        if count > 30:  # More than 30 pending in one department
            bottlenecks.append(
                {
                    "type": "Department Backlog",
                    "description": f"{dept} department has {count} pending reviews",
                    "severity": "Medium",
                    "recommendation": f"Allocate additional reviewers to {dept}",
                }
            )

    # 3. Flagged items pending
    flagged_pending = sum(
        1
        for a in accounts
        if getattr(a, "flagged", False) and getattr(a, "review_status", "") == "pending"
    )

    if flagged_pending > 10:
        bottlenecks.append(
            {
                "type": "Flagged Items Pending",
                "description": f"{flagged_pending} flagged items are still pending review",
                "severity": "High",
                "recommendation": "Prioritize review of flagged items immediately",
            }
        )

    return bottlenecks


def render_progress_metrics(progress: dict):
    """Render progress metric cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Accounts",
            value=f"{progress.get('total', 0):,}",
            help="Total accounts requiring review",
        )

    with col2:
        reviewed = progress.get("reviewed", 0)
        st.metric(
            label="Reviewed",
            value=f"{reviewed:,}",
            delta=f"{reviewed}",
            help="Number of completed reviews",
        )

    with col3:
        completion = progress.get("completion_rate", 0)
        on_track = progress.get("on_track", False)
        st.metric(
            label="Completion Rate",
            value=f"{completion:.1f}%",
            delta="On Track" if on_track else "Behind",
            delta_color="normal" if on_track else "inverse",
            help="Percentage of accounts reviewed",
        )

    with col4:
        pending = progress.get("pending", 0)
        st.metric(
            label="Pending Reviews",
            value=f"{pending:,}",
            delta=f"-{pending}",
            delta_color="inverse",
            help="Number of pending reviews",
        )


def create_reviewer_workload_chart(workload_data: list[dict]) -> go.Figure:
    """Create stacked bar chart for reviewer workload."""
    if not workload_data:
        return go.Figure()

    reviewers = [w["reviewer"] for w in workload_data]
    reviewed = [w["reviewed"] for w in workload_data]
    in_review = [w["in_review"] for w in workload_data]
    pending = [w["pending"] for w in workload_data]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Reviewed",
            y=reviewers,
            x=reviewed,
            orientation="h",
            marker=dict(color="#27ae60"),
            hovertemplate="<b>%{y}</b><br>Reviewed: %{x}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="In Review",
            y=reviewers,
            x=in_review,
            orientation="h",
            marker=dict(color="#3498db"),
            hovertemplate="<b>%{y}</b><br>In Review: %{x}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="Pending",
            y=reviewers,
            x=pending,
            orientation="h",
            marker=dict(color="#f39c12"),
            hovertemplate="<b>%{y}</b><br>Pending: %{x}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Number of Accounts",
        yaxis_title="Reviewer",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="right", x=1),
    )

    return fig


def create_sla_status_chart(sla_data: dict) -> go.Figure:
    """Create gauge chart for SLA compliance."""
    on_time = sla_data.get("on_time", 0)
    total = sla_data.get("total", 1)

    compliance_rate = (on_time / total * 100) if total > 0 else 0

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=compliance_rate,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "SLA Compliance %", "font": {"size": 20}},
            delta={"reference": 90, "increasing": {"color": "#27ae60"}},
            gauge={
                "axis": {"range": [None, 100], "tickwidth": 1, "tickcolor": "darkblue"},
                "bar": {"color": "#3498db"},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, 50], "color": "#e74c3c"},
                    {"range": [50, 75], "color": "#f39c12"},
                    {"range": [75, 100], "color": "#27ae60"},
                ],
                "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 90},
            },
        )
    )

    fig.update_layout(height=400, margin=dict(t=50, b=50, l=50, r=50))

    # Add breakdown text
    fig.add_annotation(
        text=f"On Time: {sla_data.get('on_time', 0)} | At Risk: {sla_data.get('at_risk', 0)} | Breached: {sla_data.get('breached', 0)}",
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.1,
        showarrow=False,
        font=dict(size=12),
    )

    return fig


def create_pending_heatmap(heatmap_data: pd.DataFrame) -> go.Figure:
    """Create heatmap for pending items by department and priority."""
    if heatmap_data.empty:
        return go.Figure()

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale="YlOrRd",
            text=heatmap_data.values,
            texttemplate="%{text}",
            textfont={"size": 14},
            hovertemplate="<b>%{y}</b><br>Priority: %{x}<br>Count: %{z}<extra></extra>",
        )
    )

    fig.update_layout(xaxis_title="Priority", yaxis_title="Department", height=400)

    return fig


def create_sla_timeline_gantt(timeline_data: list[dict]) -> go.Figure:
    """Create Gantt chart for review timeline."""
    if not timeline_data:
        return go.Figure()

    df = pd.DataFrame(timeline_data)

    # Color by status
    color_map = {"Completed": "#27ae60", "In Progress": "#3498db", "Pending": "#f39c12"}

    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Status",
        color_discrete_map=color_map,
        hover_data=["Resource"],
    )

    fig.update_layout(xaxis_title="Timeline", yaxis_title="Account", height=500, showlegend=True)

    return fig


def render_bottleneck_detection(bottlenecks: list[dict]):
    """Render bottleneck detection cards."""
    if not bottlenecks:
        st.success("✅ No major bottlenecks detected!")
        st.caption("Workflow is operating smoothly.")
        return

    st.warning(f"⚠️ {len(bottlenecks)} bottleneck(s) detected")

    for i, bottleneck in enumerate(bottlenecks, 1):
        severity = bottleneck.get("severity", "Medium")

        # Color by severity
        severity_colors = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#3498db"}
        color = severity_colors.get(severity, "#95a5a6")

        with st.expander(f"{i}. {bottleneck.get('type', 'Unknown')} ({severity} Severity)"):
            st.markdown(f"**Description:** {bottleneck.get('description', 'N/A')}")
            st.markdown(f"**Recommendation:** {bottleneck.get('recommendation', 'N/A')}")

            # Action button
            st.button(
                f"Take Action #{i}", key=f"action_{i}", help="Opens action wizard (coming soon)"
            )
