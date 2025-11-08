"""
Project Aura: AI-Powered Financial Statement Review Agent

Multi-page Streamlit application for GL account validation, consolidation, and reporting.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Local imports
from src.agent import create_agent, query_agent
from src.analytics import calculate_gl_hygiene_score, get_pending_items_report
from src.db import get_mongo_database
from src.db.mongodb import get_audit_trail_collection
from src.db.postgres import get_gl_accounts_by_period
from src.insights import (
    compare_multi_period,
    generate_drill_down_report,
    generate_executive_summary,
    generate_proactive_insights,
)
from src.visualizations import create_hygiene_gauge, create_trend_line_chart

# Page configuration
st.set_page_config(
    page_title="Project Aura - Financial Review Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .critical-item {
        background-color: #ffe6e6;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
    }
    .high-item {
        background-color: #fff4e6;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
    }
    .success-item {
        background-color: #e6ffe6;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Session state initialization
if "current_entity" not in st.session_state:
    st.session_state.current_entity = "Entity001"
if "current_period" not in st.session_state:
    st.session_state.current_period = "2024-03"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = None


# ==============================================
# SIDEBAR: Global Filters & Navigation
# ==============================================
with st.sidebar:
    st.image(
        "https://via.placeholder.com/200x80/1f77b4/ffffff?text=Project+Aura", use_column_width=True
    )
    st.markdown("---")

    # Entity & Period Selection
    st.subheader("🏢 Entity & Period")

    entities = ["Entity001", "Entity002", "Entity003", "Entity004", "Entity005"]
    st.session_state.current_entity = st.selectbox(
        "Select Entity",
        entities,
        index=(
            entities.index(st.session_state.current_entity)
            if st.session_state.current_entity in entities
            else 0
        ),
    )

    periods = ["2024-03", "2024-02", "2024-01", "2023-12", "2023-11"]
    st.session_state.current_period = st.selectbox(
        "Select Period",
        periods,
        index=(
            periods.index(st.session_state.current_period)
            if st.session_state.current_period in periods
            else 0
        ),
    )

    st.markdown("---")

    # Quick Stats
    st.subheader("📊 Quick Stats")
    try:
        accounts = get_gl_accounts_by_period(
            st.session_state.current_period, st.session_state.current_entity
        )

        total_accounts = len(accounts)
        total_balance = sum([acc.debit_balance + acc.credit_balance for acc in accounts])

        st.metric("Total Accounts", f"{total_accounts:,}")
        st.metric("Total Balance", f"₹{total_balance:,.0f}")
    except Exception as e:
        st.error(f"Error loading stats: {e!s}")

    st.markdown("---")
    st.caption("Project Aura v1.0 | Finnovate Hackathon 2024")


# ==============================================
# PAGE ROUTING
# ==============================================
page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📊 Dashboard",
        "🔍 Analytics",
        "🔎 Lookup",
        "📄 Reports",
        "🤖 AI Assistant",
        "⚙️ Settings",
    ],
    label_visibility="collapsed",
)


# ==============================================
# PAGE 1: HOME (OVERVIEW)
# ==============================================
if page == "🏠 Home":
    st.markdown('<div class="main-header">Welcome to Project Aura</div>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Financial Statement Review Agent for Adani Group**")

    st.markdown("---")

    # Executive Summary
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 Executive Summary")
        try:
            summary = generate_executive_summary(
                st.session_state.current_entity, st.session_state.current_period
            )

            if "error" not in summary:
                # Overall Status
                status = summary.get("overall_status", "N/A")
                status_color = {
                    "Excellent": "#2ecc71",
                    "Good": "#3498db",
                    "Fair": "#f39c12",
                    "Needs Attention": "#e74c3c",
                }.get(status, "#95a5a6")

                st.markdown(
                    f"""
                <div style="background-color: {status_color}; color: white; padding: 1rem; border-radius: 0.5rem; text-align: center; font-size: 1.5rem; font-weight: bold;">
                    {status}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # Key Metrics
                metrics = summary.get("key_metrics", {})
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                col_m1.metric("Total Accounts", f"{metrics.get('total_accounts', 0):,}")
                col_m2.metric("Total Balance", f"₹{metrics.get('total_balance', 0):,.0f}")
                col_m3.metric("Hygiene Score", f"{metrics.get('hygiene_score', 0):.1f}/100")
                col_m4.metric("Completion Rate", f"{metrics.get('completion_rate', 0):.1f}%")

                # Highlights
                st.markdown("#### ✅ Highlights")
                for highlight in summary.get("highlights", [])[:3]:
                    st.markdown(
                        f'<div class="success-item">✓ {highlight}</div>', unsafe_allow_html=True
                    )

                # Concerns
                st.markdown("#### ⚠️ Areas of Concern")
                for concern in summary.get("concerns", [])[:3]:
                    st.markdown(f'<div class="high-item">⚠ {concern}</div>', unsafe_allow_html=True)

                # Recommendations
                st.markdown("#### 💡 Recommendations")
                for rec in summary.get("recommendations", [])[:3]:
                    st.markdown(f"- {rec}")
            else:
                st.error(summary["error"])
        except Exception as e:
            st.error(f"Error generating summary: {e!s}")

    with col2:
        st.subheader("🎯 GL Hygiene Score")
        try:
            hygiene = calculate_gl_hygiene_score(
                st.session_state.current_entity, st.session_state.current_period
            )

            if "error" not in hygiene:
                fig = create_hygiene_gauge(hygiene["overall_score"], hygiene["components"])
                st.plotly_chart(fig, use_column_width=True)

                # Component Breakdown
                st.markdown("**Components:**")
                for comp, score in hygiene["components"].items():
                    st.progress(
                        score / 100, text=f"{comp.replace('_', ' ').title()}: {score:.0f}/100"
                    )
            else:
                st.error(hygiene["error"])
        except Exception as e:
            st.error(f"Error loading hygiene score: {e!s}")

    st.markdown("---")

    # Proactive Insights
    st.subheader("💡 Proactive Insights")
    try:
        insights = generate_proactive_insights(
            st.session_state.current_entity, st.session_state.current_period
        )

        if "error" not in insights:
            for insight in insights.get("insights", [])[:5]:
                priority = insight.get("priority", "info")
                icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "info": "🔵"}.get(
                    priority, "⚪"
                )

                with st.expander(
                    f"{icon} {insight.get('message', 'N/A')}", expanded=(priority == "critical")
                ):
                    st.markdown(f"**Type:** {insight.get('type', 'N/A')}")
                    st.markdown(f"**Recommendation:** {insight.get('recommendation', 'N/A')}")
        else:
            st.error(insights["error"])
    except Exception as e:
        st.error(f"Error loading insights: {e!s}")


