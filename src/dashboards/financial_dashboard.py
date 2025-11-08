"""
Financial Analysis Dashboard

Deep-dive financial analysis with variance waterfalls, category breakdowns,
top accounts, trend analysis, and drill-down GL table.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analytics import (
    calculate_review_status_summary,
    calculate_variance_analysis,
    perform_analytics,
)
from src.db.postgres import get_gl_accounts_by_period


def render_financial_dashboard(filters: dict):
    """Render financial analysis dashboard with detailed metrics."""

    st.title("💰 Financial Analysis Dashboard")
    st.markdown(f"**Entity:** {filters['entity']} | **Period:** {filters['period']}")
    st.markdown("---")

    # Fetch financial data
    with st.spinner("Loading financial data..."):
        data = fetch_financial_data(filters["entity"], filters["period"], filters)

    if "error" in data:
        st.error(f"Error loading data: {data['error']}")
        return

    # Row 1: Financial Summary Cards (4 columns)
    render_financial_summary(data["summary"])

    st.markdown("---")

    # Row 2: Variance Waterfall Chart
    st.subheader("📊 Variance Waterfall Analysis")
    if data["variance_data"]:
        fig = create_variance_waterfall_chart(data["variance_data"])
        st.plotly_chart(fig, use_column_width=True)
    else:
        st.info("No variance data available for this period")

    st.markdown("---")

    # Row 3: Category Breakdown & Top Accounts (2 columns)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥧 Category Breakdown")
        if data["category_data"]:
            fig = create_category_breakdown_chart(data["category_data"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("No category data available")

    with col2:
        st.subheader("📈 Top 10 Accounts by Balance")
        if data["top_accounts"]:
            fig = create_top_accounts_chart(data["top_accounts"])
            st.plotly_chart(fig, use_column_width=True)
        else:
            st.info("No account data available")

    st.markdown("---")

    # Row 4: Trend Analysis
    st.subheader("📉 Balance Trend Over Time")
    if data["trend_data"]:
        fig = create_trend_chart(data["trend_data"])
        st.plotly_chart(fig, use_column_width=True)
    else:
        st.info("Insufficient historical data for trend analysis")

    st.markdown("---")

    # Row 5: GL Account Table with Drill-down
    st.subheader("📋 GL Account Details")
    render_gl_account_table(data["gl_accounts"], filters)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_financial_data(entity: str, period: str, filters: dict) -> dict:
    """Fetch all financial data for dashboard."""
    try:
        # Analytics data
        analytics = perform_analytics(entity, period)

        # Variance analysis
        variance_data = calculate_variance_analysis(entity, period)

        # Review status
        review_status = calculate_review_status_summary(entity, period)

        # Fetch GL accounts
        accounts = get_gl_accounts_by_period(period, entity)

        # Filter by category if specified
        if filters.get("category") != "All":
            accounts = [
                a for a in accounts if getattr(a, "account_category", None) == filters["category"]
            ]

        # Filter by department if specified
        if filters.get("department") != "All":
            accounts = [
                a for a in accounts if getattr(a, "department", None) == filters["department"]
            ]

        # Build summary metrics
        total_debit = sum(getattr(a, "debit_amount", 0) or 0 for a in accounts)
        total_credit = sum(getattr(a, "credit_amount", 0) or 0 for a in accounts)
        net_balance = total_debit - total_credit

        summary = {
            "total_debit": total_debit,
            "total_credit": total_credit,
            "net_balance": net_balance,
            "account_count": len(accounts),
            "variance_percentage": (
                variance_data.get("total_variance_percentage", 0) if variance_data else 0
            ),
        }

        # Category breakdown
        category_data = calculate_category_breakdown(accounts)

        # Top accounts by balance
        top_accounts = get_top_accounts_by_balance(accounts, top_n=10)

        # Trend data (mock for now - would query historical periods)
        trend_data = generate_trend_data(entity, period)

        # Convert accounts to DataFrame
        gl_accounts_df = accounts_to_dataframe(accounts)

        return {
            "summary": summary,
            "variance_data": variance_data,
            "category_data": category_data,
            "top_accounts": top_accounts,
            "trend_data": trend_data,
            "gl_accounts": gl_accounts_df,
            "analytics": analytics,
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_category_breakdown(accounts: list) -> dict:
    """Calculate balance breakdown by account category."""
    category_totals = {}

    for account in accounts:
        category = getattr(account, "account_category", "Uncategorized")
        balance = getattr(account, "closing_balance", 0) or 0

        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += abs(balance)

    return category_totals


def get_top_accounts_by_balance(accounts: list, top_n: int = 10) -> list[dict]:
    """Get top N accounts by closing balance."""
    account_data = []

    for account in accounts:
        account_data.append(
            {
                "account_code": getattr(account, "account_code", "N/A"),
                "account_name": getattr(account, "account_name", "N/A"),
                "balance": abs(getattr(account, "closing_balance", 0) or 0),
                "category": getattr(account, "account_category", "N/A"),
            }
        )

    # Sort by balance descending
    account_data.sort(key=lambda x: x["balance"], reverse=True)

    return account_data[:top_n]


def generate_trend_data(entity: str, period: str) -> list[dict] | None:
    """Generate trend data for balance over time (mock implementation)."""
    # In production, this would query multiple periods from database
    # For now, generate sample trend data

    # Parse period (e.g., "2024-03")
    try:
        year, month = map(int, period.split("-"))
    except:
        return None

    # Generate 6 months of data
    trend_points = []
    base_balance = 1000000

    for i in range(6):
        month_offset = month - i
        year_offset = year

        while month_offset <= 0:
            month_offset += 12
            year_offset -= 1

        trend_points.append(
            {
                "period": f"{year_offset}-{month_offset:02d}",
                "balance": base_balance * (1 + (i * 0.05)),  # Mock growth
            }
        )

    return list(reversed(trend_points))


def accounts_to_dataframe(accounts: list) -> pd.DataFrame:
    """Convert account objects to pandas DataFrame."""
    data = []

    for account in accounts:
        data.append(
            {
                "Account Code": getattr(account, "account_code", "N/A"),
                "Account Name": getattr(account, "account_name", "N/A"),
                "Category": getattr(account, "account_category", "N/A"),
                "Department": getattr(account, "department", "N/A"),
                "Opening Balance": getattr(account, "opening_balance", 0) or 0,
                "Debit": getattr(account, "debit_amount", 0) or 0,
                "Credit": getattr(account, "credit_amount", 0) or 0,
                "Closing Balance": getattr(account, "closing_balance", 0) or 0,
                "Status": getattr(account, "review_status", "pending").title(),
                "Flagged": "🚩" if getattr(account, "flagged", False) else "",
            }
        )

    return pd.DataFrame(data)


def render_financial_summary(summary: dict):
    """Render financial summary cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Debit",
            value=f"₹{summary.get('total_debit', 0):,.0f}",
            help="Sum of all debit transactions",
        )

    with col2:
        st.metric(
            label="Total Credit",
            value=f"₹{summary.get('total_credit', 0):,.0f}",
            help="Sum of all credit transactions",
        )

    with col3:
        net_balance = summary.get("net_balance", 0)
        st.metric(
            label="Net Balance",
            value=f"₹{net_balance:,.0f}",
            delta=f"{'Debit' if net_balance > 0 else 'Credit'} Heavy",
            help="Difference between total debits and credits",
        )

    with col4:
        variance_pct = summary.get("variance_percentage", 0)
        st.metric(
            label="Variance %",
            value=f"{variance_pct:.1f}%",
            delta=f"{variance_pct:.1f}%",
            delta_color="off" if abs(variance_pct) < 5 else "normal",
            help="Percentage variance from expected values",
        )


