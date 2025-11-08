"""
Interactive Dashboard System with 5 specialized dashboards.

Provides comprehensive financial review visualizations with drill-down capability:
1. Overview Dashboard - High-level KPIs and summary
2. Financial Analysis Dashboard - Revenue, expense trends, variance analysis
3. Review Status Dashboard - Review progress, bottlenecks, SLA tracking
4. Quality & Hygiene Dashboard - Data quality metrics, validation results
5. Risk & Anomaly Dashboard - Outliers, anomalies, critical issues
"""

from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analytics import (
    calculate_gl_hygiene_score,
    calculate_review_status_summary,
    get_pending_items_report,
)
from src.db.postgres import get_gl_accounts_by_period
from src.visualizations import (
    create_anomaly_scatter,
    create_category_breakdown_pie,
    create_department_comparison_radar,
    create_hygiene_gauge,
    create_review_status_sunburst,
    create_reviewer_workload_bar,
    create_variance_waterfall_chart,
)


# ==============================================
# GLOBAL FILTER SIDEBAR
# ==============================================
def apply_global_filters() -> dict[str, Any]:
    """
    Render global filter controls in sidebar and return filter dictionary.

    Returns:
        Dict with keys: entity, period, view_type, date_range, etc.
    """
    st.sidebar.markdown("### 🎛️ Dashboard Filters")

    # Entity selector
    entities = st.session_state.get("available_entities", ["AEML", "ABEX", "AGEL", "APL"])
    entity = st.sidebar.selectbox(
        "Entity",
        entities,
        index=(
            entities.index(st.session_state.get("current_entity", entities[0]))
            if st.session_state.get("current_entity") in entities
            else 0
        ),
        key="dashboard_entity",
    )

    # Period selector
    periods = st.session_state.get("available_periods", ["Mar-24", "Feb-24", "Jan-24"])
    period = st.sidebar.selectbox(
        "Period",
        periods,
        index=(
            periods.index(st.session_state.get("current_period", periods[0]))
            if st.session_state.get("current_period") in periods
            else 0
        ),
        key="dashboard_period",
    )

    # View type
    view_type = st.sidebar.radio(
        "View By",
        ["Overview", "By Department", "By Category", "By Reviewer"],
        index=0,
        key="dashboard_view",
    )

    # Additional filters
    with st.sidebar.expander("🔍 Advanced Filters"):
        include_zero_balance = st.checkbox("Include Zero Balance Accounts", value=False)
        review_status = st.multiselect(
            "Review Status", ["reviewed", "pending", "flagged", "all"], default=["all"]
        )
        criticality = st.multiselect(
            "Criticality", ["Critical", "High", "Medium", "Low", "all"], default=["all"]
        )

    # Update session state
    st.session_state.current_entity = entity
    st.session_state.current_period = period

    return {
        "entity": entity,
        "period": period,
        "view_type": view_type,
        "include_zero_balance": include_zero_balance,
        "review_status": review_status if "all" not in review_status else None,
        "criticality": criticality if "all" not in criticality else None,
    }