# ==============================================
# PAGE 2: DASHBOARD (5 COMPREHENSIVE DASHBOARDS)
# ==============================================
elif page == "📊 Dashboard":
    st.markdown('<div class="main-header">Interactive Dashboards</div>', unsafe_allow_html=True)
    st.markdown("**Comprehensive analytics with drill-down capabilities and real-time insights**")

    # Import dashboard module
    from src.dashboards import apply_global_filters, render_dashboard

    # Apply global filters and get filter dict
    filters = apply_global_filters()

    st.markdown("---")

    # Create 5 tabs for the dashboards
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Overview",
            "💰 Financial Analysis",
            "📋 Review Status",
            "✨ Quality & Hygiene",
            "🔍 Risk & Anomalies",
        ]
    )

    with tab1:
        # Overview Dashboard
        try:
            render_dashboard("overview", filters)
        except Exception as e:
            st.error(f"Error loading Overview Dashboard: {e!s}")
            st.exception(e)

    with tab2:
        # Financial Analysis Dashboard
        try:
            render_dashboard("financial", filters)
        except Exception as e:
            st.error(f"Error loading Financial Dashboard: {e!s}")
            st.exception(e)

    with tab3:
        # Review Status Dashboard
        try:
            render_dashboard("review", filters)
        except Exception as e:
            st.error(f"Error loading Review Dashboard: {e!s}")
            st.exception(e)

    with tab4:
        # Quality & Hygiene Dashboard
        try:
            render_dashboard("quality", filters)
        except Exception as e:
            st.error(f"Error loading Quality Dashboard: {e!s}")
            st.exception(e)

    with tab5:
        # Risk & Anomaly Dashboard
        try:
            render_dashboard("risk", filters)
        except Exception as e:
            st.error(f"Error loading Risk Dashboard: {e!s}")
            st.exception(e)