def create_variance_waterfall_chart(variance_data: dict) -> go.Figure:
    """Create waterfall chart for variance analysis."""
    if not variance_data or "variance_details" not in variance_data:
        return go.Figure()

    details = variance_data.get("variance_details", [])

    # Build waterfall data
    categories = ["Opening Balance"] + [d["category"] for d in details] + ["Closing Balance"]
    values = [variance_data.get("opening_balance", 0)]

    for detail in details:
        values.append(detail.get("variance_amount", 0))

    # Calculate closing balance
    closing = sum(values)
    values.append(closing)

    # Determine measure types
    measures = ["absolute"] + ["relative"] * len(details) + ["total"]

    fig = go.Figure(
        go.Waterfall(
            name="Variance",
            orientation="v",
            measure=measures,
            x=categories,
            y=values,
            text=[f"₹{v:,.0f}" for v in values],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#27ae60"}},
            decreasing={"marker": {"color": "#e74c3c"}},
            totals={"marker": {"color": "#3498db"}},
        )
    )

    fig.update_layout(
        title="Variance Breakdown",
        showlegend=False,
        height=400,
        xaxis_title="Category",
        yaxis_title="Amount (₹)",
    )

    return fig


def create_category_breakdown_chart(category_data: dict) -> go.Figure:
    """Create pie chart for category breakdown."""
    if not category_data:
        return go.Figure()

    labels = list(category_data.keys())
    values = list(category_data.values())

    # Color palette
    colors = ["#3498db", "#e74c3c", "#27ae60", "#f39c12", "#9b59b6", "#1abc9c"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=colors[: len(labels)]),
                textinfo="label+percent",
                textposition="outside",
                hovertemplate="<b>%{label}</b><br>Balance: ₹%{value:,.0f}<br>Percentage: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        showlegend=True,
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    )

    return fig


