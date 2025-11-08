"""
Dashboard Module

Multi-page interactive dashboard system with persistent filtering and state management.
Provides 5 specialized dashboard pages: Overview, Financial, Review, Quality, and Risk.
"""

from datetime import datetime
from typing import Dict, Literal, Optional

import streamlit as st


def render_dashboard(
    page: Literal["overview", "financial", "review", "quality", "risk"], filters: dict
):
    """
    Route to appropriate dashboard page.

    Args:
        page: Dashboard page to render
        filters: Filter dict from apply_global_filters()
    """
    # Route to specific dashboard
    if page == "overview":
        from .overview_dashboard import render_overview_dashboard

        render_overview_dashboard(filters)
    elif page == "financial":
        from .financial_dashboard import render_financial_dashboard

        render_financial_dashboard(filters)
    elif page == "review":
        from .review_dashboard import render_review_dashboard

        render_review_dashboard(filters)
    elif page == "quality":
        from .quality_dashboard import render_quality_dashboard

        render_quality_dashboard(filters)
    elif page == "risk":
        from .risk_dashboard import render_risk_dashboard

        render_risk_dashboard(filters)
    else:
        st.error(f"Unknown dashboard page: {page}")


def apply_global_filters() -> dict:
    """
    Render global filter bar and return filter selections.

    Returns:
        Dict with filter values: entity, period, department, category, date_range
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Global Filters")

    # Initialize session state for filters if not exists
    if "dashboard_filters" not in st.session_state:
        st.session_state.dashboard_filters = {
            "entity": "Entity001",
            "period": "2024-03",
            "department": "All",
            "category": "All",
            "date_range": "Current Period",
        }

    # Entity selection
    entities = ["All", "Entity001", "Entity002", "Entity003", "Entity004", "Entity005"]
    entity = st.sidebar.selectbox(
        "Entity",
        entities,
        index=(
            entities.index(st.session_state.dashboard_filters["entity"])
            if st.session_state.dashboard_filters["entity"] in entities
            else 1
        ),
        key="filter_entity",
    )
    st.session_state.dashboard_filters["entity"] = entity

    # Period selection
    periods = ["2024-03", "2024-02", "2024-01", "2023-12", "2023-11", "2023-10"]
    period = st.sidebar.selectbox(
        "Period",
        periods,
        index=(
            periods.index(st.session_state.dashboard_filters["period"])
            if st.session_state.dashboard_filters["period"] in periods
            else 0
        ),
        key="filter_period",
    )
    st.session_state.dashboard_filters["period"] = period

    # Department filter
    departments = ["All", "Finance", "Operations", "Sales", "IT", "HR", "Marketing"]
    department = st.sidebar.selectbox(
        "Department",
        departments,
        index=(
            departments.index(st.session_state.dashboard_filters["department"])
            if st.session_state.dashboard_filters["department"] in departments
            else 0
        ),
        key="filter_department",
    )
    st.session_state.dashboard_filters["department"] = department

    # Category filter
    categories = ["All", "Assets", "Liabilities", "Equity", "Revenue", "Expenses"]
    category = st.sidebar.selectbox(
        "Category",
        categories,
        index=(
            categories.index(st.session_state.dashboard_filters["category"])
            if st.session_state.dashboard_filters["category"] in categories
            else 0
        ),
        key="filter_category",
    )
    st.session_state.dashboard_filters["category"] = category

    # Date range filter
    date_ranges = ["Current Period", "Last 3 Months", "Last 6 Months", "Year to Date", "Custom"]
    date_range = st.sidebar.selectbox(
        "Date Range",
        date_ranges,
        index=(
            date_ranges.index(st.session_state.dashboard_filters["date_range"])
            if st.session_state.dashboard_filters["date_range"] in date_ranges
            else 0
        ),
        key="filter_date_range",
    )
    st.session_state.dashboard_filters["date_range"] = date_range

    # Custom date range (if selected)
    if date_range == "Custom":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("From", key="filter_start_date")
        with col2:
            end_date = st.date_input("To", key="filter_end_date")
        st.session_state.dashboard_filters["custom_start"] = start_date
        st.session_state.dashboard_filters["custom_end"] = end_date

    # Action buttons
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🔄 Refresh", key="refresh_dashboard"):
            # Clear cache to force data reload
            st.cache_data.clear()
            st.rerun()

    with col2:
        if st.button("🗑️ Reset", key="reset_filters"):
            # Reset to default filters
            st.session_state.dashboard_filters = {
                "entity": "Entity001",
                "period": "2024-03",
                "department": "All",
                "category": "All",
                "date_range": "Current Period",
            }
            st.rerun()

    # Export button
    if st.sidebar.button("📥 Export Dashboard", key="export_dashboard"):
        st.sidebar.info("Export functionality coming soon!")

    # Full-screen mode toggle
    st.sidebar.markdown("---")
    fullscreen = st.sidebar.checkbox("🖥️ Full Screen Mode", key="fullscreen_mode")
    if fullscreen:
        st.markdown(
            """
        <style>
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
                max-width: 100%;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )

    # Display active filters summary
    st.sidebar.markdown("---")
    st.sidebar.caption("**Active Filters:**")
    st.sidebar.caption(f"📍 Entity: {entity}")
    st.sidebar.caption(f"📅 Period: {period}")
    if department != "All":
        st.sidebar.caption(f"🏢 Department: {department}")
    if category != "All":
        st.sidebar.caption(f"📊 Category: {category}")

    return st.session_state.dashboard_filters


__all__ = ["render_dashboard", "apply_global_filters"]