# ==============================================
# PAGE 3: ANALYTICS (INSIGHTS & DRILL-DOWN)
# ==============================================
elif page == "🔍 Analytics":
    st.markdown('<div class="main-header">Deep Dive Analytics</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎯 Drill-Down", "📊 Multi-Period Comparison", "📋 Pending Items"])

    with tab1:
        st.subheader("Drill-Down Analysis")

        col1, col2 = st.columns(2)
        with col1:
            dimension = st.selectbox(
                "Dimension", ["category", "department", "criticality", "review_status"]
            )
        with col2:
            # Load unique values for selected dimension
            value = st.text_input("Filter Value (e.g., Assets, Finance, High)", "")

        if st.button("🔍 Analyze", type="primary"):
            if value:
                try:
                    report = generate_drill_down_report(
                        st.session_state.current_entity,
                        st.session_state.current_period,
                        dimension,
                        value,
                    )

                    if "error" not in report:
                        # Metrics
                        st.markdown("### Summary Metrics")
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        metrics = report.get("summary_metrics", {})
                        col_m1.metric("Total Accounts", f"{metrics.get('total_accounts', 0):,}")
                        col_m2.metric("Total Balance", f"₹{metrics.get('total_balance', 0):,.0f}")
                        col_m3.metric("Avg Balance", f"₹{metrics.get('avg_balance', 0):,.0f}")
                        col_m4.metric("Completion %", f"{metrics.get('completion_rate', 0):.1f}%")

                        # Status Distribution
                        st.markdown("### Status Distribution")
                        status_dist = report.get("status_distribution", {})
                        if status_dist:
                            cols = st.columns(len(status_dist))
                            for idx, (status, count) in enumerate(status_dist.items()):
                                cols[idx].metric(status, count)

                        # Top Accounts
                        st.markdown("### Top Accounts by Balance")
                        if "top_accounts" in report:
                            st.dataframe(
                                pd.DataFrame(report["top_accounts"]), use_column_width=True
                            )
                    else:
                        st.error(report["error"])
                except Exception as e:
                    st.error(f"Error: {e!s}")
            else:
                st.warning("Please enter a filter value")

    with tab2:
        st.subheader("Multi-Period Trend Analysis")

        selected_periods = st.multiselect(
            "Select Periods to Compare",
            ["2024-03", "2024-02", "2024-01", "2023-12", "2023-11"],
            default=["2024-03", "2024-02", "2024-01"],
        )

        if st.button("📊 Compare Periods", type="primary"):
            if len(selected_periods) >= 2:
                try:
                    comparison = compare_multi_period(
                        st.session_state.current_entity, selected_periods
                    )

                    if "error" not in comparison:
                        # Trend Charts
                        st.markdown("### Trend Analysis")

                        trend_data = {
                            "Total Balance": [
                                p["total_balance"] for p in comparison.get("period_summaries", [])
                            ],
                            "Hygiene Score": [
                                p["hygiene_score"] for p in comparison.get("period_summaries", [])
                            ],
                            "Completion Rate": [
                                p["completion_rate"] for p in comparison.get("period_summaries", [])
                            ],
                        }

                        fig = create_trend_line_chart(trend_data, selected_periods)
                        st.plotly_chart(fig, use_column_width=True)

                        # Period Summaries Table
                        st.markdown("### Period-wise Summary")
                        st.dataframe(
                            pd.DataFrame(comparison.get("period_summaries", [])),
                            use_column_width=True,
                        )

                        # Trends
                        st.markdown("### Identified Trends")
                        trends = comparison.get("trends", {})
                        for metric, trend_info in trends.items():
                            direction = trend_info.get("direction", "N/A")
                            icon = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(
                                direction, "❓"
                            )
                            st.markdown(
                                f"**{metric}:** {icon} {direction.title()} ({trend_info.get('change_pct', 0):.1f}%)"
                            )
                    else:
                        st.error(comparison["error"])
                except Exception as e:
                    st.error(f"Error: {e!s}")
            else:
                st.warning("Please select at least 2 periods")

    with tab3:
        st.subheader("Pending Items Report")

        try:
            pending = get_pending_items_report(
                st.session_state.current_entity, st.session_state.current_period
            )

            if "error" not in pending:
                # Summary
                col1, col2, col3 = st.columns(3)
                col1.metric("Pending Reviews", f"{pending.get('pending_reviews_count', 0):,}")
                col2.metric("Missing Docs", f"{pending.get('missing_docs_count', 0):,}")
                col3.metric("Flagged Items", f"{pending.get('flagged_items_count', 0):,}")

                # Pending Reviews
                st.markdown("### 📝 Pending Reviews")
                if pending.get("pending_reviews"):
                    st.dataframe(pd.DataFrame(pending["pending_reviews"]), use_column_width=True)
                else:
                    st.success("No pending reviews!")

                # Missing Documentation
                st.markdown("### 📄 Missing Documentation")
                if pending.get("missing_docs"):
                    st.dataframe(pd.DataFrame(pending["missing_docs"]), use_column_width=True)
                else:
                    st.success("All documentation complete!")

                # Flagged Items
                st.markdown("### 🚩 Flagged Items")
                if pending.get("flagged_items"):
                    st.dataframe(pd.DataFrame(pending["flagged_items"]), use_column_width=True)
                else:
                    st.success("No flagged items!")
            else:
                st.error(pending["error"])
        except Exception as e:
            st.error(f"Error: {e!s}")


# ==============================================
# PAGE 4: LOOKUP (ACCOUNT SEARCH)
# ==============================================
elif page == "🔎 Lookup":
    st.markdown('<div class="main-header">GL Account Lookup</div>', unsafe_allow_html=True)

    search_query = st.text_input(
        "🔍 Search by Account Code or Name", placeholder="e.g., 100000, Cash, Bank"
    )

    if search_query:
        try:
            accounts = get_gl_accounts_by_period(
                st.session_state.current_period, st.session_state.current_entity
            )

            # Filter accounts
            filtered = [
                acc
                for acc in accounts
                if search_query.lower() in acc.account_code.lower()
                or search_query.lower() in acc.account_name.lower()
            ]

            st.markdown(f"**Found {len(filtered)} account(s)**")

            for acc in filtered[:10]:
                with st.expander(f"{acc.account_code} - {acc.account_name}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Basic Information**")
                        st.write(f"**Category:** {acc.category}")
                        st.write(f"**Department:** {acc.department}")
                        st.write(f"**Criticality:** {acc.criticality}")
                        st.write(f"**Debit Balance:** ₹{acc.debit_balance:,.2f}")
                        st.write(f"**Credit Balance:** ₹{acc.credit_balance:,.2f}")

                    with col2:
                        st.markdown("**Review Status**")
                        st.write(f"**Status:** {acc.review_status}")
                        st.write(f"**Reviewed By:** {acc.reviewed_by or 'N/A'}")
                        st.write(f"**Reviewed At:** {acc.reviewed_at or 'N/A'}")
                        st.write(f"**Comments:** {acc.comments or 'N/A'}")
        except Exception as e:
            st.error(f"Error: {e!s}")


# ==============================================
# PAGE 5: REPORTS (EXPORT & GENERATION)
# ==============================================
elif page == "📄 Reports":
    st.markdown(
        '<div class="main-header">Automated Report Generation</div>', unsafe_allow_html=True
    )
    st.markdown("Generate professional reports in multiple formats (PDF, Excel, CSV, Markdown)")

    st.markdown("---")

    # Import report module
    from src.reports import generate_report

    # Report Configuration
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Report Configuration")

        # Report type selection with descriptions
        report_types = {
            "status": "📊 GL Account Status Report - Pending reviews, missing docs, flagged items, SLA status",
            "variance": "📈 Variance Analysis Report - Period-over-period variance with waterfall charts",
            "hygiene": "🏥 GL Hygiene Dashboard - Quality score breakdown with component analysis",
            "reviewer_performance": "👥 Reviewer Performance Report - Productivity metrics and bottleneck detection",
            "sla_compliance": "⏰ SLA Compliance Report - Deadline tracking, at-risk items, breach detection",
            "executive_summary": "📄 Executive Summary - One-page leadership dashboard with key insights",
        }

        report_type = st.selectbox(
            "Select Report Type",
            options=list(report_types.keys()),
            format_func=lambda x: report_types[x],
            help="Choose the type of report to generate",
        )

        # Entity & Period (pre-filled from session state)
        entity = st.text_input(
            "Entity", value=st.session_state.current_entity, help="Entity code (e.g., Entity001)"
        )

        period = st.text_input(
            "Period",
            value=st.session_state.current_period,
            help="Period in YYYY-MM format (e.g., 2024-03)",
        )

        # Advanced options (collapsible)
        with st.expander("⚙️ Advanced Options"):
            if report_type == "variance":
                previous_period = st.text_input(
                    "Previous Period (for variance)",
                    value="2024-02",
                    help="Period to compare against",
                )

            output_dir = st.text_input(
                "Output Directory", value="data/reports", help="Directory to save generated reports"
            )

    with col2:
        st.subheader("📁 Available Formats")

        # Show formats based on report type
        format_info = {
            "status": ["PDF (6 sections)", "CSV (combined data)"],
            "variance": ["PDF (summary)", "Excel (6 sheets)", "HTML (waterfall chart)"],
            "hygiene": ["PDF (detailed)", "PNG (charts)", "HTML (dashboard)", "JSON (data)"],
            "reviewer_performance": ["PDF (analysis)", "CSV (metrics)"],
            "sla_compliance": [
                "PDF (summary)",
                "Excel (6 sheets: Summary, On-Time, Delayed, At-Risk, Breached, Critical)",
            ],
            "executive_summary": [
                "PDF (1-page A4)",
                "Markdown (email-friendly)",
                "PNG (dashboard)",
            ],
        }

        formats = format_info.get(report_type, ["PDF"])
        st.info(f"**{report_types[report_type].split(' - ')[0]}** will generate:")
        for fmt in formats:
            st.markdown(f"✓ {fmt}")

        st.markdown("---")

        # Report Preview
        st.markdown("**Report Features:**")
        if report_type == "status":
            st.markdown("• Executive summary with key metrics")
            st.markdown("• Top 10 pending reviews")
            st.markdown("• Missing documentation analysis")
            st.markdown("• Flagged items with priority")
            st.markdown("• SLA compliance tracking")
            st.markdown("• Actionable recommendations")
        elif report_type == "variance":
            st.markdown("• Summary metrics comparison")
            st.markdown("• Top movers (largest variances)")
            st.markdown("• Category-wise breakdown")
            st.markdown("• Interactive waterfall chart")
            st.markdown("• Trend analysis")
        elif report_type == "hygiene":
            st.markdown("• Overall hygiene score gauge")
            st.markdown("• 4 component scores breakdown")
            st.markdown("• Quality issues by severity")
            st.markdown("• Interactive component charts")
            st.markdown("• Improvement recommendations")
        elif report_type == "reviewer_performance":
            st.markdown("• Top performers ranking")
            st.markdown("• Workload distribution analysis")
            st.markdown("• Bottleneck detection (>20 pending)")
            st.markdown("• Productivity score calculation")
            st.markdown("• Reallocation recommendations")
        elif report_type == "sla_compliance":
            st.markdown("• Overall compliance rate")
            st.markdown("• At-risk items (≤24h deadline)")
            st.markdown("• Breached SLA tracking")
            st.markdown("• Critical item monitoring")
            st.markdown("• 6-sheet Excel breakdown")
        else:  # executive_summary
            st.markdown("• 6 key KPI cards")
            st.markdown("• Top 4 highlights & concerns")
            st.markdown("• Strategic recommendations")
            st.markdown("• Status breakdown table")
            st.markdown("• One-page compact layout")

    st.markdown("---")

    # Generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_btn = st.button("🚀 Generate Report", type="primary")

    if generate_btn:
        try:
            with st.spinner(f"Generating {report_types[report_type].split(' - ')[0]}..."):
                # Prepare kwargs
                kwargs = {"output_dir": output_dir}
                if report_type == "variance" and "previous_period" in locals():
                    kwargs["previous_period"] = previous_period

                # Generate report
                generated_files = generate_report(report_type, entity, period, **kwargs)

                if generated_files:
                    st.success("✅ Report generated successfully!")

                    # Display generated files
                    st.markdown("### 📥 Generated Files")

                    cols = st.columns(len(generated_files))
                    for idx, (format_type, file_path) in enumerate(generated_files.items()):
                        with cols[idx]:
                            file_path_obj = (
                                Path(file_path)
                                if isinstance(file_path, str)
                                else Path(file_path[0]) if isinstance(file_path, list) else None
                            )

                            if file_path_obj and file_path_obj.exists():
                                file_size = file_path_obj.stat().st_size / 1024  # KB

                                st.markdown(f"**{format_type.upper()}**")
                                st.caption(f"Size: {file_size:.1f} KB")
                                st.caption(f"📂 {file_path_obj.name}")

                                # Download button
                                with open(file_path_obj, "rb") as f:
                                    st.download_button(
                                        label=f"💾 Download {format_type.upper()}",
                                        data=f,
                                        file_name=file_path_obj.name,
                                        mime=f"application/{format_type}",
                                        key=f"download_{format_type}_{idx}",
                                    )
                            elif isinstance(file_path, list):
                                # Multiple files (e.g., PNG charts)
                                st.markdown(f"**{format_type.upper()}** ({len(file_path)} files)")
                                for i, fp in enumerate(file_path):
                                    fp_obj = Path(fp)
                                    if fp_obj.exists():
                                        with open(fp_obj, "rb") as f:
                                            st.download_button(
                                                label=f"💾 {fp_obj.name}",
                                                data=f,
                                                file_name=fp_obj.name,
                                                mime="image/png",
                                                key=f"download_{format_type}_{i}_{idx}",
                                            )

                    st.markdown("---")

                    # Quick preview for text/JSON formats
                    if "json" in generated_files:
                        with st.expander("📄 JSON Data Preview"):
                            import json

                            with open(generated_files["json"]) as f:
                                json_data = json.load(f)
                            st.json(json_data)

                    if "markdown" in generated_files:
                        with st.expander("📝 Markdown Preview"):
                            with open(generated_files["markdown"], encoding="utf-8") as f:
                                markdown_content = f.read()
                            st.markdown(markdown_content)
                else:
                    st.error("❌ Report generation failed. No files were created.")

        except Exception as e:
            st.error(f"❌ Error generating report: {e!s}")
            st.exception(e)

    st.markdown("---")

    # Report History (list previously generated reports)
    st.subheader("📚 Report History")

    reports_dir = Path("data/reports")
    if reports_dir.exists():
        report_files = sorted(
            reports_dir.glob("*.*"), key=lambda x: x.stat().st_mtime, reverse=True
        )

        if report_files:
            # Group by report type
            grouped_reports = {}
            for file in report_files[:20]:  # Last 20 reports
                # Extract report type from filename
                parts = file.stem.split("_")
                if len(parts) >= 2:
                    report_key = parts[0]
                    if report_key not in grouped_reports:
                        grouped_reports[report_key] = []
                    grouped_reports[report_key].append(file)

            # Display in tabs
            if grouped_reports:
                tabs = st.tabs([f"{k.title()} ({len(v)})" for k, v in grouped_reports.items()])

                for tab, (report_key, files) in zip(tabs, grouped_reports.items(), strict=False):
                    with tab:
                        for file in files[:10]:  # Show 10 per type
                            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                            with col1:
                                st.text(file.name)
                            with col2:
                                st.caption(f"{file.stat().st_size / 1024:.1f} KB")
                            with col3:
                                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                                st.caption(mtime.strftime("%Y-%m-%d %H:%M"))
                            with col4:
                                with open(file, "rb") as f:
                                    st.download_button(
                                        label="�",
                                        data=f,
                                        file_name=file.name,
                                        key=f"history_{file.name}",
                                    )
        else:
            st.info("No reports generated yet. Generate your first report above!")
    else:
        st.info(
            "Reports directory not found. It will be created when you generate your first report."
        )


# ==============================================
# PAGE 6: AI ASSISTANT (CHAT INTERFACE)
# ==============================================
elif page == "🤖 AI Assistant":
    st.markdown('<div class="main-header">AI Assistant</div>', unsafe_allow_html=True)
    st.markdown("Ask questions about your GL accounts in natural language.")

    # Initialize agent if not exists
    if st.session_state.agent is None:
        with st.spinner("Initializing AI Agent..."):
            try:
                st.session_state.agent = create_agent()
                st.success("✅ AI Agent ready!")
            except Exception as e:
                st.error(f"Error initializing agent: {e!s}")
                st.info("Please ensure GOOGLE_API_KEY is set in environment variables.")

    # Chat interface
    st.markdown("### 💬 Chat History")

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Aura:** {message['content']}")

    # Input
    user_query = st.text_input(
        "Ask a question:", placeholder="e.g., What are the top 5 accounts with largest variances?"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🚀 Ask", type="primary"):
            if user_query and st.session_state.agent:
                st.session_state.chat_history.append({"role": "user", "content": user_query})

                with st.spinner("Thinking..."):
                    try:
                        response = query_agent(st.session_state.agent, user_query)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": response}
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e!s}")
            elif not st.session_state.agent:
                st.warning("AI Agent not initialized. Please check configuration.")

    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.chat_history = []
            st.rerun()


# ==============================================
# PAGE 7: SETTINGS (CONFIGURATION)
# ==============================================
elif page == "⚙️ Settings":
    st.markdown('<div class="main-header">Settings & Configuration</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🗄️ Database", "🔔 Notifications", "ℹ️ About"])

    with tab1:
        st.subheader("Database Connection Status")

        # PostgreSQL
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**PostgreSQL**")
            try:
                accounts = get_gl_accounts_by_period(st.session_state.current_period)
                st.success(f"✅ Connected ({len(accounts)} total accounts)")
            except Exception as e:
                st.error(f"❌ Connection failed: {e!s}")

        # MongoDB
        with col2:
            st.markdown("**MongoDB**")
            try:
                db = get_mongo_database()
                audit_col = get_audit_trail_collection()
                count = audit_col.count_documents({})
                st.success(f"✅ Connected ({count} audit records)")
            except Exception as e:
                st.error(f"❌ Connection failed: {e!s}")

    with tab2:
        st.subheader("Notification Preferences")
        st.checkbox("Email notifications for critical items", value=True)
        st.checkbox("Daily summary reports", value=False)
        st.checkbox("Anomaly alerts", value=True)
        st.number_input("Alert threshold (₹)", value=100000, step=10000)

        if st.button("💾 Save Preferences"):
            st.success("Preferences saved!")

    with tab3:
        st.subheader("About Project Aura")
        st.markdown(
            """
        **Project Aura** is an AI-powered financial statement review agent built for the Adani Group's
        1,000+ entity finance operations.

        **Key Features:**
        - ✅ Automated GL account validation
        - 📊 Real-time analytics and insights
        - 🤖 Natural language query interface
        - 📈 Multi-period trend analysis
        - 🎯 Anomaly detection using ML
        - 📄 Comprehensive reporting

        **Technology Stack:**
        - Python 3.11+
        - Streamlit (UI)
        - PostgreSQL (structured data)
        - MongoDB (documents & audit logs)
        - LangChain + Google Gemini (AI agent)
        - Plotly (visualizations)

        **Version:** 1.0.0
        **Hackathon:** Finnovate 2024
        **Team:** [Your Team Name]
        """
        )

        st.markdown("---")
        st.caption("© 2024 Project Aura. Built for Adani Group's Finnovate Hackathon.")