def create_top_accounts_chart(top_accounts: list[dict]) -> go.Figure:
    """Create horizontal bar chart for top accounts."""
    if not top_accounts:
        return go.Figure()

    account_names = [
        f"{acc['account_code']}<br>{acc['account_name'][:20]}..." for acc in top_accounts
    ]
    balances = [acc["balance"] for acc in top_accounts]

    # Color by category
    category_colors = {
        "Assets": "#3498db",
        "Liabilities": "#e74c3c",
        "Equity": "#27ae60",
        "Revenue": "#f39c12",
        "Expenses": "#9b59b6",
    }

    colors = [category_colors.get(acc["category"], "#95a5a6") for acc in top_accounts]

    fig = go.Figure(
        data=[
            go.Bar(
                y=account_names,
                x=balances,
                orientation="h",
                marker=dict(color=colors),
                text=[f"₹{bal:,.0f}" for bal in balances],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Balance: ₹%{x:,.0f}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        xaxis_title="Balance (₹)",
        yaxis_title="Account",
        height=400,
        margin=dict(l=150),
        showlegend=False,
    )

    return fig


def create_trend_chart(trend_data: list[dict]) -> go.Figure:
    """Create line chart for balance trend over time."""
    if not trend_data:
        return go.Figure()

    periods = [t["period"] for t in trend_data]
    balances = [t["balance"] for t in trend_data]

    fig = go.Figure()

    # Add line
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=balances,
            mode="lines+markers",
            name="Balance",
            line=dict(color="#3498db", width=3),
            marker=dict(size=8),
            hovertemplate="<b>Period: %{x}</b><br>Balance: ₹%{y:,.0f}<extra></extra>",
        )
    )

    # Add trend line
    if len(balances) >= 2:
        # Simple linear trend
        from numpy import poly1d, polyfit

        x_numeric = list(range(len(balances)))
        coeffs = polyfit(x_numeric, balances, 1)
        trend_line = poly1d(coeffs)
        trend_values = [trend_line(x) for x in x_numeric]

        fig.add_trace(
            go.Scatter(
                x=periods,
                y=trend_values,
                mode="lines",
                name="Trend",
                line=dict(color="#e74c3c", width=2, dash="dash"),
                hovertemplate="<b>Trend: ₹%{y:,.0f}</b><extra></extra>",
            )
        )

    fig.update_layout(
        xaxis_title="Period",
        yaxis_title="Balance (₹)",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="right", x=1),
    )

    return fig


def render_gl_account_table(df: pd.DataFrame, filters: dict):
    """Render interactive GL account table with drill-down."""
    if df.empty:
        st.info("No GL accounts found for the selected filters.")
        return

    # Add search functionality
    search = st.text_input("🔍 Search Accounts", placeholder="Search by code or name...")

    if search:
        mask = df["Account Code"].str.contains(search, case=False, na=False) | df[
            "Account Name"
        ].str.contains(search, case=False, na=False)
        df = df[mask]

    # Show summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"**Total Accounts:** {len(df)}")
    with col2:
        st.caption(f"**Total Balance:** ₹{df['Closing Balance'].sum():,.0f}")
    with col3:
        flagged_count = (df["Flagged"] == "🚩").sum()
        st.caption(f"**Flagged:** {flagged_count}")

    # Format currency columns
    currency_cols = ["Opening Balance", "Debit", "Credit", "Closing Balance"]
    for col in currency_cols:
        df[col] = df[col].apply(lambda x: f"₹{x:,.0f}")

    # Display table
    st.dataframe(df, use_column_width=True, height=400, hide_index=True)

    # Export button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"gl_accounts_{filters['entity']}_{filters['period']}.csv",
        mime="text/csv",
    )