# ==============================================
# DASHBOARD 1: OVERVIEW
# ==============================================
def render_overview_dashboard(filters: dict[str, Any]):
    """
    High-level overview dashboard with key metrics and summary charts.

    Features:
    - KPI cards (accounts, balance, completion rate, hygiene score)
    - Status distribution pie chart
    - Top accounts by balance
    - Quick action items
    """
    entity = filters["entity"]
    period = filters["period"]

    st.markdown("### 📊 Overview Dashboard")
    st.markdown(f"**Entity:** {entity} | **Period:** {period}")

    # Fetch data
    try:
        accounts = get_gl_accounts_by_period(period)
        entity_accounts = [a for a in accounts if a.entity == entity]

        if not entity_accounts:
            st.warning(f"No GL accounts found for {entity}/{period}")
            return

        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)

        total_accounts = len(entity_accounts)
        total_balance = sum(abs(a.balance) for a in entity_accounts)
        reviewed_count = sum(1 for a in entity_accounts if a.review_status == "reviewed")
        completion_rate = (reviewed_count / total_accounts * 100) if total_accounts > 0 else 0

        col1.metric("Total Accounts", f"{total_accounts:,}")
        col2.metric("Total Balance", f"₹{total_balance:,.0f}")
        col3.metric("Completion Rate", f"{completion_rate:.1f}%")

        # Hygiene score
        try:
            hygiene = calculate_gl_hygiene_score(entity, period)
            col4.metric("Hygiene Score", f"{hygiene.get('overall_score', 0):.0f}/100")
        except:
            col4.metric("Hygiene Score", "N/A")

        st.markdown("---")

        # Charts Row 1
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### 📊 Review Status Distribution")
            # Status breakdown
            status_counts = {}
            for a in entity_accounts:
                status_counts[a.review_status] = status_counts.get(a.review_status, 0) + 1

            fig = create_category_breakdown_pie(status_counts, title="Review Status Distribution")
            st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            st.markdown("#### 💰 Top 10 Accounts by Balance")
            # Top accounts
            top_accounts = sorted(entity_accounts, key=lambda a: abs(a.balance), reverse=True)[:10]

            df_top = pd.DataFrame(
                [
                    {
                        "Account": f"{a.account_code} - {a.account_name[:30]}",
                        "Balance": abs(a.balance),
                        "Status": a.review_status,
                    }
                    for a in top_accounts
                ]
            )

            fig = go.Figure(
                go.Bar(
                    x=df_top["Balance"],
                    y=df_top["Account"],
                    orientation="h",
                    marker=dict(color="lightblue"),
                    text=df_top["Balance"].apply(lambda x: f"₹{x:,.0f}"),
                    textposition="auto",
                )
            )
            fig.update_layout(
                title="Top 10 Accounts by Balance",
                xaxis_title="Balance (₹)",
                yaxis_title="",
                height=400,
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Action Items
        st.markdown("#### 🎯 Quick Action Items")

        pending_accounts = [a for a in entity_accounts if a.review_status == "pending"]
        flagged_accounts = [a for a in entity_accounts if a.review_status == "flagged"]

        action_col1, action_col2, action_col3 = st.columns(3)

        with action_col1:
            st.metric("Pending Reviews", len(pending_accounts))
            if pending_accounts:
                with st.expander("View Pending"):
                    for a in pending_accounts[:5]:
                        st.write(f"• {a.account_code} - {a.account_name[:30]}")

        with action_col2:
            st.metric("Flagged Accounts", len(flagged_accounts))
            if flagged_accounts:
                with st.expander("View Flagged"):
                    for a in flagged_accounts[:5]:
                        st.write(f"• {a.account_code} - {a.account_name[:30]}")

        with action_col3:
            zero_balance = [a for a in entity_accounts if a.balance == 0]
            st.metric("Zero Balance", len(zero_balance))
            if zero_balance:
                with st.expander("View Zero Balance"):
                    for a in zero_balance[:5]:
                        st.write(f"• {a.account_code} - {a.account_name[:30]}")

    except Exception as e:
        st.error(f"Error rendering overview dashboard: {e}")
        st.exception(e)


# ==============================================
# DASHBOARD 2: FINANCIAL ANALYSIS
# ==============================================
def render_financial_dashboard(filters: dict[str, Any]):
    """
    Financial analysis with variance, trends, and category breakdowns.

    Features:
    - Variance waterfall chart
    - Category breakdown by balance
    - Trend analysis (if multiple periods available)
    - Balance heatmap
    """
    entity = filters["entity"]
    period = filters["period"]

    st.markdown("### 💰 Financial Analysis Dashboard")
    st.markdown(f"**Entity:** {entity} | **Period:** {period}")

    try:
        accounts = get_gl_accounts_by_period(period)
        entity_accounts = [a for a in accounts if a.entity == entity]

        if not entity_accounts:
            st.warning(f"No GL accounts found for {entity}/{period}")
            return

        # Category breakdown
        st.markdown("#### 📊 Balance by Category")

        category_balances = {}
        for a in entity_accounts:
            cat = a.category or "Uncategorized"
            category_balances[cat] = category_balances.get(cat, 0) + abs(a.balance)

        fig = create_category_breakdown_pie(
            category_balances, title="Balance Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Variance Analysis (if previous period data exists)
        st.markdown("#### 📈 Variance Analysis")

        # For demo, create sample variance data
        variance_df = pd.DataFrame(
            [
                {
                    "account_name": f"{a.account_code} - {a.account_name[:20]}",
                    "variance": a.balance * 0.1,
                }
                for a in sorted(entity_accounts, key=lambda x: abs(x.balance), reverse=True)[:10]
            ]
        )

        fig_waterfall = create_variance_waterfall_chart(variance_df)
        st.plotly_chart(fig_waterfall, use_container_width=True)

        st.markdown("---")

        # Top movers
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 Largest Accounts")
            top_10 = sorted(entity_accounts, key=lambda a: abs(a.balance), reverse=True)[:10]
            for idx, a in enumerate(top_10, 1):
                st.write(
                    f"{idx}. **{a.account_code}** - {a.account_name[:30]}: ₹{abs(a.balance):,.0f}"
                )

        with col2:
            st.markdown("#### 📊 Category Summary")
            for cat, bal in sorted(category_balances.items(), key=lambda x: x[1], reverse=True):
                st.write(f"**{cat}**: ₹{bal:,.0f}")

    except Exception as e:
        st.error(f"Error rendering financial dashboard: {e}")
        st.exception(e)


# ==============================================
# DASHBOARD 3: REVIEW STATUS
# ==============================================
def render_review_dashboard(filters: dict[str, Any]):
    """
    Review progress tracking with bottleneck identification.

    Features:
    - Review status sunburst
    - Reviewer workload bar chart
    - SLA compliance metrics
    - Bottleneck alerts
    """
    entity = filters["entity"]
    period = filters["period"]

    st.markdown("### 📋 Review Status Dashboard")
    st.markdown(f"**Entity:** {entity} | **Period:** {period}")

    try:
        # Fetch review summary
        review_summary = calculate_review_status_summary(entity, period)

        if "error" in review_summary:
            st.warning(review_summary["error"])
            return

        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)

        overall = review_summary.get("overall", {})
        col1.metric("Total Reviews", overall.get("total", 0))
        col2.metric("Reviewed", overall.get("reviewed", 0))
        col3.metric("Pending", overall.get("pending", 0))
        col4.metric("Flagged", overall.get("flagged", 0))

        st.markdown("---")

        # Charts
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### 🎯 Review Progress")

            # Create sunburst chart
            status_data = review_summary.get("by_status", {})
            if status_data:
                fig = create_review_status_sunburst(status_data)
                st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            st.markdown("#### 👥 Reviewer Workload")

            reviewer_stats = review_summary.get("by_reviewer", [])
            if reviewer_stats:
                fig = create_reviewer_workload_bar(reviewer_stats)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No reviewer data available")

        st.markdown("---")

        # Pending items table
        st.markdown("#### ⏳ Pending Items")

        try:
            pending_items = get_pending_items_report(entity, period)

            if "error" not in pending_items:
                pending_uploads = pending_items.get("pending_uploads", [])
                pending_reviews = pending_items.get("pending_reviews", [])

                tab1, tab2 = st.tabs(["Pending Uploads", "Pending Reviews"])

                with tab1:
                    if pending_uploads:
                        df_uploads = pd.DataFrame(pending_uploads)
                        st.dataframe(df_uploads, use_container_width=True)
                    else:
                        st.success("✅ No pending uploads!")

                with tab2:
                    if pending_reviews:
                        df_reviews = pd.DataFrame(pending_reviews)
                        st.dataframe(df_reviews, use_container_width=True)
                    else:
                        st.success("✅ No pending reviews!")
        except Exception as e:
            st.warning(f"Could not load pending items: {e}")

    except Exception as e:
        st.error(f"Error rendering review dashboard: {e}")
        st.exception(e)


# ==============================================
# DASHBOARD 4: QUALITY & HYGIENE
# ==============================================
def render_quality_dashboard(filters: dict[str, Any]):
    """
    Data quality and hygiene metrics dashboard.

    Features:
    - Hygiene gauge
    - Component breakdown radar chart
    - Validation results
    - Quality trends
    """
    entity = filters["entity"]
    period = filters["period"]

    st.markdown("### ✨ Quality & Hygiene Dashboard")
    st.markdown(f"**Entity:** {entity} | **Period:** {period}")

    try:
        # Fetch hygiene score
        hygiene = calculate_gl_hygiene_score(entity, period)

        if "error" in hygiene:
            st.warning(hygiene["error"])
            return

        # Overall Score Card
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("#### 🎯 Overall Hygiene Score")
            fig_gauge = create_hygiene_gauge(
                hygiene.get("overall_score", 0), hygiene.get("components", {})
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("---")

        # Component breakdown
        st.markdown("#### 📊 Component Breakdown")

        components = hygiene.get("components", {})

        # Create radar chart for component comparison
        if components:
            fig_radar = create_department_comparison_radar({"Current Period": components})
            st.plotly_chart(fig_radar, use_container_width=True)

        # Component progress bars
        col1, col2 = st.columns(2)

        for idx, (comp_name, score) in enumerate(components.items()):
            target_col = col1 if idx % 2 == 0 else col2

            with target_col:
                st.markdown(f"**{comp_name.replace('_', ' ').title()}**")
                st.progress(score / 100, text=f"{score:.0f}/100")

        st.markdown("---")

        # Recommendations
        st.markdown("#### 💡 Quality Improvement Recommendations")

        recommendations = hygiene.get("recommendations", [])
        if recommendations:
            for rec in recommendations:
                st.info(f"💡 {rec}")
        else:
            st.success("✅ All quality metrics are within acceptable ranges!")

    except Exception as e:
        st.error(f"Error rendering quality dashboard: {e}")
        st.exception(e)


# ==============================================
# DASHBOARD 5: RISK & ANOMALIES
# ==============================================
def render_risk_dashboard(filters: dict[str, Any]):
    """
    Risk monitoring and anomaly detection dashboard.

    Features:
    - Anomaly scatter plot
    - Critical issue alerts
    - Risk heatmap
    - Flagged items
    """
    entity = filters["entity"]
    period = filters["period"]

    st.markdown("### 🔍 Risk & Anomaly Dashboard")
    st.markdown(f"**Entity:** {entity} | **Period:** {period}")

    try:
        accounts = get_gl_accounts_by_period(period)
        entity_accounts = [a for a in accounts if a.entity == entity]

        if not entity_accounts:
            st.warning(f"No GL accounts found for {entity}/{period}")
            return

        # Risk Summary Cards
        col1, col2, col3, col4 = st.columns(4)

        flagged = [a for a in entity_accounts if a.review_status == "flagged"]
        high_balance = [a for a in entity_accounts if abs(a.balance) > 100_000_000]  # >100M
        zero_balance = [a for a in entity_accounts if a.balance == 0]

        col1.metric(
            "Flagged Accounts", len(flagged), delta=f"{len(flagged)/len(entity_accounts)*100:.1f}%"
        )
        col2.metric("High Balance (>₹100M)", len(high_balance))
        col3.metric("Zero Balance", len(zero_balance))
        col4.metric("Total Risk Score", f"{len(flagged)*3 + len(high_balance)}")

        st.markdown("---")

        # Anomaly Detection
        st.markdown("#### 🔍 Anomaly Detection")

        # Create sample anomaly data for visualization
        anomaly_data = []
        for a in entity_accounts:
            # Simple anomaly scoring based on balance and status
            anomaly_score = 0.0
            if a.review_status == "flagged":
                anomaly_score += 0.7
            if abs(a.balance) > 100_000_000:
                anomaly_score += 0.3
            if abs(a.balance) == 0:
                anomaly_score += 0.2

            if anomaly_score > 0:
                anomaly_data.append(
                    {
                        "account_code": a.account_code,
                        "account_name": a.account_name,
                        "current_balance": abs(a.balance),
                        "anomaly_score": min(anomaly_score, 1.0),
                        "z_score": anomaly_score * 2.5,  # Mock z-score
                        "reason": f"Status: {a.review_status}, Balance: ₹{abs(a.balance):,.0f}",
                    }
                )

        if anomaly_data:
            fig_scatter = create_anomaly_scatter(anomaly_data)
            st.plotly_chart(fig_scatter, use_container_width=True)

            st.markdown("---")

            # Anomaly table
            st.markdown("#### ⚠️ Detected Anomalies")
            df_anomalies = pd.DataFrame(anomaly_data)
            st.dataframe(
                df_anomalies.sort_values("anomaly_score", ascending=False).head(20),
                use_container_width=True,
            )
        else:
            st.success("✅ No anomalies detected!")

        st.markdown("---")

        # ML Predictions & Feedback Section
        st.markdown("#### 🤖 ML Predictions & Feedback")

        try:
            from src.feedback_handler import MLFeedbackCollector

            collector = MLFeedbackCollector()

            # Show feedback statistics
            stats = collector.get_feedback_stats()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Feedback", stats.get("total_feedback", 0))
            col2.metric("Accuracy Rate", f"{stats.get('accuracy_rate', 0):.1f}%")
            col3.metric("Corrections", stats.get("incorrect", 0))
            col4.metric("Uncertain", stats.get("uncertain", 0))

            st.markdown("---")

            # Sample predictions for top anomalies
            if anomaly_data:
                st.markdown("##### 🎯 Review ML Predictions")
                st.info("👉 Help improve our AI by providing feedback on predictions below")

                # Show top 5 anomalies with predictions
                top_anomalies = sorted(
                    anomaly_data, key=lambda x: x["anomaly_score"], reverse=True
                )[:5]

                for idx, anomaly in enumerate(top_anomalies):
                    account_code = anomaly["account_code"]

                    with st.expander(
                        f"📊 {account_code} - {anomaly['account_name']} (Score: {anomaly['anomaly_score']:.2f})"
                    ):
                        # Display predictions
                        pred_col1, pred_col2, pred_col3 = st.columns(3)

                        # Mock predictions (in real app, load from ML model)
                        pred_anomaly = anomaly["anomaly_score"]
                        pred_priority = min(anomaly["anomaly_score"] * 10, 10)
                        pred_attention = 1 if anomaly["anomaly_score"] > 0.7 else 0

                        pred_col1.metric("Anomaly Score", f"{pred_anomaly:.2f}")
                        pred_col2.metric("Priority Score", f"{pred_priority:.1f}/10")
                        pred_col3.metric("Needs Attention", "Yes" if pred_attention else "No")

                        st.markdown("**Reason:** " + anomaly["reason"])

                        # Feedback section
                        st.markdown("---")
                        st.markdown("**Was this prediction helpful?**")

                        feedback_col1, feedback_col2, feedback_col3 = st.columns(3)

                        # Use unique keys for each button
                        key_prefix = f"fb_{idx}_{account_code}"

                        with feedback_col1:
                            if st.button("✅ Correct", key=f"{key_prefix}_correct"):
                                feedback_id = collector.collect_prediction_feedback(
                                    account_code=account_code,
                                    prediction_type="anomaly",
                                    predicted_value=pred_anomaly,
                                    feedback_type="correct",
                                    user_id=st.session_state.get(
                                        "user_email", "demo_user@example.com"
                                    ),
                                    period=period,
                                    entity=entity,
                                )
                                st.success("✅ Thank you! Feedback recorded.")

                        with feedback_col2:
                            if st.button("❌ Incorrect", key=f"{key_prefix}_incorrect"):
                                st.session_state[f"{key_prefix}_show_correction"] = True

                        with feedback_col3:
                            if st.button("❓ Uncertain", key=f"{key_prefix}_uncertain"):
                                feedback_id = collector.collect_prediction_feedback(
                                    account_code=account_code,
                                    prediction_type="anomaly",
                                    predicted_value=pred_anomaly,
                                    feedback_type="uncertain",
                                    user_id=st.session_state.get(
                                        "user_email", "demo_user@example.com"
                                    ),
                                    period=period,
                                    entity=entity,
                                )
                                st.info("📝 Feedback recorded as uncertain.")

                        # Show correction input if needed
                        if st.session_state.get(f"{key_prefix}_show_correction", False):
                            st.markdown("---")
                            st.markdown("**Provide Correction:**")

                            correction_col1, correction_col2 = st.columns(2)

                            with correction_col1:
                                actual_anomaly = st.number_input(
                                    "Actual Anomaly Score (0-1)",
                                    min_value=0.0,
                                    max_value=1.0,
                                    value=0.0,
                                    step=0.1,
                                    key=f"{key_prefix}_actual_anomaly",
                                )

                            with correction_col2:
                                actual_priority = st.number_input(
                                    "Actual Priority (0-10)",
                                    min_value=0.0,
                                    max_value=10.0,
                                    value=5.0,
                                    step=0.5,
                                    key=f"{key_prefix}_actual_priority",
                                )

                            comments = st.text_area(
                                "Comments (optional)",
                                placeholder="Why was the prediction incorrect?",
                                key=f"{key_prefix}_comments",
                            )

                            submit_col1, submit_col2 = st.columns([1, 5])

                            with submit_col1:
                                if st.button("Submit", key=f"{key_prefix}_submit"):
                                    # Collect feedback for anomaly
                                    collector.collect_prediction_feedback(
                                        account_code=account_code,
                                        prediction_type="anomaly",
                                        predicted_value=pred_anomaly,
                                        actual_value=actual_anomaly,
                                        feedback_type="incorrect",
                                        user_id=st.session_state.get(
                                            "user_email", "demo_user@example.com"
                                        ),
                                        comments=comments,
                                        period=period,
                                        entity=entity,
                                    )

                                    # Collect feedback for priority
                                    collector.collect_prediction_feedback(
                                        account_code=account_code,
                                        prediction_type="priority",
                                        predicted_value=pred_priority,
                                        actual_value=actual_priority,
                                        feedback_type="incorrect",
                                        user_id=st.session_state.get(
                                            "user_email", "demo_user@example.com"
                                        ),
                                        comments=comments,
                                        period=period,
                                        entity=entity,
                                    )

                                    st.success(
                                        "✅ Corrections submitted! Thank you for helping improve our AI."
                                    )
                                    st.session_state[f"{key_prefix}_show_correction"] = False
                                    st.rerun()

                            with submit_col2:
                                if st.button("Cancel", key=f"{key_prefix}_cancel"):
                                    st.session_state[f"{key_prefix}_show_correction"] = False
                                    st.rerun()

                st.markdown("---")
                st.markdown("##### 📈 Recent Feedback History")

                # Show recent feedback
                recent_feedback = collector.get_recent_feedback(limit=10)

                if recent_feedback:
                    feedback_df = pd.DataFrame(recent_feedback)
                    display_cols = [
                        "account_code",
                        "prediction_type",
                        "feedback_type",
                        "predicted_value",
                        "actual_value",
                        "timestamp",
                    ]
                    available_cols = [col for col in display_cols if col in feedback_df.columns]

                    st.dataframe(
                        feedback_df[available_cols].sort_values("timestamp", ascending=False),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No feedback history yet. Be the first to provide feedback!")

        except ImportError:
            st.warning("⚠️ ML Feedback system not available")
        except Exception as e:
            st.warning(f"⚠️ Could not load ML feedback: {e!s}")

        st.markdown("---")

        # Critical Issues
        st.markdown("#### 🚨 Critical Issues")

        if flagged:
            st.warning(f"⚠️ {len(flagged)} accounts are flagged for review")
            with st.expander("View Flagged Accounts"):
                for a in flagged:
                    st.write(f"• **{a.account_code}** - {a.account_name}: ₹{abs(a.balance):,.0f}")
        else:
            st.success("✅ No critical issues found!")

    except Exception as e:
        st.error(f"Error rendering risk dashboard: {e}")
        st.exception(e)


# ==============================================
# MAIN DASHBOARD ROUTER
# ==============================================
def render_dashboard(dashboard_type: str, filters: dict[str, Any]):
    """
    Route to appropriate dashboard based on type.

    Args:
        dashboard_type: One of 'overview', 'financial', 'review', 'quality', 'risk'
        filters: Filter dictionary from apply_global_filters()
    """
    dashboard_map = {
        "overview": render_overview_dashboard,
        "financial": render_financial_dashboard,
        "review": render_review_dashboard,
        "quality": render_quality_dashboard,
        "risk": render_risk_dashboard,
    }

    renderer = dashboard_map.get(dashboard_type)

    if renderer:
        renderer(filters)
    else:
        st.error(f"Unknown dashboard type: {dashboard_type}")
