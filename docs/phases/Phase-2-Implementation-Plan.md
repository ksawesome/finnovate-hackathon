# Phase 2: Advanced Features & Production Readiness - Implementation Plan

**Status**: 🚧 In Progress
**Start Date**: November 8, 2025
**Target Completion**: November 9, 2025 (Day 2)
**Goal**: Build state-of-the-art features to win hackathon

---

## Executive Summary

Phase 2 transforms Project Aura from a functional data pipeline into a **state-of-the-art AI-powered financial review assistant**. This phase adds the critical features that will impress hackathon judges: automated report generation, interactive dashboards, ML-powered insights, conversational AI agent, and production-grade polish.

**Key Objectives**:
1. Close all gaps from Phase 1 (missing features, incomplete modules)
2. Build automated report generation engine with PDF/CSV export
3. Create interactive Plotly dashboards with drill-down capability
4. Implement ML learning loop with user feedback
5. Enhance agentic behavior with RAG and structured tools
6. Add email automation system for workflow notifications

**Success Criteria**:
- ✅ All Phase 1 gaps closed (100% feature parity with problem statement)
- ✅ 5+ automated report types with visual exports
- ✅ Interactive dashboard with ≥10 chart types and drill-downs
- ✅ ML model trained with ≥80% accuracy and feedback loop
- ✅ Conversational agent with RAG answering ≥20 accounting questions
- ✅ Email notification system with 6+ template types
- ✅ Test coverage ≥85% for all new modules
- ✅ Demo-ready with ≤3 second response times

---

## Part 0: Phase 1 Gap Closure & Foundation Strengthening

**Duration**: 2-3 hours
**Priority**: 🔴 CRITICAL - Must complete before starting new features
**Goal**: Ensure solid foundation before building advanced features

### 0.1 Missing Core Features from Problem Statement

#### **Gap 0.1.1: Analytics Module Enhancement** 🔴
**Current State**:
- ✅ `src/analytics.py` exists with basic `perform_analytics()` function
- ❌ Only returns simple aggregations (total_balance, mean_balance, pending_reviews)
- ❌ No variance calculation
- ❌ No period comparison
- ❌ No drill-down by entity/department/category

**Required Enhancements**:
```python
# src/analytics.py - MUST ADD

def calculate_variance_analysis(entity: str, current_period: str, previous_period: str) -> dict:
    """
    Calculate period-over-period variance for all GL accounts.

    Returns:
        {
            'total_accounts': int,
            'variance_summary': {
                'total_variance': float,
                'avg_variance_pct': float,
                'max_increase': {'account': str, 'amount': float, 'pct': float},
                'max_decrease': {'account': str, 'amount': float, 'pct': float}
            },
            'major_variances': [  # >10% or >50k threshold
                {
                    'account_code': str,
                    'account_name': str,
                    'current_balance': float,
                    'previous_balance': float,
                    'variance_amount': float,
                    'variance_pct': float,
                    'flag': 'increase' | 'decrease'
                }
            ],
            'variance_by_category': {
                'Assets': {'total_variance': float, 'account_count': int},
                'Liabilities': {...},
                'Revenue': {...},
                'Expenses': {...}
            }
        }
    """
    pass

def calculate_review_status_summary(entity: str, period: str) -> dict:
    """
    Comprehensive review status across all dimensions.

    Returns:
        {
            'overall': {
                'total_accounts': int,
                'reviewed': int,
                'pending': int,
                'flagged': int,
                'completion_pct': float
            },
            'by_department': {
                'Finance': {'total': int, 'reviewed': int, 'pending': int},
                'Treasury': {...},
                ...
            },
            'by_criticality': {
                'Critical': {'total': int, 'reviewed': int, 'pending': int},
                'High': {...},
                'Medium': {...},
                'Low': {...}
            },
            'by_reviewer': [
                {
                    'name': str,
                    'email': str,
                    'assigned': int,
                    'completed': int,
                    'pending': int,
                    'completion_pct': float,
                    'avg_days_to_review': float
                }
            ],
            'sla_compliance': {
                'on_time': int,
                'delayed': int,
                'at_risk': int,  # Within 24h of deadline
                'compliance_pct': float
            }
        }
    """
    pass

def calculate_gl_hygiene_score(entity: str, period: str) -> dict:
    """
    Calculate overall GL hygiene score (0-100).

    Scoring Components:
    - Trial balance check (Debits = Credits): 25 points
    - Supporting documentation uploaded: 20 points
    - Review completion rate: 20 points
    - SLA compliance: 15 points
    - Data quality (no nulls, valid formats): 10 points
    - Zero balance accounts handled: 10 points

    Returns:
        {
            'overall_score': float,  # 0-100
            'grade': 'A' | 'B' | 'C' | 'D' | 'F',
            'components': {
                'trial_balance': {'score': float, 'max': 25, 'status': str},
                'documentation': {'score': float, 'max': 20, 'status': str},
                'review_completion': {'score': float, 'max': 20, 'status': str},
                'sla_compliance': {'score': float, 'max': 15, 'status': str},
                'data_quality': {'score': float, 'max': 10, 'status': str},
                'zero_balance_handling': {'score': float, 'max': 10, 'status': str}
            },
            'recommendations': [str],  # Action items to improve score
            'trend': {
                'previous_score': float,
                'change': float,
                'direction': 'improving' | 'declining' | 'stable'
            }
        }
    """
    pass

def get_pending_items_report(entity: str, period: str) -> dict:
    """
    Detailed report of all pending items by type.

    Returns:
        {
            'pending_uploads': [
                {
                    'account_code': str,
                    'account_name': str,
                    'assigned_to': str,
                    'department': str,
                    'due_date': datetime,
                    'days_overdue': int,
                    'balance': float,
                    'criticality': str
                }
            ],
            'pending_reviews': [...],  # Similar structure
            'pending_approvals': [...],  # Similar structure
            'summary': {
                'total_pending_uploads': int,
                'total_pending_reviews': int,
                'total_pending_approvals': int,
                'critical_pending': int,
                'overdue_count': int
            }
        }
    """
    pass

def identify_anomalies_ml(entity: str, period: str, threshold: float = 2.0) -> dict:
    """
    ML-based anomaly detection using statistical methods.

    Uses:
    - Z-score analysis for balance outliers
    - Isolation Forest for pattern detection
    - Historical trend comparison

    Returns:
        {
            'statistical_outliers': [
                {
                    'account_code': str,
                    'account_name': str,
                    'current_balance': float,
                    'z_score': float,
                    'anomaly_score': float,
                    'reason': str
                }
            ],
            'pattern_anomalies': [...],
            'trend_breaks': [...],  # Sudden changes in trend
            'total_anomalies': int,
            'severity_distribution': {'high': int, 'medium': int, 'low': int}
        }
    """
    pass

def export_analytics_to_csv(analytics_dict: dict, output_path: str) -> str:
    """Export any analytics result to CSV for download."""
    pass

def export_analytics_to_excel(analytics_dict: dict, output_path: str) -> str:
    """Export analytics with multiple sheets to Excel."""
    pass
```

**Acceptance Criteria**:
- ✅ All 7 analytics functions implemented with comprehensive return types
- ✅ Unit tests for each function with sample data
- ✅ Performance: Each function completes in <500ms for 501 records
- ✅ Integration tests with real PostgreSQL data

---

#### **Gap 0.1.2: Insights Module Completion** 🔴
**Current State**:
- ✅ `src/insights.py` exists with placeholder functions
- ❌ `generate_insights()` only returns simple balance sum
- ❌ `drill_down_analysis()` only does basic filtering
- ❌ No proactive insight generation

**Required Enhancements**:
```python
# src/insights.py - MUST ADD

def generate_proactive_insights(entity: str, period: str) -> list[dict]:
    """
    AI-powered proactive insights that surface important findings.

    Insights Types:
    1. Expense warnings: "Expense X is 3x previous period"
    2. Missing documentation: "5 critical accounts missing supporting docs"
    3. SLA risks: "12 accounts at risk of missing deadline"
    4. Pattern changes: "Cash balances decreased 40% - investigate"
    5. Reviewer bottlenecks: "User X has 25 pending reviews"

    Returns:
        [
            {
                'type': 'warning' | 'info' | 'critical',
                'category': str,  # expense, documentation, sla, pattern, workload
                'title': str,
                'description': str,
                'affected_accounts': [str],
                'recommended_action': str,
                'priority': int,  # 1-5
                'timestamp': datetime
            }
        ]
    """
    pass

def generate_executive_summary(entity: str, period: str) -> dict:
    """
    Executive-ready summary for leadership.

    Returns:
        {
            'period': str,
            'entity': str,
            'generated_at': datetime,
            'key_metrics': {
                'total_gl_accounts': int,
                'total_balance': float,
                'net_income': float,
                'total_assets': float,
                'total_liabilities': float
            },
            'review_status': {
                'completion_rate': float,
                'on_time_rate': float,
                'critical_issues': int
            },
            'highlights': [str],  # Top 3-5 bullet points
            'concerns': [str],  # Top 3-5 issues requiring attention
            'recommendations': [str],  # Next steps
            'comparison_to_previous': {
                'revenue_change': float,
                'expense_change': float,
                'major_movements': [str]
            }
        }
    """
    pass

def generate_drill_down_report(
    entity: str,
    period: str,
    dimension: str,  # 'department', 'category', 'reviewer', 'criticality'
    value: str
) -> dict:
    """
    Detailed drill-down report for specific dimension.

    Example: dimension='department', value='Finance'
    Returns all Finance department GL accounts with full details.
    """
    pass

def compare_multi_period(
    entity: str,
    periods: list[str]  # e.g., ['2024-01', '2024-02', '2024-03']
) -> dict:
    """
    Multi-period trend analysis.

    Returns:
        {
            'periods': [str],
            'trend_data': {
                'total_balance': [float],  # One per period
                'account_count': [int],
                'review_completion': [float]
            },
            'growing_accounts': [...],  # Accounts with upward trend
            'declining_accounts': [...],
            'volatile_accounts': [...],  # High variance across periods
            'regression_analysis': {
                'revenue_trend': {'slope': float, 'r_squared': float},
                'expense_trend': {...}
            }
        }
    """
    pass
```

**Acceptance Criteria**:
- ✅ All 4 insight functions implemented
- ✅ Proactive insights generate ≥5 relevant findings per entity
- ✅ Executive summary fits on 1 page (PDF ready)
- ✅ Multi-period comparison handles up to 12 periods

---

#### **Gap 0.1.3: Visualization Module Enhancement** 🔴
**Current State**:
- ✅ `src/visualizations.py` exists with 1 placeholder chart
- ❌ Only `create_dashboard_charts()` with simple bar chart
- ❌ No chart variety (pie, gauge, waterfall, heatmap, etc.)
- ❌ No interactivity configuration
- ❌ No export to static images

**Required Enhancements**:
```python
# src/visualizations.py - MUST ADD

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_variance_waterfall_chart(variance_df: pd.DataFrame) -> go.Figure:
    """
    Waterfall chart showing period-over-period changes.

    Args:
        variance_df: Columns ['account_name', 'variance_amount', 'category']

    Returns:
        Plotly waterfall chart with hover details
    """
    pass

def create_hygiene_gauge(hygiene_score: float, components: dict) -> go.Figure:
    """
    Gauge chart showing GL hygiene score 0-100.

    Color bands:
    - 0-60: Red (Poor)
    - 60-75: Orange (Fair)
    - 75-85: Yellow (Good)
    - 85-95: Light Green (Very Good)
    - 95-100: Dark Green (Excellent)
    """
    pass

def create_review_status_sunburst(status_data: dict) -> go.Figure:
    """
    Sunburst chart showing review status hierarchy.

    Levels:
    1. Overall status (Reviewed, Pending, Flagged)
    2. By department
    3. By criticality
    """
    pass

def create_sla_timeline_gantt(assignments: list[dict]) -> go.Figure:
    """
    Gantt chart showing assignment timelines vs SLA deadlines.

    Shows:
    - Assignment date
    - Current status
    - Due date
    - Completion date (if done)
    - Overdue items in red
    """
    pass

def create_variance_heatmap(
    variance_data: pd.DataFrame,  # Rows=accounts, Cols=periods
    title: str = "GL Account Variance Heatmap"
) -> go.Figure:
    """
    Heatmap showing variance patterns across accounts and time.

    Color scale: Red (negative) → White (no change) → Green (positive)
    """
    pass

def create_department_comparison_radar(dept_metrics: dict) -> go.Figure:
    """
    Radar chart comparing departments on multiple metrics.

    Metrics:
    - Completion rate
    - SLA compliance
    - Documentation quality
    - Average review time
    - Issue count
    """
    pass

def create_trend_line_chart(
    trend_data: dict,  # Keys=metric_name, Values=list of values
    periods: list[str],
    title: str = "Trend Analysis"
) -> go.Figure:
    """
    Multi-line chart showing trends over time.

    Supports:
    - Multiple metrics on same chart
    - Hover tooltips with details
    - Range selector
    - Export buttons
    """
    pass

def create_category_breakdown_pie(category_data: dict) -> go.Figure:
    """
    Pie chart with pull-out effect for major categories.

    Shows distribution by:
    - Account category (Assets, Liabilities, Revenue, Expenses)
    - With percentage labels
    - Click to drill down
    """
    pass

def create_reviewer_workload_bar(reviewer_stats: list[dict]) -> go.Figure:
    """
    Horizontal bar chart showing reviewer workload.

    Bars:
    - Assigned (total)
    - Completed (stacked)
    - Pending (stacked)
    - Color-coded by urgency
    """
    pass

def create_anomaly_scatter(anomaly_data: list[dict]) -> go.Figure:
    """
    Scatter plot showing anomalies by balance vs z-score.

    Features:
    - Size = balance magnitude
    - Color = severity
    - Hover = account details
    """
    pass

def export_chart_to_png(fig: go.Figure, output_path: str, width: int = 1200, height: int = 800):
    """Export Plotly chart to static PNG image."""
    pass

def export_chart_to_html(fig: go.Figure, output_path: str):
    """Export interactive Plotly chart to standalone HTML."""
    pass

def create_dashboard_layout(charts: list[go.Figure], layout: str = 'grid') -> go.Figure:
    """
    Combine multiple charts into dashboard layout.

    Layouts:
    - 'grid': 2x2 or 3x2 grid
    - 'vertical': Stack vertically
    - 'tabs': Separate tabs (requires Streamlit wrapper)
    """
    pass
```

**Acceptance Criteria**:
- ✅ All 13 chart functions implemented with Plotly
- ✅ Each chart has hover tooltips and interactivity
- ✅ Export functions tested for PNG and HTML
- ✅ Charts render in <2 seconds for 501 records
- ✅ All charts have professional styling (colors, fonts, legends)

---

#### **Gap 0.1.4: Streamlit App Foundation** 🔴
**Current State**:
- ✅ `src/app.py` exists with basic structure
- ❌ Only file upload widget implemented
- ❌ No navigation between pages
- ❌ No data display tables
- ❌ No chart integration

**Required Enhancements**:
```python
# src/app.py - MUST REWRITE COMPLETELY

import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Project Aura - GL Review Assistant",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        color: white;
    }
    .status-reviewed { background-color: #28a745; }
    .status-pending { background-color: #ffc107; color: black; }
    .status-flagged { background-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point."""

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        [
            "🏠 Home",
            "📊 Dashboard",
            "📈 Analytics",
            "🔍 GL Account Lookup",
            "📝 Reports",
            "🤖 AI Assistant",
            "⚙️ Settings"
        ]
    )

    # Route to appropriate page
    if page == "🏠 Home":
        render_home_page()
    elif page == "📊 Dashboard":
        render_dashboard_page()
    elif page == "📈 Analytics":
        render_analytics_page()
    elif page == "🔍 GL Account Lookup":
        render_lookup_page()
    elif page == "📝 Reports":
        render_reports_page()
    elif page == "🤖 AI Assistant":
        render_ai_assistant_page()
    elif page == "⚙️ Settings":
        render_settings_page()

def render_home_page():
    """Home page with overview and quick actions."""
    st.markdown('<div class="main-header">Project Aura 🌟</div>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Financial Statement Review Assistant")

    # Quick stats in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total GL Accounts", "501", "24 new")
    with col2:
        st.metric("Review Progress", "78%", "+12%")
    with col3:
        st.metric("Hygiene Score", "85/100", "+5")
    with col4:
        st.metric("SLA Compliance", "92%", "+3%")

    # File upload section
    st.markdown("---")
    st.subheader("📤 Upload Trial Balance")

    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=['csv'],
        help="Upload trial balance CSV with GL accounts"
    )

    if uploaded_file:
        # Process file
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        # Add ingestion logic here

def render_dashboard_page():
    """Interactive dashboard with multiple charts."""
    st.title("📊 Interactive Dashboard")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        entity = st.selectbox("Entity", ["ABEX", "AGEL", "APL"])
    with col2:
        period = st.selectbox("Period", ["2024-01", "2024-02", "2024-03"])
    with col3:
        view = st.selectbox("View", ["Overview", "By Department", "By Category"])

    # Display charts based on view
    # (Implementation in Part 1)

def render_analytics_page():
    """Advanced analytics and insights."""
    st.title("📈 Advanced Analytics")
    # (Implementation in Part 1)

def render_lookup_page():
    """GL account search and details."""
    st.title("🔍 GL Account Lookup")
    # (Implementation in Part 1)

def render_reports_page():
    """Generate and download reports."""
    st.title("📝 Automated Reports")
    # (Implementation in Part 1)

def render_ai_assistant_page():
    """Conversational AI interface."""
    st.title("🤖 AI Assistant")
    # (Implementation in Part 4)

def render_settings_page():
    """Application settings."""
    st.title("⚙️ Settings")
    # (Implementation later)

if __name__ == "__main__":
    main()
```

**Acceptance Criteria**:
- ✅ Multi-page app with 7 pages
- ✅ Professional styling with custom CSS
- ✅ Responsive layout (works on different screen sizes)
- ✅ Sidebar navigation functional
- ✅ File upload working end-to-end
- ✅ State management between pages (session_state)

---

### 0.2 Code Quality & Testing Gaps

#### **Gap 0.2.1: Missing Unit Tests** 🟡
**Current State**:
- ✅ 17 tests in `tests/test_assignment_engine.py`
- ✅ Tests in `tests/test_data_ingestion.py`
- ✅ Tests in `tests/test_data_validation.py`
- ❌ No tests for `analytics.py`
- ❌ No tests for `insights.py`
- ❌ No tests for `visualizations.py`
- ❌ No tests for Streamlit app components

**Required**:
```python
# tests/test_analytics.py - CREATE
def test_variance_analysis():
    """Test variance calculation correctness."""
    pass

def test_review_status_summary():
    """Test review status aggregations."""
    pass

def test_hygiene_score_calculation():
    """Test hygiene scoring algorithm."""
    pass

# tests/test_insights.py - CREATE
def test_proactive_insights_generation():
    """Test insight generation logic."""
    pass

def test_executive_summary():
    """Test summary report creation."""
    pass

# tests/test_visualizations.py - CREATE
def test_chart_generation():
    """Test all chart types render without errors."""
    pass

def test_chart_export():
    """Test PNG/HTML export."""
    pass
```

**Acceptance Criteria**:
- ✅ 3 new test files created
- ✅ ≥15 new unit tests added
- ✅ Test coverage ≥85% for analytics, insights, visualizations
- ✅ All tests pass in CI pipeline

---

#### **Gap 0.2.2: Documentation Gaps** 🟢
**Current State**:
- ✅ Comprehensive docs in `docs/` folder
- ✅ ADRs for major decisions
- ✅ Phase completion reports
- ❌ No API documentation for modules
- ❌ No user guide for Streamlit app
- ❌ No deployment guide

**Required**:
- Create `docs/guides/API-Reference.md` with function signatures
- Create `docs/guides/User-Guide.md` with screenshots
- Add docstrings to all public functions (Google style)

**Acceptance Criteria**:
- ✅ All public functions have docstrings
- ✅ API reference document created
- ✅ User guide with 10+ screenshots

---

## Part 1: Automated Report Generation Engine

**Duration**: 3-4 hours
**Priority**: 🔴 CRITICAL
**Goal**: Build comprehensive reporting system that generates professional reports on-demand

### 1.1 Report Types & Specifications

#### **Report 1.1.1: GL Account Status Report** 🔴
**Business Need**: Show which GL accounts are missing supporting documents and need attention.

**Specification**:
```yaml
Report Name: GL Account Status Report
Format: PDF + CSV
Sections:
  1. Executive Summary
     - Total GL accounts
     - Pending uploads count
     - Critical pending count
     - Overall completion %

  2. Pending Uploads Table
     Columns:
       - Account Code
       - Account Name
       - Balance (formatted with ₹)
       - Assigned To (Name)
       - Department
       - Due Date
       - Days Overdue (highlighted if >0)
       - Criticality (badge with color)
     Sorting: By Days Overdue DESC, then Criticality
     Filtering: Show only pending items

  3. Pending Reviews Table
     (Similar structure)

  4. Pending Approvals Table
     (Similar structure)

  5. Charts
     - Pie chart: Status distribution
     - Bar chart: Pending by department
     - Timeline: Overdue items

  6. Recommendations
     - Top 5 action items
     - Users with most pending items
     - Critical accounts requiring immediate attention

Footer: Generated timestamp, page numbers, Project Aura branding
```

**Implementation**:
```python
# src/reports/status_report.py - CREATE NEW FILE

from datetime import datetime
from typing import Dict, List
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

class GLAccountStatusReport:
    """Generate comprehensive GL account status report."""

    def __init__(self, entity: str, period: str):
        self.entity = entity
        self.period = period
        self.data = self._fetch_data()

    def _fetch_data(self) -> Dict:
        """Fetch all required data from analytics module."""
        from src.analytics import get_pending_items_report, calculate_review_status_summary

        return {
            'pending_items': get_pending_items_report(self.entity, self.period),
            'review_summary': calculate_review_status_summary(self.entity, self.period)
        }

    def generate_pdf(self, output_path: str) -> str:
        """
        Generate PDF report.

        Returns:
            Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("GL Account Status Report", title_style))
        story.append(Paragraph(f"Entity: {self.entity} | Period: {self.period}", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Section 1: Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        summary_data = self._create_summary_table()
        story.append(summary_data)
        story.append(Spacer(1, 0.2*inch))

        # Section 2: Pending Uploads
        if self.data['pending_items']['pending_uploads']:
            story.append(Paragraph("Pending Uploads (Supporting Documents Required)", styles['Heading2']))
            uploads_table = self._create_pending_table(self.data['pending_items']['pending_uploads'])
            story.append(uploads_table)
            story.append(Spacer(1, 0.2*inch))

        # Section 3: Pending Reviews
        if self.data['pending_items']['pending_reviews']:
            story.append(Paragraph("Pending Reviews", styles['Heading2']))
            reviews_table = self._create_pending_table(self.data['pending_items']['pending_reviews'])
            story.append(reviews_table)
            story.append(Spacer(1, 0.2*inch))

        # Section 4: Charts
        story.append(PageBreak())
        story.append(Paragraph("Visual Analysis", styles['Heading2']))

        # Pie chart
        pie_chart = self._create_status_pie_chart()
        story.append(pie_chart)
        story.append(Spacer(1, 0.2*inch))

        # Bar chart
        bar_chart = self._create_department_bar_chart()
        story.append(bar_chart)

        # Section 5: Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Recommendations", styles['Heading2']))
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

        # Build PDF
        doc.build(story)
        return output_path

    def _create_summary_table(self) -> Table:
        """Create executive summary statistics table."""
        summary = self.data['pending_items']['summary']

        data = [
            ['Metric', 'Count'],
            ['Total GL Accounts', str(summary.get('total_accounts', 0))],
            ['Pending Uploads', str(summary['total_pending_uploads'])],
            ['Pending Reviews', str(summary['total_pending_reviews'])],
            ['Pending Approvals', str(summary['total_pending_approvals'])],
            ['Critical Items Pending', str(summary['critical_pending'])],
            ['Overdue Items', str(summary['overdue_count'])]
        ]

        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        return table

    def _create_pending_table(self, items: List[Dict]) -> Table:
        """Create table of pending items."""
        # Header
        data = [['Account Code', 'Account Name', 'Balance', 'Assigned To', 'Due Date', 'Days Overdue', 'Criticality']]

        # Data rows
        for item in items[:20]:  # Limit to 20 items per page
            data.append([
                item['account_code'],
                item['account_name'][:30] + '...' if len(item['account_name']) > 30 else item['account_name'],
                f"₹{item['balance']:,.2f}",
                item['assigned_to'],
                item['due_date'].strftime('%Y-%m-%d') if isinstance(item['due_date'], datetime) else item['due_date'],
                str(item.get('days_overdue', 0)),
                item['criticality']
            ])

        table = Table(data, colWidths=[1*inch, 1.8*inch, 1.2*inch, 1.2*inch, 1*inch, 0.8*inch, 0.8*inch])

        # Styling
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]

        # Highlight overdue items
        for i, item in enumerate(items[:20], start=1):
            if item.get('days_overdue', 0) > 0:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ffcccc')))

        table.setStyle(TableStyle(style_commands))
        return table

    def _create_status_pie_chart(self) -> Drawing:
        """Create pie chart showing status distribution."""
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 100
        pie.height = 100

        summary = self.data['pending_items']['summary']
        pie.data = [
            summary['total_pending_uploads'],
            summary['total_pending_reviews'],
            summary['total_pending_approvals']
        ]
        pie.labels = ['Pending Uploads', 'Pending Reviews', 'Pending Approvals']
        pie.slices.strokeWidth = 0.5

        drawing.add(pie)
        return drawing

    def _create_department_bar_chart(self) -> Drawing:
        """Create bar chart showing pending by department."""
        # Aggregate by department
        dept_counts = {}
        for item in self.data['pending_items']['pending_uploads']:
            dept = item.get('department', 'Unknown')
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        drawing = Drawing(400, 200)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 300
        bc.data = [list(dept_counts.values())]
        bc.categoryAxis.categoryNames = list(dept_counts.keys())

        drawing.add(bc)
        return drawing

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        summary = self.data['pending_items']['summary']

        if summary['overdue_count'] > 0:
            recommendations.append(f"URGENT: {summary['overdue_count']} items are overdue. Immediate action required.")

        if summary['critical_pending'] > 0:
            recommendations.append(f"Focus on {summary['critical_pending']} critical accounts first.")

        if summary['total_pending_uploads'] > 20:
            recommendations.append(f"High volume of pending uploads ({summary['total_pending_uploads']}). Consider sending bulk reminder emails.")

        # Identify users with most pending
        user_workload = {}
        for item in self.data['pending_items']['pending_uploads']:
            user = item['assigned_to']
            user_workload[user] = user_workload.get(user, 0) + 1

        if user_workload:
            top_user = max(user_workload, key=user_workload.get)
            recommendations.append(f"Reviewer '{top_user}' has {user_workload[top_user]} pending items. Consider redistributing workload.")

        recommendations.append("Schedule daily standup to review progress on critical items.")

        return recommendations

    def generate_csv(self, output_path: str) -> str:
        """Generate CSV export of all pending items."""
        all_items = []

        # Combine all pending items
        for item_type in ['pending_uploads', 'pending_reviews', 'pending_approvals']:
            items = self.data['pending_items'].get(item_type, [])
            for item in items:
                item['type'] = item_type.replace('pending_', '')
                all_items.append(item)

        df = pd.DataFrame(all_items)
        df.to_csv(output_path, index=False)
        return output_path
```

**Acceptance Criteria**:
- ✅ PDF report generates with all 6 sections
- ✅ Professional formatting with colors, borders, headers/footers
- ✅ Charts render correctly in PDF
- ✅ CSV export includes all pending items
- ✅ Report generation completes in <5 seconds
- ✅ Handles empty data gracefully (shows "No pending items" message)

---

#### **Report 1.1.2: Variance Analysis Report** 🔴
**Business Need**: Identify and explain major changes in GL account balances period-over-period.

**Specification**:
```yaml
Report Name: Period-over-Period Variance Analysis
Format: PDF + Excel
Sections:
  1. Variance Summary
     - Total variance amount
     - Average variance %
     - Number of accounts with >10% variance
     - Number of accounts with >₹50k variance

  2. Top 10 Increases
     Table with: Account, Previous Balance, Current Balance, Change, Change%

  3. Top 10 Decreases
     (Similar structure)

  4. Variance by Category
     - Assets variance
     - Liabilities variance
     - Revenue variance
     - Expenses variance

  5. Charts
     - Waterfall chart showing major movements
     - Heatmap of variance across categories
     - Scatter plot: Balance vs Variance%

  6. Anomaly Alerts
     - List of accounts with unusual variance patterns
     - Statistical outliers (Z-score > 2)
     - Accounts requiring investigation

Excel Tabs:
  - Summary
  - All Variances (full detail table)
  - Increases
  - Decreases
  - Charts
```

**Implementation**:
```python
# src/reports/variance_report.py - CREATE NEW FILE

from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from typing import Dict, List

class VarianceAnalysisReport:
    """Generate period-over-period variance analysis report."""

    def __init__(self, entity: str, current_period: str, previous_period: str):
        self.entity = entity
        self.current_period = current_period
        self.previous_period = previous_period
        self.data = self._fetch_data()

    def _fetch_data(self) -> Dict:
        """Fetch variance analysis data."""
        from src.analytics import calculate_variance_analysis, identify_anomalies_ml

        return {
            'variance': calculate_variance_analysis(
                self.entity,
                self.current_period,
                self.previous_period
            ),
            'anomalies': identify_anomalies_ml(self.entity, self.current_period)
        }

    def generate_pdf(self, output_path: str) -> str:
        """Generate PDF variance report."""
        # Implementation similar to status report
        # Focus on variance tables and charts
        pass

    def generate_excel(self, output_path: str) -> str:
        """
        Generate comprehensive Excel workbook with multiple sheets.

        Sheets:
        1. Summary - Key metrics and charts
        2. All Variances - Complete variance table
        3. Top Increases - Top 20 increases
        4. Top Decreases - Top 20 decreases
        5. By Category - Category breakdown
        6. Anomalies - Statistical outliers
        """
        wb = Workbook()

        # Remove default sheet
        wb.remove(wb.active)

        # Sheet 1: Summary
        ws_summary = wb.create_sheet("Summary")
        self._populate_summary_sheet(ws_summary)

        # Sheet 2: All Variances
        ws_all = wb.create_sheet("All Variances")
        self._populate_all_variances_sheet(ws_all)

        # Sheet 3: Top Increases
        ws_increases = wb.create_sheet("Top Increases")
        self._populate_top_movements_sheet(ws_increases, 'increases')

        # Sheet 4: Top Decreases
        ws_decreases = wb.create_sheet("Top Decreases")
        self._populate_top_movements_sheet(ws_decreases, 'decreases')

        # Sheet 5: By Category
        ws_category = wb.create_sheet("By Category")
        self._populate_category_sheet(ws_category)

        # Sheet 6: Anomalies
        ws_anomalies = wb.create_sheet("Anomalies")
        self._populate_anomalies_sheet(ws_anomalies)

        # Save workbook
        wb.save(output_path)
        return output_path

    def _populate_summary_sheet(self, ws):
        """Populate summary sheet with key metrics."""
        # Title
        ws['A1'] = 'Variance Analysis Summary'
        ws['A1'].font = Font(size=16, bold=True, color='1F4E78')
        ws['A2'] = f'Entity: {self.entity}'
        ws['A3'] = f'Periods: {self.previous_period} → {self.current_period}'
        ws['A4'] = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

        # Key metrics starting at row 6
        metrics = [
            ['Metric', 'Value'],
            ['Total Accounts Analyzed', self.data['variance']['total_accounts']],
            ['Total Variance Amount', f"₹{self.data['variance']['variance_summary']['total_variance']:,.2f}"],
            ['Average Variance %', f"{self.data['variance']['variance_summary']['avg_variance_pct']:.2f}%"],
            ['Accounts with >10% Variance', len([v for v in self.data['variance']['major_variances'] if abs(v['variance_pct']) > 10])],
            ['Accounts with >₹50k Variance', len([v for v in self.data['variance']['major_variances'] if abs(v['variance_amount']) > 50000])]
        ]

        for row_idx, row_data in enumerate(metrics, start=6):
            for col_idx, cell_value in enumerate(row_data, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=cell_value)
                if row_idx == 6:  # Header row
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

        # Add chart (simplified - actual chart would use openpyxl.chart)
        ws['A15'] = 'Top 5 Increases:'
        ws['A15'].font = Font(bold=True)

        top_increases = sorted(
            self.data['variance']['major_variances'],
            key=lambda x: x['variance_amount'],
            reverse=True
        )[:5]

        for idx, item in enumerate(top_increases, start=16):
            ws[f'A{idx}'] = item['account_code']
            ws[f'B{idx}'] = item['account_name']
            ws[f'C{idx}'] = f"₹{item['variance_amount']:,.2f}"

        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

    def _populate_all_variances_sheet(self, ws):
        """Populate complete variance data table."""
        # Headers
        headers = [
            'Account Code',
            'Account Name',
            'Category',
            'Previous Balance',
            'Current Balance',
            'Variance Amount',
            'Variance %',
            'Flag'
        ]

        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.font = Font(bold=True, color='FFFFFF')

        # Data rows
        for row_idx, item in enumerate(self.data['variance']['major_variances'], start=2):
            ws.cell(row=row_idx, column=1, value=item['account_code'])
            ws.cell(row=row_idx, column=2, value=item['account_name'])
            ws.cell(row=row_idx, column=3, value=item.get('category', 'Unknown'))
            ws.cell(row=row_idx, column=4, value=item['previous_balance'])
            ws.cell(row=row_idx, column=5, value=item['current_balance'])
            ws.cell(row=row_idx, column=6, value=item['variance_amount'])
            ws.cell(row=row_idx, column=7, value=item['variance_pct'])
            ws.cell(row=row_idx, column=8, value=item['flag'])

            # Color code based on flag
            flag_cell = ws.cell(row=row_idx, column=8)
            if item['flag'] == 'increase':
                flag_cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
            else:
                flag_cell.fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

    def _populate_top_movements_sheet(self, ws, direction: str):
        """Populate top increases or decreases."""
        # Filter and sort based on direction
        if direction == 'increases':
            items = sorted(
                [v for v in self.data['variance']['major_variances'] if v['variance_amount'] > 0],
                key=lambda x: x['variance_amount'],
                reverse=True
            )[:20]
            title = 'Top 20 Increases'
        else:
            items = sorted(
                [v for v in self.data['variance']['major_variances'] if v['variance_amount'] < 0],
                key=lambda x: x['variance_amount']
            )[:20]
            title = 'Top 20 Decreases'

        ws['A1'] = title
        ws['A1'].font = Font(size=14, bold=True)

        # Headers
        headers = ['Rank', 'Account Code', 'Account Name', 'Previous', 'Current', 'Change', 'Change %']
        for col_idx, header in enumerate(headers, start=1):
            ws.cell(row=3, column=col_idx, value=header).font = Font(bold=True)

        # Data
        for rank, item in enumerate(items, start=1):
            row = rank + 3
            ws.cell(row=row, column=1, value=rank)
            ws.cell(row=row, column=2, value=item['account_code'])
            ws.cell(row=row, column=3, value=item['account_name'])
            ws.cell(row=row, column=4, value=f"₹{item['previous_balance']:,.2f}")
            ws.cell(row=row, column=5, value=f"₹{item['current_balance']:,.2f}")
            ws.cell(row=row, column=6, value=f"₹{item['variance_amount']:,.2f}")
            ws.cell(row=row, column=7, value=f"{item['variance_pct']:.2f}%")

    def _populate_category_sheet(self, ws):
        """Populate variance breakdown by category."""
        ws['A1'] = 'Variance by Category'
        ws['A1'].font = Font(size=14, bold=True)

        category_data = self.data['variance']['variance_by_category']

        # Headers
        headers = ['Category', 'Total Variance', 'Account Count', 'Average Variance']
        for col_idx, header in enumerate(headers, start=1):
            ws.cell(row=3, column=col_idx, value=header).font = Font(bold=True)

        # Data
        row = 4
        for category, metrics in category_data.items():
            ws.cell(row=row, column=1, value=category)
            ws.cell(row=row, column=2, value=f"₹{metrics['total_variance']:,.2f}")
            ws.cell(row=row, column=3, value=metrics['account_count'])
            avg = metrics['total_variance'] / metrics['account_count'] if metrics['account_count'] > 0 else 0
            ws.cell(row=row, column=4, value=f"₹{avg:,.2f}")
            row += 1

    def _populate_anomalies_sheet(self, ws):
        """Populate anomaly detection results."""
        ws['A1'] = 'Statistical Anomalies'
        ws['A1'].font = Font(size=14, bold=True)
        ws['A2'] = 'Accounts with unusual variance patterns requiring investigation'

        # Headers
        headers = ['Account Code', 'Account Name', 'Current Balance', 'Z-Score', 'Anomaly Score', 'Reason']
        for col_idx, header in enumerate(headers, start=1):
            ws.cell(row=4, column=col_idx, value=header).font = Font(bold=True)

        # Data
        anomalies = self.data['anomalies']['statistical_outliers']
        for row_idx, item in enumerate(anomalies, start=5):
            ws.cell(row=row_idx, column=1, value=item['account_code'])
            ws.cell(row=row_idx, column=2, value=item['account_name'])
            ws.cell(row=row_idx, column=3, value=f"₹{item['current_balance']:,.2f}")
            ws.cell(row=row_idx, column=4, value=f"{item['z_score']:.2f}")
            ws.cell(row=row_idx, column=5, value=f"{item['anomaly_score']:.2f}")
            ws.cell(row=row_idx, column=6, value=item['reason'])

            # Highlight high severity
            if item['anomaly_score'] > 0.8:
                for col in range(1, 7):
                    ws.cell(row=row_idx, column=col).fill = PatternFill(
                        start_color='FFC7CE', end_color='FFC7CE', fill_type='solid'
                    )
```

**Acceptance Criteria**:
- ✅ Excel workbook with 6 sheets generated
- ✅ All sheets properly formatted with headers, colors, fonts
- ✅ Charts embedded in Excel (at least 2 charts)
- ✅ PDF report with waterfall and heatmap charts
- ✅ Handles periods with no previous data gracefully
- ✅ Generation completes in <10 seconds

---
#### **Report 1.1.3: GL Hygiene Dashboard Report** 🔴
**Business Need**: Provide a consolidated quality & readiness view for leadership and reviewers; quantify health of the close process.

**Specification**:
```yaml
Report Name: GL Hygiene Dashboard Report
Format: PDF + PNG (dashboard snapshot) + JSON (raw metrics)
Sections:
  1. Hygiene Score Summary
     - Overall score (0-100) with grade (A-F)
     - Component breakdown (trial balance, documentation, review completion, SLA compliance, data quality, zero-balance handling)
     - Trend vs previous period

  2. Component Detail Tables
     Columns per component:
       - Component Name
       - Score / Max
       - Status (Good / Needs Attention / Critical)
       - Recommended Action

  3. Risk Indicators
     - Critical accounts missing docs
     - Accounts with failed validations
     - Accounts flagged for anomalies
     - SLA at-risk count

  4. Visuals
     - Gauge: Overall hygiene
     - Radar: Component scores comparison
     - Bar: Documentation completeness by department
     - Heatmap: Validation failure density by category

  5. Recommendations
     - Auto-generated from low-scoring components
     - Prioritized list with impact level

Footer: Generated timestamp, version metadata
```

**Implementation Skeleton**:
```python
# src/reports/hygiene_report.py
from typing import Dict, List
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

class GLHygieneDashboardReport:
    """Generate GL hygiene dashboard snapshot report."""
    def __init__(self, entity: str, period: str):
        self.entity = entity
        self.period = period
        self.hygiene = self._fetch_hygiene()
        self.risks = self._fetch_risks()

    def _fetch_hygiene(self) -> Dict:
        from src.analytics import calculate_gl_hygiene_score
        return calculate_gl_hygiene_score(self.entity, self.period)

    def _fetch_risks(self) -> Dict:
        from src.analytics import identify_anomalies_ml, get_pending_items_report
        pending = get_pending_items_report(self.entity, self.period)
        anomalies = identify_anomalies_ml(self.entity, self.period)
        return {
            'critical_missing_docs': [i for i in pending['pending_uploads'] if i['criticality'] == 'Critical'],
            'validation_failures': [],  # populated after adding custom expectations
            'anomalies': anomalies['statistical_outliers'],
            'sla_at_risk': [i for i in pending['pending_reviews'] if i.get('days_overdue', 0) < 1 and i.get('due_date')]
        }

    def generate_pdf(self, output_path: str) -> str:
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(output_path, pagesize=(8.27*inch, 11.69*inch), leftMargin=0.5*inch, rightMargin=0.5*inch)
        story = []
        story.append(Paragraph(f"GL Hygiene Dashboard - {self.entity} ({self.period})", styles['Title']))
        story.append(Paragraph(f"Generated: {datetime.utcnow().isoformat()}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        # Score summary table placeholder
        # Component breakdown table placeholder
        # Risk indicators placeholder
        # Recommendations placeholder
        doc.build(story)
        return output_path

    def export_json(self) -> Dict:
        return {'hygiene': self.hygiene, 'risks': self.risks}
```

**Acceptance Criteria**:
- ✅ Hygiene score matches component weighting logic
- ✅ PDF includes all 5 sections with tables & visuals placeholders integrated
- ✅ JSON export consumable by dashboard API
- ✅ Recommendations generated when any component <70% of max

---

#### **Report 1.1.4: Reviewer Performance Report** 🔴
**Business Need**: Show productivity, bottlenecks, SLA adherence, and workload distribution across reviewers to enable rebalancing and recognition.

**Specification**:
```yaml
Report Name: Reviewer Performance
Format: PDF + CSV
Sections:
  1. Overview Metrics
     - Total reviewers
     - Average completion rate
     - Average turnaround time (days)
     - Pending backlog

  2. Reviewer Table (sortable)
     Columns: Reviewer, Assigned, Completed, Pending, Avg Review Time (d), SLA Breaches, Critical Accounts, Completion %
     Highlight: Top performers (green), Bottlenecks (red)

  3. Visuals
     - Horizontal bar: Workload distribution
     - Scatter: Completion % vs Avg Review Time
     - Box plot: Review time distribution

  4. Bottleneck Analysis
     - Reviewers with > X pending
     - Reviewers holding ≥ N critical accounts

  5. Recommendations
     - Reassignment suggestions
     - Recognition candidates
```

**Implementation Skeleton**:
```python
# src/reports/reviewer_performance_report.py
from typing import List, Dict
from datetime import datetime
import pandas as pd

class ReviewerPerformanceReport:
    def __init__(self, entity: str, period: str):
        self.entity = entity
        self.period = period
        self.review_stats = self._fetch_review_stats()

    def _fetch_review_stats(self) -> List[Dict]:
        from src.analytics import calculate_review_status_summary
        summary = calculate_review_status_summary(self.entity, self.period)
        return summary['by_reviewer']

    def identify_bottlenecks(self) -> List[Dict]:
        return [r for r in self.review_stats if r['pending'] > 15 or r['completion_pct'] < 50]

    def generate_csv(self, path: str) -> str:
        pd.DataFrame(self.review_stats).to_csv(path, index=False)
        return path

    def generate_pdf(self, path: str) -> str:
        # Similar pattern to status report
        return path
```

**Acceptance Criteria**:
- ✅ Aggregated reviewer metrics derived from source tables
- ✅ Bottleneck detection flags ≥90% of synthetic edge cases in test
- ✅ CSV export includes all reviewer columns
- ✅ PDF highlights top/bottom quartile reviewers

---

#### **Report 1.1.5: SLA Compliance Report** 🔴
**Business Need**: Track adherence to deadlines and highlight at-risk or breached items for operational control.

**Specification**:
```yaml
Report Name: SLA Compliance
Format: PDF + Excel (multi-sheet)
Sheets:
  - Summary: Compliance %, On-Time, Delayed, At-Risk, Breaches Trend
  - Upcoming Deadlines: Items due in next 72h
  - Breaches: Overdue items with severity
  - Department SLA: Compliance by department
  - Critical SLA: Critical accounts SLA performance
Sections (PDF):
  1. Compliance Overview
  2. SLA Trend (last 6 periods)
  3. At-Risk Items Detail
  4. Breaches Root Cause Categorization
  5. Recommendations & Preventive Actions
```

**Implementation Skeleton**:
```python
# src/reports/sla_compliance_report.py
from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd

class SLAComplianceReport:
    def __init__(self, entity: str, period: str):
        self.entity = entity
        self.period = period
        self.data = self._fetch_sla_data()

    def _fetch_sla_data(self) -> Dict:
        from src.analytics import calculate_review_status_summary, get_pending_items_report
        review = calculate_review_status_summary(self.entity, self.period)
        pending = get_pending_items_report(self.entity, self.period)
        return {
            'overview': review['sla_compliance'],
            'pending_reviews': pending['pending_reviews'],
            'pending_uploads': pending['pending_uploads']
        }

    def classify_items(self) -> Dict[str, List[Dict]]:
        now = datetime.utcnow()
        upcoming, breaches, at_risk = [], [], []
        for item in self.data['pending_reviews']:
            due = item.get('due_date')
            if not due:
                continue
            if isinstance(due, str):
                continue  # parse if needed
            delta = (due - now).total_seconds() / 3600
            if delta < 0:
                breaches.append(item)
            elif delta <= 24:
                at_risk.append(item)
            elif delta <= 72:
                upcoming.append(item)
        return {'upcoming': upcoming, 'breaches': breaches, 'at_risk': at_risk}

    def generate_excel(self, path: str) -> str:
        wb = pd.ExcelWriter(path, engine='openpyxl')
        classes = self.classify_items()
        pd.DataFrame([self.data['overview']]).to_excel(wb, sheet_name='Summary', index=False)
        pd.DataFrame(classes['upcoming']).to_excel(wb, sheet_name='Upcoming Deadlines', index=False)
        pd.DataFrame(classes['breaches']).to_excel(wb, sheet_name='Breaches', index=False)
        pd.DataFrame(classes['at_risk']).to_excel(wb, sheet_name='At Risk', index=False)
        wb.close()
        return path
```

**Acceptance Criteria**:
- ✅ SLA classification logic handles missing due dates gracefully
- ✅ Excel workbook produced with ≥4 sheets populated
- ✅ At-risk threshold (<=24h) configurable via parameter later
- ✅ Breach recommendations include root-cause categories (to be enriched)

---

#### **Report 1.1.6: Executive Summary & Insights Report** 🔴
**Business Need**: Provide a one-pager for CFO / leadership highlighting performance, risks, and recommended actions.

**Specification**:
```yaml
Report Name: Executive Summary
Format: PDF + Markdown (for embedding) + PNG header visual
Sections:
  1. Key Metrics (cards): Accounts, Total Balance, Net Income, Hygiene Score, Completion %, SLA Compliance
  2. Highlights (top 5 positive developments)
  3. Concerns (top 5 issues)
  4. Risk Radar (visual summary of anomalies, SLA breaches, pending critical docs)
  5. Recommendations (prioritized, impact + effort tags)
  6. Trend Snapshot (mini line charts revenue/expense, completion%)
Footer: Prepared by Project Aura | Timestamp | Version
```

**Implementation Skeleton**:
```python
# src/reports/executive_summary_report.py
from datetime import datetime
from typing import Dict, List

class ExecutiveSummaryReport:
    def __init__(self, entity: str, period: str):
        self.entity = entity
        self.period = period
        self.summary = self._assemble()

    def _assemble(self) -> Dict:
        from src.insights import generate_executive_summary, generate_proactive_insights
        exec_summary = generate_executive_summary(self.entity, self.period)
        insights = generate_proactive_insights(self.entity, self.period)
        return { 'summary': exec_summary, 'insights': insights }

    def generate_markdown(self) -> str:
        s = self.summary['summary']
        md = [f"# Executive Summary - {self.entity} ({self.period})", f"Generated: {datetime.utcnow().isoformat()}\n"]
        md.append("## Key Metrics")
        for k,v in s['key_metrics'].items():
            md.append(f"- **{k.replace('_',' ').title()}**: {v}")
        md.append("\n## Highlights")
        md.extend([f"- {h}" for h in s['highlights']])
        md.append("\n## Concerns")
        md.extend([f"- {c}" for c in s['concerns']])
        md.append("\n## Recommendations")
        md.extend([f"- {r}" for r in s['recommendations']])
        return "\n".join(md)
```

**Acceptance Criteria**:
- ✅ Markdown output renders cleanly in Streamlit
- ✅ PDF fits on 1 page (A4) with readable font sizes
- ✅ Highlights & concerns auto-populated from insights logic
- ✅ Trend snapshot pulls last ≥3 periods when available

---

### 1.2 Report Orchestration & API Layer
Create a lightweight orchestrator to unify report generation for UI & agent tool usage.

```python
# src/reports/__init__.py
from typing import Literal
from .status_report import GLAccountStatusReport
from .variance_report import VarianceAnalysisReport
from .hygiene_report import GLHygieneDashboardReport
from .reviewer_performance_report import ReviewerPerformanceReport
from .sla_compliance_report import SLAComplianceReport
from .executive_summary_report import ExecutiveSummaryReport

REPORT_TYPES = {
    'status': GLAccountStatusReport,
    'variance': VarianceAnalysisReport,
    'hygiene': GLHygieneDashboardReport,
    'reviewer_performance': ReviewerPerformanceReport,
    'sla': SLAComplianceReport,
    'executive_summary': ExecutiveSummaryReport,
}

def generate_report(kind: Literal['status','variance','hygiene','reviewer_performance','sla','executive_summary'], **kwargs):
    cls = REPORT_TYPES[kind]
    return cls(**kwargs)
```

**Acceptance Criteria**:
- ✅ Unified factory function resolves all 6 report types
- ✅ Each report class returns at least one successful export in tests
- ✅ Error handling: Invalid kind raises ValueError with supported list

---

### 1.3 Testing Strategy (Reports)
**Planned Tests**:
- Unit: Component scoring, SLA classification, bottleneck detection
- Integration: End-to-end report PDF/Excel/CSV generation using sample seed data
- Performance: Each report <10s generation (variance may be heaviest)
- Resilience: Empty / minimal data sets produce graceful "No data" sections.

**Edge Cases**:
1. Previous period missing (variance report fallback)
2. No critical accounts (status + hygiene recommendations adapt)
3. All reviewers completed (performance report shows zero backlog)
4. All items overdue (SLA report severity coloring)
5. Missing component data (hygiene component scored 0 with recommendation)

---

## Part 1 Status Summary
Coverage: 6/6 report types specified (2 with deep code skeletons, 4 with structured skeletons). Orchestration + testing approach defined.

---

## Part 2: Interactive Visualization & Dashboard System

**Duration**: 4-5 hours
**Priority**: 🔴 CRITICAL
**Goal**: Build production-ready interactive dashboards with drill-down capability and real-time updates

### 2.1 Dashboard Architecture & Navigation

#### **2.1.1 Multi-Page Dashboard Structure** 🔴
**Design Philosophy**: Modular, tab-based navigation with persistent filters and state management.

**Page Structure**:
```yaml
Dashboard Pages:
  1. Overview Dashboard (Home)
     - KPI cards (4-6 metrics)
     - Status summary charts
     - Quick actions panel
     - Recent activity feed

  2. Financial Analysis Dashboard
     - Balance composition (Assets/Liabilities/Revenue/Expenses)
     - Variance waterfall chart
     - Trend lines (6-12 periods)
     - Category drill-down

  3. Review Progress Dashboard
     - Review status sunburst
     - Reviewer workload bars
     - SLA compliance gauge
     - Department comparison radar

  4. Quality & Hygiene Dashboard
     - GL hygiene gauge (main)
     - Component breakdown bars
     - Validation results table
     - Anomaly scatter plot

  5. Risk & Compliance Dashboard
     - SLA timeline Gantt
     - Critical pending items table
     - Anomaly heatmap
     - Risk indicators panel

Global Features:
  - Filter bar: Entity, Period, Department, Category
  - Refresh button with timestamp
  - Export dashboard snapshot (PNG/PDF)
  - Full-screen mode toggle
```

**Implementation**:
```python
# src/dashboards/__init__.py - CREATE NEW MODULE
from typing import Literal
import streamlit as st

def render_dashboard(page: Literal['overview', 'financial', 'review', 'quality', 'risk']):
    """Route to appropriate dashboard page."""
    if page == 'overview':
        from .overview_dashboard import render_overview_dashboard
        render_overview_dashboard()
    elif page == 'financial':
        from .financial_dashboard import render_financial_dashboard
        render_financial_dashboard()
    elif page == 'review':
        from .review_progress_dashboard import render_review_progress_dashboard
        render_review_progress_dashboard()
    elif page == 'quality':
        from .quality_hygiene_dashboard import render_quality_hygiene_dashboard
        render_quality_hygiene_dashboard()
    elif page == 'risk':
        from .risk_compliance_dashboard import render_risk_compliance_dashboard
        render_risk_compliance_dashboard()

def apply_global_filters() -> dict:
    """Render global filter bar and return selections."""
    st.sidebar.header("🔍 Filters")

    # Entity filter
    entity = st.sidebar.selectbox(
        "Entity",
        options=["All", "ABEX", "AGEL", "APL"],
        index=0
    )

    # Period filter
    period = st.sidebar.selectbox(
        "Period",
        options=["2024-03", "2024-02", "2024-01", "2023-12"],
        index=0
    )

    # Department filter
    department = st.sidebar.multiselect(
        "Department",
        options=["All", "Finance", "Treasury", "Operations", "Sales"],
        default=["All"]
    )

    # Category filter
    category = st.sidebar.multiselect(
        "Category",
        options=["All", "Assets", "Liabilities", "Revenue", "Expenses"],
        default=["All"]
    )

    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    return {
        'entity': entity,
        'period': period,
        'department': department,
        'category': category
    }
```

**Acceptance Criteria**:
- ✅ 5 dashboard pages with distinct layouts
- ✅ Global filter bar persists selections across page navigation
- ✅ Refresh button clears cache and reloads data
- ✅ Navigation responsive (loads page in <2s)

---

#### **2.1.2 Overview Dashboard Implementation** 🔴
**Purpose**: Executive summary view with key metrics and quick insights.

**Layout Specification**:
```yaml
Layout:
  Row 1: KPI Cards (4 columns)
    - Total GL Accounts (with delta vs previous period)
    - Overall Hygiene Score (with grade badge)
    - Review Completion % (with progress bar)
    - SLA Compliance % (with status icon)

  Row 2: Two-Column Split
    Left: Status Distribution Pie Chart
    Right: Department Performance Bar Chart

  Row 3: Three-Column Split
    Col 1: Pending Uploads Count (with list preview)
    Col 2: Pending Reviews Count (with list preview)
    Col 3: Critical Items Count (with alert icon)

  Row 4: Full-Width
    Recent Activity Timeline (last 10 actions)

  Row 5: Two-Column Split
    Left: Top 5 Proactive Insights (cards)
    Right: Quick Actions Panel (buttons)
```

**Implementation**:
```python
# src/dashboards/overview_dashboard.py - CREATE
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

def render_overview_dashboard():
    """Render main overview dashboard."""
    st.title("📊 Overview Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Get filters
    from . import apply_global_filters
    filters = apply_global_filters()

    # Fetch data
    data = fetch_overview_data(filters['entity'], filters['period'])

    # Row 1: KPI Cards
    render_kpi_cards(data['kpis'])

    st.markdown("---")

    # Row 2: Charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            create_status_distribution_chart(data['status']),
            use_container_width=True
        )
    with col2:
        st.plotly_chart(
            create_department_performance_chart(data['department_stats']),
            use_container_width=True
        )

    st.markdown("---")

    # Row 3: Pending Items Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        render_pending_card("Uploads", data['pending']['uploads'])
    with col2:
        render_pending_card("Reviews", data['pending']['reviews'])
    with col3:
        render_critical_card(data['pending']['critical'])

    st.markdown("---")

    # Row 4: Recent Activity
    st.subheader("📋 Recent Activity")
    render_activity_timeline(data['recent_activity'])

    st.markdown("---")

    # Row 5: Insights & Actions
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("💡 Proactive Insights")
        render_insights_cards(data['insights'])
    with col2:
        st.subheader("⚡ Quick Actions")
        render_quick_actions()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_overview_data(entity: str, period: str) -> dict:
    """Fetch all data needed for overview dashboard."""
    from src.analytics import (
        calculate_gl_hygiene_score,
        calculate_review_status_summary,
        get_pending_items_report
    )
    from src.insights import generate_proactive_insights

    return {
        'kpis': {
            'total_accounts': 501,
            'hygiene_score': calculate_gl_hygiene_score(entity, period),
            'review_completion': calculate_review_status_summary(entity, period)['overall']['completion_pct'],
            'sla_compliance': calculate_review_status_summary(entity, period)['sla_compliance']['compliance_pct']
        },
        'status': calculate_review_status_summary(entity, period)['overall'],
        'department_stats': calculate_review_status_summary(entity, period)['by_department'],
        'pending': get_pending_items_report(entity, period),
        'insights': generate_proactive_insights(entity, period),
        'recent_activity': []  # Placeholder - would query audit_trail
    }

def render_kpi_cards(kpis: dict):
    """Render top-row KPI metric cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total GL Accounts",
            value=f"{kpis['total_accounts']:,}",
            delta="24 new",
            delta_color="normal"
        )

    with col2:
        hygiene = kpis['hygiene_score']
        grade = hygiene['grade']
        grade_colors = {'A': '🟢', 'B': '🔵', 'C': '🟡', 'D': '🟠', 'F': '🔴'}
        st.metric(
            label="GL Hygiene Score",
            value=f"{hygiene['overall_score']:.0f}/100 {grade_colors.get(grade, '')}",
            delta=f"{hygiene['trend']['change']:+.0f}" if 'trend' in hygiene else None
        )

    with col3:
        completion = kpis['review_completion']
        st.metric(
            label="Review Completion",
            value=f"{completion:.1f}%",
            delta="+12%" if completion > 75 else None,
            delta_color="normal" if completion > 75 else "inverse"
        )

    with col4:
        sla = kpis['sla_compliance']
        st.metric(
            label="SLA Compliance",
            value=f"{sla:.1f}%",
            delta="+3%" if sla > 90 else None,
            delta_color="normal" if sla > 90 else "inverse"
        )

def create_status_distribution_chart(status_data: dict) -> go.Figure:
    """Create pie chart for review status distribution."""
    fig = go.Figure(data=[go.Pie(
        labels=['Reviewed', 'Pending', 'Flagged'],
        values=[
            status_data.get('reviewed', 0),
            status_data.get('pending', 0),
            status_data.get('flagged', 0)
        ],
        marker=dict(colors=['#28a745', '#ffc107', '#dc3545']),
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title="Review Status Distribution",
        showlegend=True,
        height=350
    )

    return fig

def create_department_performance_chart(dept_stats: dict) -> go.Figure:
    """Create horizontal bar chart for department completion rates."""
    departments = list(dept_stats.keys())
    completion_rates = [
        (dept_stats[d]['reviewed'] / dept_stats[d]['total'] * 100) if dept_stats[d]['total'] > 0 else 0
        for d in departments
    ]

    fig = go.Figure(data=[go.Bar(
        y=departments,
        x=completion_rates,
        orientation='h',
        marker=dict(
            color=completion_rates,
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Completion %")
        ),
        text=[f"{rate:.1f}%" for rate in completion_rates],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Completion: %{x:.1f}%<extra></extra>'
    )])

    fig.update_layout(
        title="Department Performance",
        xaxis_title="Completion %",
        yaxis_title="Department",
        height=350,
        xaxis=dict(range=[0, 110])
    )

    return fig

def render_pending_card(title: str, items: list):
    """Render pending items card with count and preview."""
    count = len(items)
    st.metric(label=f"Pending {title}", value=count)

    if count > 0:
        with st.expander(f"View top 5 {title.lower()}"):
            for i, item in enumerate(items[:5], 1):
                st.text(f"{i}. {item['account_code']} - {item['account_name'][:30]}")

def render_critical_card(critical_items: int):
    """Render critical items alert card."""
    st.metric(
        label="Critical Items",
        value=critical_items,
        delta="Requires Attention" if critical_items > 0 else "All Clear",
        delta_color="inverse" if critical_items > 0 else "normal"
    )
    if critical_items > 0:
        st.warning(f"⚠️ {critical_items} critical accounts need immediate attention!")

def render_activity_timeline(activities: list):
    """Render recent activity timeline."""
    if not activities:
        st.info("No recent activity to display.")
        return

    for activity in activities[:10]:
        st.text(f"• {activity['timestamp']} - {activity['user']}: {activity['action']}")

def render_insights_cards(insights: list):
    """Render proactive insight cards."""
    if not insights:
        st.success("✅ No critical insights at this time.")
        return

    for insight in insights[:5]:
        icon = {'critical': '🔴', 'warning': '⚠️', 'info': 'ℹ️'}.get(insight['type'], 'ℹ️')
        with st.container():
            st.markdown(f"**{icon} {insight['title']}**")
            st.caption(insight['description'])
            st.caption(f"Priority: {insight['priority']} | Action: {insight['recommended_action']}")
            st.markdown("---")

def render_quick_actions():
    """Render quick action buttons."""
    if st.button("📥 Upload Trial Balance", use_container_width=True):
        st.switch_page("pages/upload.py")  # Placeholder

    if st.button("📝 Generate Report", use_container_width=True):
        st.switch_page("pages/reports.py")  # Placeholder

    if st.button("🔍 Search GL Accounts", use_container_width=True):
        st.switch_page("pages/lookup.py")  # Placeholder

    if st.button("🤖 Ask AI Assistant", use_container_width=True):
        st.switch_page("pages/assistant.py")  # Placeholder
```

**Acceptance Criteria**:
- ✅ Overview dashboard renders all 5 rows without errors
- ✅ KPI cards show live data from analytics functions
- ✅ Charts interactive with hover tooltips
- ✅ Pending cards expandable with item previews
- ✅ Insights rendered with priority-based ordering
- ✅ Dashboard loads in <3 seconds with cached data

---

#### **2.1.3 Financial Analysis Dashboard** 🔴
**Purpose**: Deep-dive into financial balances, variances, and trends.

**Layout Specification**:
```yaml
Layout:
  Row 1: Summary Cards (3 columns)
    - Total Balance
    - Net Income
    - Major Variance Amount

  Row 2: Full-Width
    Variance Waterfall Chart (period-over-period)

  Row 3: Two-Column Split
    Left: Category Breakdown Pie Chart (Assets/Liabilities/Revenue/Expenses)
    Right: Top 10 Accounts by Balance (Bar Chart)

  Row 4: Full-Width
    Multi-Period Trend Lines (6-12 periods)

  Row 5: Interactive Data Table
    All GL accounts with filters, sorting, drill-down links
```

**Implementation Skeleton**:
```python
# src/dashboards/financial_dashboard.py - CREATE
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_financial_dashboard():
    st.title("💰 Financial Analysis Dashboard")

    from . import apply_global_filters
    filters = apply_global_filters()

    data = fetch_financial_data(filters['entity'], filters['period'])

    # Row 1: Financial Summary Cards
    render_financial_summary_cards(data['summary'])

    st.markdown("---")

    # Row 2: Variance Waterfall
    st.subheader("Period-over-Period Variance")
    st.plotly_chart(
        create_variance_waterfall(data['variance']),
        use_container_width=True
    )

    st.markdown("---")

    # Row 3: Category & Top Accounts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            create_category_breakdown_pie(data['category_breakdown']),
            use_container_width=True
        )
    with col2:
        st.plotly_chart(
            create_top_accounts_bar(data['top_accounts']),
            use_container_width=True
        )

    st.markdown("---")

    # Row 4: Trend Lines
    st.subheader("Multi-Period Trends")
    st.plotly_chart(
        create_trend_chart(data['trends']),
        use_container_width=True
    )

    st.markdown("---")

    # Row 5: Interactive Table
    st.subheader("GL Account Details")
    render_gl_accounts_table(data['gl_accounts'])

@st.cache_data(ttl=300)
def fetch_financial_data(entity: str, period: str) -> dict:
    from src.analytics import perform_analytics, calculate_variance_analysis
    from src.insights import compare_multi_period

    # Get current period analytics
    current = perform_analytics(entity, period)

    # Calculate variance (mock previous period for now)
    prev_period = "2024-02" if period == "2024-03" else "2024-01"
    variance = calculate_variance_analysis(entity, period, prev_period)

    # Get multi-period trends
    periods = ["2024-01", "2024-02", "2024-03"]
    trends = compare_multi_period(entity, periods) if periods else {}

    return {
        'summary': {
            'total_balance': current['total_balance'],
            'net_income': 0,  # Would calculate from revenue - expenses
            'variance_amount': variance['variance_summary']['total_variance']
        },
        'variance': variance,
        'category_breakdown': {},  # Would aggregate by category
        'top_accounts': [],  # Would query top 10 by absolute balance
        'trends': trends,
        'gl_accounts': []  # Would query all accounts with filters
    }

def render_financial_summary_cards(summary: dict):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Balance", f"₹{summary['total_balance']:,.2f}")
    with col2:
        st.metric("Net Income", f"₹{summary['net_income']:,.2f}", delta="+12%")
    with col3:
        st.metric("Total Variance", f"₹{summary['variance_amount']:,.2f}", delta="-5%")

def create_variance_waterfall(variance_data: dict) -> go.Figure:
    """Create waterfall chart showing major variances."""
    from src.visualizations import create_variance_waterfall_chart
    import pandas as pd

    # Convert variance data to DataFrame
    variances = variance_data.get('major_variances', [])
    if not variances:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No variance data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    df = pd.DataFrame(variances)
    return create_variance_waterfall_chart(df)

def create_category_breakdown_pie(category_data: dict) -> go.Figure:
    """Create pie chart for category distribution."""
    from src.visualizations import create_category_breakdown_pie
    return create_category_breakdown_pie(category_data)

def create_top_accounts_bar(accounts: list) -> go.Figure:
    """Create bar chart of top accounts by balance."""
    if not accounts:
        fig = go.Figure()
        fig.add_annotation(text="No account data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    fig = go.Figure(data=[go.Bar(
        y=[acc['account_name'][:20] for acc in accounts],
        x=[abs(acc['balance']) for acc in accounts],
        orientation='h',
        marker=dict(color='#1f77b4')
    )])
    fig.update_layout(title="Top 10 Accounts by Balance", xaxis_title="Balance (₹)", yaxis_title="Account")
    return fig

def create_trend_chart(trends: dict) -> go.Figure:
    """Create multi-line trend chart."""
    from src.visualizations import create_trend_line_chart
    return create_trend_line_chart(
        trends.get('trend_data', {}),
        trends.get('periods', []),
        title="Financial Trends (6 Periods)"
    )

def render_gl_accounts_table(accounts: list):
    """Render interactive GL accounts table with sorting and filtering."""
    import pandas as pd

    if not accounts:
        st.info("No GL account data available for selected filters.")
        return

    df = pd.DataFrame(accounts)

    # Add search box
    search = st.text_input("🔍 Search accounts", placeholder="Enter account code or name")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # Display table with formatting
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "balance": st.column_config.NumberColumn("Balance", format="₹%.2f"),
            "account_code": st.column_config.TextColumn("Account Code", width="small"),
            "account_name": st.column_config.TextColumn("Account Name", width="large")
        }
    )
```

**Acceptance Criteria**:
- ✅ Financial dashboard displays all financial metrics correctly
- ✅ Waterfall chart shows top variances with proper colors (red/green)
- ✅ Category pie chart with percentages and hover details
- ✅ Trend chart shows multi-period data with range selector
- ✅ GL accounts table searchable and sortable
- ✅ Drill-down from charts to table (click → filter table)

---

### 2.2 Advanced Chart Implementations

#### **2.2.1 Complete Visualization Module Enhancement** 🔴
**Required Charts** (from Part 0 Gap 0.1.3):

```python
# src/visualizations.py - COMPLETE ALL 13 CHART FUNCTIONS

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List

def create_variance_waterfall_chart(variance_df: pd.DataFrame) -> go.Figure:
    """
    Waterfall chart showing period-over-period changes.

    Args:
        variance_df: DataFrame with columns ['account_name', 'variance_amount', 'category']
    """
    # Sort by variance amount
    df = variance_df.sort_values('variance_amount', ascending=False).head(15)

    # Prepare data
    accounts = df['account_name'].tolist()
    amounts = df['variance_amount'].tolist()

    # Calculate cumulative for waterfall
    cumulative = [0]
    for amt in amounts[:-1]:
        cumulative.append(cumulative[-1] + amt)

    fig = go.Figure(go.Waterfall(
        name="Variance",
        orientation="v",
        measure=["relative"] * (len(amounts) - 1) + ["total"],
        x=accounts,
        textposition="outside",
        text=[f"₹{amt:,.0f}" for amt in amounts],
        y=amounts,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#dc3545"}},
        increasing={"marker": {"color": "#28a745"}},
        totals={"marker": {"color": "#1f77b4"}}
    ))

    fig.update_layout(
        title="Top 15 Account Variances (Period-over-Period)",
        xaxis_title="GL Account",
        yaxis_title="Variance Amount (₹)",
        showlegend=False,
        height=500,
        hovermode="x unified"
    )

    return fig

def create_hygiene_gauge(hygiene_score: float, components: dict) -> go.Figure:
    """
    Gauge chart showing GL hygiene score 0-100.

    Color bands:
    - 0-60: Red (Poor)
    - 60-75: Orange (Fair)
    - 75-85: Yellow (Good)
    - 85-95: Light Green (Very Good)
    - 95-100: Dark Green (Excellent)
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=hygiene_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "GL Hygiene Score", 'font': {'size': 24}},
        delta={'reference': components.get('trend', {}).get('previous_score', hygiene_score)},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': '#dc3545'},
                {'range': [60, 75], 'color': '#fd7e14'},
                {'range': [75, 85], 'color': '#ffc107'},
                {'range': [85, 95], 'color': '#90ee90'},
                {'range': [95, 100], 'color': '#28a745'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=80, b=20)
    )

    return fig

def create_review_status_sunburst(status_data: dict) -> go.Figure:
    """
    Sunburst chart showing review status hierarchy.

    Levels:
    1. Overall status (Reviewed, Pending, Flagged)
    2. By department
    3. By criticality
    """
    labels = []
    parents = []
    values = []
    colors = []

    # Level 1: Overall status
    for status in ['Reviewed', 'Pending', 'Flagged']:
        labels.append(status)
        parents.append("")
        values.append(status_data['overall'].get(status.lower(), 0))
        colors.append({'Reviewed': '#28a745', 'Pending': '#ffc107', 'Flagged': '#dc3545'}[status])

    # Level 2: By department (under each status)
    for dept, dept_data in status_data.get('by_department', {}).items():
        for status in ['reviewed', 'pending']:
            if dept_data.get(status, 0) > 0:
                labels.append(f"{dept} - {status.title()}")
                parents.append(status.title())
                values.append(dept_data[status])
                colors.append({'reviewed': '#28a745', 'pending': '#ffc107'}[status])

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(colors=colors),
        branchvalues="total",
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percentParent}<extra></extra>'
    ))

    fig.update_layout(
        title="Review Status Distribution (Hierarchical)",
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig

def create_sla_timeline_gantt(assignments: list[dict]) -> go.Figure:
    """
    Gantt chart showing assignment timelines vs SLA deadlines.

    Shows:
    - Assignment date
    - Current status
    - Due date
    - Completion date (if done)
    - Overdue items in red
    """
    df_gantt = []

    for assignment in assignments[:20]:  # Limit to 20 for readability
        # Determine color based on status
        if assignment.get('days_overdue', 0) > 0:
            color = '#dc3545'  # Red for overdue
        elif assignment.get('completed', False):
            color = '#28a745'  # Green for completed
        else:
            color = '#ffc107'  # Yellow for in-progress

        df_gantt.append(dict(
            Task=f"{assignment['account_code']}",
            Start=assignment.get('assigned_date', '2024-03-01'),
            Finish=assignment.get('due_date', '2024-03-15'),
            Resource=assignment.get('assigned_to', 'Unknown'),
            Color=color
        ))

    fig = px.timeline(
        df_gantt,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Resource",
        title="Assignment Timeline & SLA Compliance",
        hover_data=["Resource"]
    )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=600, xaxis_title="Timeline", yaxis_title="GL Account")

    return fig

def create_variance_heatmap(
    variance_data: pd.DataFrame,  # Rows=accounts, Cols=periods
    title: str = "GL Account Variance Heatmap"
) -> go.Figure:
    """
    Heatmap showing variance patterns across accounts and time.

    Color scale: Red (negative) → White (no change) → Green (positive)
    """
    fig = go.Figure(data=go.Heatmap(
        z=variance_data.values,
        x=variance_data.columns,
        y=variance_data.index,
        colorscale=[
            [0, '#dc3545'],      # Red
            [0.5, '#ffffff'],    # White
            [1, '#28a745']       # Green
        ],
        zmid=0,
        text=variance_data.values,
        texttemplate='%{text:.1f}%',
        textfont={"size": 10},
        hovertemplate='Account: %{y}<br>Period: %{x}<br>Variance: %{z:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title="GL Account",
        height=600
    )

    return fig

def create_department_comparison_radar(dept_metrics: dict) -> go.Figure:
    """
    Radar chart comparing departments on multiple metrics.

    Metrics:
    - Completion rate
    - SLA compliance
    - Documentation quality
    - Average review time
    - Issue count
    """
    fig = go.Figure()

    categories = ['Completion Rate', 'SLA Compliance', 'Documentation Quality', 'Avg Review Time', 'Issue Count']

    for dept, metrics in dept_metrics.items():
        fig.add_trace(go.Scatterpolar(
            r=[
                metrics.get('completion_rate', 0),
                metrics.get('sla_compliance', 0),
                metrics.get('documentation_quality', 0),
                100 - metrics.get('avg_review_time', 0),  # Invert so faster is better
                100 - metrics.get('issue_count', 0)  # Invert so fewer issues is better
            ],
            theta=categories,
            fill='toself',
            name=dept
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Department Performance Comparison",
        height=500
    )

    return fig

def create_trend_line_chart(
    trend_data: dict,  # Keys=metric_name, Values=list of values
    periods: list[str],
    title: str = "Trend Analysis"
) -> go.Figure:
    """
    Multi-line chart showing trends over time.

    Supports:
    - Multiple metrics on same chart
    - Hover tooltips with details
    - Range selector
    - Export buttons
    """
    fig = go.Figure()

    for metric_name, values in trend_data.items():
        fig.add_trace(go.Scatter(
            x=periods,
            y=values,
            mode='lines+markers',
            name=metric_name.replace('_', ' ').title(),
            hovertemplate='%{y:.2f}<extra></extra>'
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title="Value",
        hovermode="x unified",
        height=450,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            rangeslider=dict(visible=True),
            type="category"
        )
    )

    return fig

def create_category_breakdown_pie(category_data: dict) -> go.Figure:
    """
    Pie chart with pull-out effect for major categories.

    Shows distribution by:
    - Account category (Assets, Liabilities, Revenue, Expenses)
    - With percentage labels
    - Click to drill down
    """
    if not category_data:
        category_data = {'Assets': 100, 'Liabilities': 80, 'Revenue': 50, 'Expenses': 40}  # Sample

    fig = go.Figure(data=[go.Pie(
        labels=list(category_data.keys()),
        values=list(category_data.values()),
        pull=[0.1 if v == max(category_data.values()) else 0 for v in category_data.values()],  # Pull out largest
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Balance: ₹%{value:,.2f}<br>Percent: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title="Balance by Category",
        showlegend=True,
        height=400
    )

    return fig

def create_reviewer_workload_bar(reviewer_stats: list[dict]) -> go.Figure:
    """
    Horizontal bar chart showing reviewer workload.

    Bars:
    - Assigned (total)
    - Completed (stacked)
    - Pending (stacked)
    - Color-coded by urgency
    """
    reviewers = [r['name'] for r in reviewer_stats]
    completed = [r['completed'] for r in reviewer_stats]
    pending = [r['pending'] for r in reviewer_stats]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Completed',
        y=reviewers,
        x=completed,
        orientation='h',
        marker=dict(color='#28a745')
    ))
    fig.add_trace(go.Bar(
        name='Pending',
        y=reviewers,
        x=pending,
        orientation='h',
        marker=dict(color='#ffc107')
    ))

    fig.update_layout(
        title="Reviewer Workload Distribution",
        xaxis_title="Number of Accounts",
        yaxis_title="Reviewer",
        barmode='stack',
        height=max(400, len(reviewers) * 40),
        hovermode='y unified'
    )

    return fig

def create_anomaly_scatter(anomaly_data: list[dict]) -> go.Figure:
    """
    Scatter plot showing anomalies by balance vs z-score.

    Features:
    - Size = balance magnitude
    - Color = severity
    - Hover = account details
    """
    if not anomaly_data:
        return go.Figure().add_annotation(
            text="No anomalies detected",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )

    balances = [abs(a['current_balance']) for a in anomaly_data]
    z_scores = [a['z_score'] for a in anomaly_data]
    severities = [a['anomaly_score'] for a in anomaly_data]
    labels = [f"{a['account_code']}: {a['account_name'][:20]}" for a in anomaly_data]

    fig = go.Figure(data=go.Scatter(
        x=balances,
        y=z_scores,
        mode='markers',
        marker=dict(
            size=[s * 30 for s in severities],  # Scale for visibility
            color=severities,
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Severity"),
            line=dict(width=1, color='black')
        ),
        text=labels,
        hovertemplate='<b>%{text}</b><br>Balance: ₹%{x:,.2f}<br>Z-Score: %{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title="Anomaly Detection Scatter Plot",
        xaxis_title="Balance (₹)",
        yaxis_title="Z-Score",
        xaxis_type="log",
        height=500
    )

    return fig

def export_chart_to_png(fig: go.Figure, output_path: str, width: int = 1200, height: int = 800):
    """Export Plotly chart to static PNG image."""
    fig.write_image(output_path, width=width, height=height)
    return output_path

def export_chart_to_html(fig: go.Figure, output_path: str):
    """Export interactive Plotly chart to standalone HTML."""
    fig.write_html(output_path, include_plotlyjs='cdn')
    return output_path

def create_dashboard_layout(charts: list[go.Figure], layout: str = 'grid') -> go.Figure:
    """
    Combine multiple charts into dashboard layout.

    Layouts:
    - 'grid': 2x2 or 3x2 grid
    - 'vertical': Stack vertically
    - 'tabs': Separate tabs (requires Streamlit wrapper)
    """
    if layout == 'vertical':
        # Stack charts vertically using subplots
        fig = make_subplots(
            rows=len(charts), cols=1,
            subplot_titles=[c.layout.title.text for c in charts if hasattr(c.layout, 'title')]
        )
        for i, chart in enumerate(charts, 1):
            for trace in chart.data:
                fig.add_trace(trace, row=i, col=1)
        fig.update_layout(height=400 * len(charts), showlegend=True)
        return fig

    elif layout == 'grid':
        # Create 2x2 grid
        rows = (len(charts) + 1) // 2
        fig = make_subplots(
            rows=rows, cols=2,
            subplot_titles=[c.layout.title.text if hasattr(c.layout.title, 'text') else f"Chart {i+1}" for i, c in enumerate(charts)]
        )
        for i, chart in enumerate(charts):
            row = (i // 2) + 1
            col = (i % 2) + 1
            for trace in chart.data:
                fig.add_trace(trace, row=row, col=col)
        fig.update_layout(height=400 * rows, showlegend=True)
        return fig

    else:
        raise ValueError(f"Unknown layout: {layout}. Use 'grid' or 'vertical'.")
```

**Acceptance Criteria**:
- ✅ All 13 chart functions implemented and tested
- ✅ Each chart renders with professional styling (colors, fonts, legends)
- ✅ Hover tooltips provide detailed information
- ✅ Export functions tested for PNG and HTML
- ✅ Charts render in <2 seconds for 501 records
- ✅ Dashboard layout function combines multiple charts correctly

---

### 2.3 Testing & Performance Strategy

**Unit Tests**:
```python
# tests/test_dashboards.py - CREATE
def test_overview_dashboard_data_fetch():
    """Test overview dashboard data fetching."""
    pass

def test_financial_dashboard_rendering():
    """Test financial dashboard components."""
    pass

# tests/test_visualizations.py - EXPAND
def test_all_chart_types():
    """Test each chart type generates valid Plotly figure."""
    pass

def test_chart_export_png():
    """Test PNG export functionality."""
    pass

def test_chart_export_html():
    """Test HTML export functionality."""
    pass
```

**Performance Benchmarks**:
- Dashboard page load: <3 seconds
- Chart render time: <2 seconds each
- Data fetch with cache: <500ms
- Export to PNG: <5 seconds
- Full dashboard snapshot: <10 seconds

---

## Part 2 Status Summary
Coverage: Complete dashboard architecture with 5 pages, 13 chart types fully implemented, orchestration layer, and testing strategy defined.

---

## Part 3: ML Learning Loop & Predictive Intelligence

**Duration**: 4-5 hours
**Priority**: 🟠 HIGH - Key differentiator for "AI-powered" claim
**Goal**: Build production-ready ML pipeline with continual learning from user feedback

### 3.1 Feature Engineering Pipeline

#### **3.1.1 GL Account Feature Extraction** 🔴
**Purpose**: Transform raw GL data into ML-ready feature vectors for anomaly detection, risk prediction, and review prioritization.

**Feature Categories**:
```yaml
Feature Groups:
  1. Balance Features (5 features)
     - current_balance_abs: Absolute balance value
     - balance_normalized: Min-max normalized (0-1)
     - balance_log: Log-transformed balance
     - balance_sign: Binary (1=debit, -1=credit)
     - balance_magnitude_category: Categorical (tiny/small/medium/large/huge)

  2. Temporal Features (6 features)
     - days_since_last_review: Days elapsed
     - review_frequency: Reviews per period (rolling 6 periods)
     - variance_last_3_periods: Std dev of last 3 balances
     - trend_slope: Linear regression slope over last 6 periods
     - seasonality_index: Deviation from historical monthly average
     - period_numeric: Encoded period (2024-01 → 202401)

  3. Categorical Features (8 features - one-hot encoded)
     - account_category: Assets/Liabilities/Revenue/Expenses
     - department: Finance/Treasury/Operations/Sales
     - criticality: Critical/High/Medium/Low
     - review_status: Reviewed/Pending/Flagged
     - has_supporting_docs: Binary
     - assigned_reviewer: Encoded reviewer ID
     - entity: ABEX/AGEL/APL
     - zero_balance_flag: Binary

  4. Risk Features (7 features)
     - variance_pct_previous: % change from previous period
     - z_score: Statistical outlier score
     - days_to_sla_deadline: Remaining days (negative if overdue)
     - critical_missing_docs: Binary
     - historical_issue_count: Count of past validation failures
     - reviewer_workload: Assigned items for current reviewer
     - complexity_score: Computed from balance volatility + category

  5. Derived Features (4 features)
     - balance_to_category_avg: Ratio to category average
     - balance_to_entity_total: Ratio to entity total balance
     - review_velocity: Days per review (historical avg)
     - risk_composite: Weighted sum of risk indicators

Total: 30 features
```

**Implementation**:
```python
# src/ml/feature_engineering.py - CREATE NEW FILE

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sqlalchemy.orm import Session

class GLFeatureEngineer:
    """Extract and engineer features from GL account data for ML models."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []

    def extract_features(self, session: Session, entity: str, period: str) -> pd.DataFrame:
        """
        Extract all feature groups for GL accounts.

        Args:
            session: Database session
            entity: Entity code (e.g., 'ABEX')
            period: Period code (e.g., '2024-03')

        Returns:
            DataFrame with rows=accounts, columns=features
        """
        # Fetch GL accounts
        from src.db.postgres import get_gl_accounts_by_entity_period
        accounts = get_gl_accounts_by_entity_period(session, entity, period)

        if not accounts:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame([self._account_to_dict(acc) for acc in accounts])

        # Extract each feature group
        df = self._add_balance_features(df)
        df = self._add_temporal_features(df, session, entity)
        df = self._add_categorical_features(df)
        df = self._add_risk_features(df, session, entity, period)
        df = self._add_derived_features(df)

        # Store feature names
        self.feature_names = [col for col in df.columns if col not in ['account_code', 'account_name', 'id']]

        return df

    def _account_to_dict(self, account) -> Dict:
        """Convert SQLAlchemy GL account object to dict."""
        return {
            'id': account.id,
            'account_code': account.account_code,
            'account_name': account.account_name,
            'balance': account.balance,
            'category': account.category,
            'department': account.department,
            'criticality': account.criticality,
            'review_status': account.review_status,
            'entity': account.entity,
            'period': account.period,
            'created_at': account.created_at
        }

    def _add_balance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add balance-related features."""
        df['current_balance_abs'] = df['balance'].abs()
        df['balance_normalized'] = (df['current_balance_abs'] - df['current_balance_abs'].min()) / \
                                    (df['current_balance_abs'].max() - df['current_balance_abs'].min() + 1e-10)
        df['balance_log'] = np.log1p(df['current_balance_abs'])  # log(1 + x) to handle zeros
        df['balance_sign'] = np.where(df['balance'] >= 0, 1, -1)

        # Categorize magnitude
        percentiles = df['current_balance_abs'].quantile([0.2, 0.4, 0.6, 0.8])
        df['balance_magnitude_category'] = pd.cut(
            df['current_balance_abs'],
            bins=[0, percentiles[0.2], percentiles[0.4], percentiles[0.6], percentiles[0.8], float('inf')],
            labels=['tiny', 'small', 'medium', 'large', 'huge']
        )

        return df

    def _add_temporal_features(self, df: pd.DataFrame, session: Session, entity: str) -> pd.DataFrame:
        """Add time-based features using historical data."""
        from src.db.postgres import get_account_history

        # For each account, fetch historical data
        for idx, row in df.iterrows():
            history = get_account_history(session, row['account_code'], entity, periods=6)

            if history:
                # Days since last review (mock - would query review_log)
                df.at[idx, 'days_since_last_review'] = 15  # Placeholder

                # Review frequency
                df.at[idx, 'review_frequency'] = len(history) / 6.0

                # Variance over last 3 periods
                if len(history) >= 3:
                    recent_balances = [h.balance for h in history[-3:]]
                    df.at[idx, 'variance_last_3_periods'] = np.std(recent_balances)
                else:
                    df.at[idx, 'variance_last_3_periods'] = 0

                # Trend slope
                if len(history) >= 2:
                    periods_numeric = list(range(len(history)))
                    balances = [h.balance for h in history]
                    slope = np.polyfit(periods_numeric, balances, 1)[0]
                    df.at[idx, 'trend_slope'] = slope
                else:
                    df.at[idx, 'trend_slope'] = 0

                # Seasonality index (deviation from average)
                if len(history) >= 6:
                    avg_balance = np.mean([h.balance for h in history])
                    df.at[idx, 'seasonality_index'] = (row['balance'] - avg_balance) / (avg_balance + 1e-10)
                else:
                    df.at[idx, 'seasonality_index'] = 0
            else:
                # No history - fill with defaults
                df.at[idx, 'days_since_last_review'] = 30
                df.at[idx, 'review_frequency'] = 0
                df.at[idx, 'variance_last_3_periods'] = 0
                df.at[idx, 'trend_slope'] = 0
                df.at[idx, 'seasonality_index'] = 0

        # Period numeric
        df['period_numeric'] = df['period'].str.replace('-', '').astype(int)

        return df

    def _add_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add and encode categorical features."""
        categorical_cols = ['category', 'department', 'criticality', 'review_status', 'entity']

        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
            else:
                df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))

        # Binary features
        df['has_supporting_docs'] = 0  # Would query supporting_docs collection
        df['zero_balance_flag'] = (df['balance'] == 0).astype(int)

        return df

    def _add_risk_features(self, df: pd.DataFrame, session: Session, entity: str, period: str) -> pd.DataFrame:
        """Add risk-related features."""
        from src.analytics import calculate_variance_analysis

        # Variance % from previous period
        prev_period = self._get_previous_period(period)
        try:
            variance_data = calculate_variance_analysis(entity, period, prev_period)
            variance_map = {v['account_code']: v['variance_pct'] for v in variance_data['major_variances']}
            df['variance_pct_previous'] = df['account_code'].map(variance_map).fillna(0)
        except:
            df['variance_pct_previous'] = 0

        # Z-score (outlier detection)
        df['z_score'] = (df['current_balance_abs'] - df['current_balance_abs'].mean()) / \
                        (df['current_balance_abs'].std() + 1e-10)

        # Days to SLA deadline (mock - would query responsibility_matrix)
        df['days_to_sla_deadline'] = 10  # Placeholder

        # Critical missing docs
        df['critical_missing_docs'] = ((df['criticality'] == 'Critical') &
                                        (df['has_supporting_docs'] == 0)).astype(int)

        # Historical issue count (mock - would query validation_results)
        df['historical_issue_count'] = 0  # Placeholder

        # Reviewer workload (mock - would query responsibility_matrix)
        df['reviewer_workload'] = 20  # Placeholder

        # Complexity score
        df['complexity_score'] = (
            df['variance_last_3_periods'] * 0.4 +
            df['current_balance_abs'] / df['current_balance_abs'].max() * 0.3 +
            (df['category_encoded'] / 4.0) * 0.3  # Normalized category
        )

        return df

    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features from combinations."""
        # Balance to category average
        category_avg = df.groupby('category')['current_balance_abs'].transform('mean')
        df['balance_to_category_avg'] = df['current_balance_abs'] / (category_avg + 1e-10)

        # Balance to entity total
        entity_total = df['current_balance_abs'].sum()
        df['balance_to_entity_total'] = df['current_balance_abs'] / (entity_total + 1e-10)

        # Review velocity (mock)
        df['review_velocity'] = 5.0  # Placeholder - would calculate from review_log

        # Risk composite score
        df['risk_composite'] = (
            df['z_score'].abs() * 0.25 +
            df['variance_pct_previous'].abs() * 0.2 +
            df['critical_missing_docs'] * 0.15 +
            df['complexity_score'] * 0.2 +
            (df['days_to_sla_deadline'] < 0).astype(int) * 0.2  # Overdue
        )

        return df

    def _get_previous_period(self, period: str) -> str:
        """Calculate previous period (e.g., '2024-03' → '2024-02')."""
        year, month = period.split('-')
        month_int = int(month)
        if month_int == 1:
            return f"{int(year)-1}-12"
        else:
            return f"{year}-{month_int-1:02d}"

    def get_feature_matrix(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract feature matrix for ML model input.

        Returns:
            NumPy array with shape (n_samples, n_features)
        """
        # Select only numeric feature columns
        feature_cols = [col for col in self.feature_names if col in df.columns]
        X = df[feature_cols].select_dtypes(include=[np.number]).fillna(0).values

        return X

    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit scaler and transform features.

        Returns:
            Tuple of (X_scaled, y) where y is target (e.g., risk_composite)
        """
        X = self.get_feature_matrix(df)
        y = df['risk_composite'].values if 'risk_composite' in df.columns else np.zeros(len(df))

        X_scaled = self.scaler.fit_transform(X)

        return X_scaled, y

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform features using fitted scaler."""
        X = self.get_feature_matrix(df)
        X_scaled = self.scaler.transform(X)
        return X_scaled
```

**Acceptance Criteria**:
- ✅ Feature engineer extracts all 30 features without errors
- ✅ Handles missing historical data gracefully (fills with defaults)
- ✅ Feature matrix shape: (n_accounts, 30)
- ✅ All features normalized to [0, 1] or standardized
- ✅ Feature extraction completes in <5 seconds for 501 accounts

---

#### **3.1.2 Target Variable Definition** 🔴
**Purpose**: Define supervised learning targets for model training.

**Target Options**:
```yaml
Target Variables:
  1. Anomaly Score (regression)
     - Continuous 0-1 score
     - Computed from: z_score + variance_pct + complexity_score
     - Use case: Anomaly detection ranking

  2. Review Priority (classification)
     - Classes: Critical / High / Medium / Low
     - Derived from: criticality + days_to_deadline + balance_magnitude
     - Use case: Assignment prioritization

  3. Requires Attention (binary classification)
     - Classes: 0 (OK) / 1 (Needs Attention)
     - Derived from: validation_failures + missing_docs + overdue
     - Use case: Alert generation

  4. Time to Review (regression)
     - Continuous (days)
     - Historical average review time per account
     - Use case: SLA prediction
```

**Implementation**:
```python
# src/ml/target_engineering.py - CREATE

import pandas as pd
import numpy as np

def create_anomaly_target(df: pd.DataFrame) -> np.ndarray:
    """
    Create anomaly score target (0-1).

    Composite of:
    - Z-score magnitude (normalized)
    - Variance % (normalized)
    - Complexity score
    """
    z_norm = (df['z_score'].abs() - df['z_score'].abs().min()) / \
             (df['z_score'].abs().max() - df['z_score'].abs().min() + 1e-10)

    var_norm = (df['variance_pct_previous'].abs() - df['variance_pct_previous'].abs().min()) / \
               (df['variance_pct_previous'].abs().max() - df['variance_pct_previous'].abs().min() + 1e-10)

    anomaly_score = (z_norm * 0.4 + var_norm * 0.3 + df['complexity_score'] * 0.3)

    return anomaly_score.values

def create_priority_target(df: pd.DataFrame) -> np.ndarray:
    """
    Create review priority classification target.

    Mapping:
    - Critical: 3
    - High: 2
    - Medium: 1
    - Low: 0
    """
    priority_map = {'Critical': 3, 'High': 2, 'Medium': 1, 'Low': 0}
    return df['criticality'].map(priority_map).fillna(0).values

def create_attention_target(df: pd.DataFrame) -> np.ndarray:
    """
    Create binary 'requires attention' target.

    Conditions:
    - Has validation failures
    - Missing supporting docs (critical accounts)
    - Overdue for review
    """
    needs_attention = (
        (df['historical_issue_count'] > 0) |
        (df['critical_missing_docs'] == 1) |
        (df['days_to_sla_deadline'] < 0)
    ).astype(int)

    return needs_attention.values

def create_time_to_review_target(df: pd.DataFrame) -> np.ndarray:
    """
    Create time-to-review regression target.

    Uses historical review velocity or defaults to 5 days.
    """
    return df['review_velocity'].fillna(5.0).values
```

---

### 3.2 Model Training & Experiment Tracking

#### **3.2.1 Baseline Model Implementation** 🔴
**Purpose**: Train production-ready ML models for anomaly detection and prioritization.

**Model Selection**:
```yaml
Models to Train:
  1. Anomaly Detection (Regression)
     Primary: Isolation Forest (unsupervised)
     Secondary: Random Forest Regressor (supervised)
     Metrics: Precision@K, Recall@K, F1-Score

  2. Priority Classification (Multi-class)
     Primary: Gradient Boosting Classifier
     Secondary: Random Forest Classifier
     Metrics: Accuracy, Precision, Recall, F1 (weighted)

  3. Attention Detection (Binary)
     Primary: XGBoost Classifier
     Secondary: Logistic Regression
     Metrics: ROC-AUC, Precision-Recall AUC

  4. Time Prediction (Regression)
     Primary: Random Forest Regressor
     Secondary: Linear Regression with polynomial features
     Metrics: MAE, RMSE, R²
```

**Implementation**:
```python
# src/ml/models.py - EXPAND EXISTING FILE

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_recall_fscore_support, roc_auc_score,
    classification_report
)
import xgboost as xgb
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any
import joblib
from pathlib import Path

class MLModelTrainer:
    """Train and manage ML models for GL account intelligence."""

    def __init__(self, experiment_name: str = "gl-account-ml"):
        mlflow.set_experiment(experiment_name)
        self.models = {}
        self.metrics = {}

    def train_anomaly_detector(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train anomaly detection model.

        Args:
            X: Feature matrix
            y: Anomaly scores (continuous 0-1)
            test_size: Train/test split ratio

        Returns:
            Dict with model and metrics
        """
        with mlflow.start_run(run_name="anomaly_detection"):
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Train Isolation Forest (unsupervised)
            iso_forest = IsolationForest(
                n_estimators=100,
                contamination=0.1,
                random_state=42,
                n_jobs=-1
            )
            iso_forest.fit(X_train)

            # Get anomaly scores
            anomaly_scores = -iso_forest.score_samples(X_test)  # Negative = more anomalous

            # Train Random Forest Regressor (supervised)
            rf_model = RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            rf_model.fit(X_train, y_train)
            y_pred = rf_model.predict(X_test)

            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)

            # Log parameters
            mlflow.log_params({
                'model_type': 'RandomForestRegressor',
                'n_estimators': 200,
                'max_depth': 10,
                'test_size': test_size
            })

            # Log metrics
            mlflow.log_metrics({
                'mae': mae,
                'rmse': rmse,
                'r2_score': r2
            })

            # Log model
            mlflow.sklearn.log_model(rf_model, "anomaly_model")

            # Store
            self.models['anomaly_detector'] = rf_model
            self.metrics['anomaly_detector'] = {
                'mae': mae, 'rmse': rmse, 'r2': r2
            }

            return {
                'model': rf_model,
                'metrics': self.metrics['anomaly_detector'],
                'feature_importance': dict(zip(
                    [f'feature_{i}' for i in range(X.shape[1])],
                    rf_model.feature_importances_
                ))
            }

    def train_priority_classifier(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train review priority classifier.

        Args:
            X: Feature matrix
            y: Priority labels (0=Low, 1=Medium, 2=High, 3=Critical)

        Returns:
            Dict with model and metrics
        """
        with mlflow.start_run(run_name="priority_classification"):
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )

            # Train Gradient Boosting Classifier
            gb_model = GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            gb_model.fit(X_train, y_train)
            y_pred = gb_model.predict(X_test)

            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_test, y_pred, average='weighted'
            )

            # Classification report
            report = classification_report(y_test, y_pred, output_dict=True)

            # Log parameters
            mlflow.log_params({
                'model_type': 'GradientBoostingClassifier',
                'n_estimators': 150,
                'learning_rate': 0.1,
                'max_depth': 5
            })

            # Log metrics
            mlflow.log_metrics({
                'accuracy': accuracy,
                'precision_weighted': precision,
                'recall_weighted': recall,
                'f1_weighted': f1
            })

            # Log model
            mlflow.sklearn.log_model(gb_model, "priority_model")

            # Store
            self.models['priority_classifier'] = gb_model
            self.metrics['priority_classifier'] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'report': report
            }

            return {
                'model': gb_model,
                'metrics': self.metrics['priority_classifier']
            }

    def train_attention_classifier(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train binary 'requires attention' classifier.

        Args:
            X: Feature matrix
            y: Binary labels (0=OK, 1=Needs Attention)

        Returns:
            Dict with model and metrics
        """
        with mlflow.start_run(run_name="attention_classification"):
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )

            # Train XGBoost Classifier
            xgb_model = xgb.XGBClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
            xgb_model.fit(X_train, y_train)
            y_pred = xgb_model.predict(X_test)
            y_proba = xgb_model.predict_proba(X_test)[:, 1]

            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, y_proba)
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_test, y_pred, average='binary'
            )

            # Log parameters
            mlflow.log_params({
                'model_type': 'XGBClassifier',
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 6
            })

            # Log metrics
            mlflow.log_metrics({
                'accuracy': accuracy,
                'roc_auc': roc_auc,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            })

            # Log model
            mlflow.sklearn.log_model(xgb_model, "attention_model")

            # Store
            self.models['attention_classifier'] = xgb_model
            self.metrics['attention_classifier'] = {
                'accuracy': accuracy,
                'roc_auc': roc_auc,
                'precision': precision,
                'recall': recall,
                'f1': f1
            }

            return {
                'model': xgb_model,
                'metrics': self.metrics['attention_classifier']
            }

    def hyperparameter_tuning(
        self,
        model_type: str,
        X: np.ndarray,
        y: np.ndarray,
        param_grid: Dict
    ) -> Any:
        """
        Perform grid search for hyperparameter tuning.

        Args:
            model_type: 'anomaly', 'priority', or 'attention'
            X: Feature matrix
            y: Target variable
            param_grid: Hyperparameter grid

        Returns:
            Best estimator
        """
        base_models = {
            'anomaly': RandomForestRegressor(random_state=42),
            'priority': GradientBoostingClassifier(random_state=42),
            'attention': xgb.XGBClassifier(random_state=42, use_label_encoder=False)
        }

        grid_search = GridSearchCV(
            base_models[model_type],
            param_grid,
            cv=5,
            scoring='neg_mean_absolute_error' if model_type == 'anomaly' else 'accuracy',
            n_jobs=-1,
            verbose=1
        )

        grid_search.fit(X, y)

        mlflow.log_params(grid_search.best_params_)
        mlflow.log_metric('best_score', grid_search.best_score_)

        return grid_search.best_estimator_

    def save_models(self, output_dir: str = "models/"):
        """Save all trained models to disk."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        for name, model in self.models.items():
            model_path = output_path / f"{name}.joblib"
            joblib.dump(model, model_path)
            print(f"Saved {name} to {model_path}")

    def load_models(self, model_dir: str = "models/"):
        """Load trained models from disk."""
        model_path = Path(model_dir)

        for model_file in model_path.glob("*.joblib"):
            name = model_file.stem
            self.models[name] = joblib.load(model_file)
            print(f"Loaded {name} from {model_file}")
```

**Acceptance Criteria**:
- ✅ All 3 models train successfully on sample data
- ✅ MLflow experiments logged with parameters, metrics, artifacts
- ✅ Anomaly detector achieves R² > 0.6
- ✅ Priority classifier achieves accuracy > 75%
- ✅ Attention classifier achieves ROC-AUC > 0.80
- ✅ Models saved to disk and loadable

---

### 3.3 User Feedback Collection & Continual Learning

#### **3.3.1 Feedback Collection UI** 🔴
**Purpose**: Enable users to provide feedback on ML predictions for model improvement.

**Feedback Types**:
```yaml
Feedback Mechanisms:
  1. Anomaly Flag Correction
     - User marks false positive: "This is not an anomaly"
     - User marks false negative: "This should be flagged"

  2. Priority Adjustment
     - User changes: "Actually this is High priority, not Medium"

  3. Review Time Feedback
     - Actual review time recorded automatically
     - User can report if estimate was inaccurate

  4. General Feedback
     - Thumbs up/down on ML suggestions
     - Free-text comments
```

**Implementation**:
```python
# src/ml/feedback_handler.py - EXPAND EXISTING

from datetime import datetime
from typing import Dict, Optional
from bson import ObjectId

class MLFeedbackCollector:
    """Collect and store user feedback on ML predictions."""

    def __init__(self):
        from src.db.mongodb import get_mongo_database
        self.db = get_mongo_database()
        self.collection = self.db['ml_feedback']

    def record_anomaly_feedback(
        self,
        account_code: str,
        predicted_anomaly: bool,
        user_correction: bool,
        user_email: str,
        comments: Optional[str] = None
    ) -> str:
        """
        Record user feedback on anomaly detection.

        Args:
            account_code: GL account code
            predicted_anomaly: What model predicted (True/False)
            user_correction: User's correction (True/False)
            user_email: User providing feedback
            comments: Optional comments

        Returns:
            Feedback ID
        """
        feedback = {
            'feedback_type': 'anomaly_detection',
            'account_code': account_code,
            'predicted_value': predicted_anomaly,
            'corrected_value': user_correction,
            'is_correction': predicted_anomaly != user_correction,
            'user_email': user_email,
            'comments': comments,
            'created_at': datetime.utcnow(),
            'used_for_retraining': False
        }

        result = self.collection.insert_one(feedback)
        return str(result.inserted_id)

    def record_priority_feedback(
        self,
        account_code: str,
        predicted_priority: str,
        corrected_priority: str,
        user_email: str
    ) -> str:
        """Record feedback on priority classification."""
        feedback = {
            'feedback_type': 'priority_classification',
            'account_code': account_code,
            'predicted_value': predicted_priority,
            'corrected_value': corrected_priority,
            'is_correction': predicted_priority != corrected_priority,
            'user_email': user_email,
            'created_at': datetime.utcnow(),
            'used_for_retraining': False
        }

        result = self.collection.insert_one(feedback)
        return str(result.inserted_id)

    def record_review_time_actual(
        self,
        account_code: str,
        predicted_days: float,
        actual_days: float,
        user_email: str
    ) -> str:
        """Record actual review time vs predicted."""
        feedback = {
            'feedback_type': 'review_time_prediction',
            'account_code': account_code,
            'predicted_value': predicted_days,
            'actual_value': actual_days,
            'error': abs(predicted_days - actual_days),
            'user_email': user_email,
            'created_at': datetime.utcnow(),
            'used_for_retraining': False
        }

        result = self.collection.insert_one(feedback)
        return str(result.inserted_id)

    def get_feedback_for_retraining(self, feedback_type: Optional[str] = None) -> list:
        """
        Retrieve feedback that hasn't been used for retraining yet.

        Args:
            feedback_type: Filter by type (optional)

        Returns:
            List of feedback documents
        """
        query = {'used_for_retraining': False}
        if feedback_type:
            query['feedback_type'] = feedback_type

        return list(self.collection.find(query))

    def mark_feedback_used(self, feedback_ids: list):
        """Mark feedback as used for retraining."""
        self.collection.update_many(
            {'_id': {'$in': [ObjectId(fid) for fid in feedback_ids]}},
            {'$set': {'used_for_retraining': True, 'used_at': datetime.utcnow()}}
        )

    def get_feedback_stats(self) -> Dict:
        """Get statistics on collected feedback."""
        pipeline = [
            {
                '$group': {
                    '_id': '$feedback_type',
                    'total_count': {'$sum': 1},
                    'corrections': {'$sum': {'$cond': ['$is_correction', 1, 0]}},
                    'unused': {'$sum': {'$cond': [{'$eq': ['$used_for_retraining', False]}, 1, 0]}}
                }
            }
        ]

        results = list(self.collection.aggregate(pipeline))

        return {
            r['_id']: {
                'total': r['total_count'],
                'corrections': r['corrections'],
                'unused': r['unused'],
                'correction_rate': r['corrections'] / r['total_count'] if r['total_count'] > 0 else 0
            }
            for r in results
        }
```

**Streamlit Feedback UI**:
```python
# src/dashboards/ml_feedback_panel.py - CREATE

import streamlit as st
from src.ml.feedback_handler import MLFeedbackCollector

def render_feedback_panel(account_code: str, predictions: dict):
    """
    Render feedback collection panel for ML predictions.

    Args:
        account_code: GL account code
        predictions: Dict with model predictions
    """
    st.subheader("🤖 ML Predictions & Feedback")

    collector = MLFeedbackCollector()

    # Anomaly feedback
    if 'anomaly_score' in predictions:
        st.markdown("**Anomaly Detection**")
        col1, col2 = st.columns([3, 1])
        with col1:
            is_anomaly = predictions['anomaly_score'] > 0.7
            st.info(f"Predicted: {'⚠️ Anomaly' if is_anomaly else '✅ Normal'} (score: {predictions['anomaly_score']:.2f})")
        with col2:
            if st.button("Report Incorrect"):
                user_correction = not is_anomaly
                collector.record_anomaly_feedback(
                    account_code,
                    is_anomaly,
                    user_correction,
                    st.session_state.get('user_email', 'unknown@example.com')
                )
                st.success("Feedback recorded!")

    # Priority feedback
    if 'predicted_priority' in predictions:
        st.markdown("**Priority Classification**")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"Predicted Priority: {predictions['predicted_priority']}")
        with col2:
            corrected = st.selectbox(
                "Correct Priority",
                ['', 'Low', 'Medium', 'High', 'Critical'],
                key=f'priority_{account_code}'
            )
            if corrected and corrected != predictions['predicted_priority']:
                if st.button("Submit Correction"):
                    collector.record_priority_feedback(
                        account_code,
                        predictions['predicted_priority'],
                        corrected,
                        st.session_state.get('user_email', 'unknown@example.com')
                    )
                    st.success("Priority correction recorded!")

    # Review time feedback
    if 'predicted_review_days' in predictions:
        st.markdown("**Review Time Estimate**")
        st.info(f"Estimated review time: {predictions['predicted_review_days']:.1f} days")
```

**Acceptance Criteria**:
- ✅ Feedback UI integrated into dashboard
- ✅ All feedback types stored in MongoDB
- ✅ Feedback retrieval functions tested
- ✅ Stats dashboard shows feedback counts and correction rates

---

#### **3.3.2 Continual Learning Pipeline** 🔴
**Purpose**: Automatically retrain models with accumulated feedback to improve over time.

**Retraining Strategy**:
```yaml
Retraining Triggers:
  - Scheduled: Weekly (every Sunday 2AM)
  - Threshold-based: ≥50 new feedback items collected
  - Manual: Admin-triggered retraining

Safety Rails:
  - New model must outperform baseline by ≥2% on validation set
  - Rollback mechanism if performance degrades
  - A/B testing with 10% traffic to new model first
  - Human review before full deployment

Versioning:
  - Models versioned: v1.0, v1.1, v1.2, etc.
  - Metadata: training_date, feedback_count, metrics
  - Stored in MLflow Model Registry
```

**Implementation**:
```python
# src/ml/continual_learning.py - CREATE

import mlflow
import mlflow.sklearn
from datetime import datetime
from typing import Dict, Optional
import numpy as np
from sklearn.model_selection import train_test_split

class ContinualLearningPipeline:
    """Orchestrate continual learning with feedback integration."""

    def __init__(self):
        from src.ml.feature_engineering import GLFeatureEngineer
        from src.ml.models import MLModelTrainer
        from src.ml.feedback_handler import MLFeedbackCollector

        self.feature_engineer = GLFeatureEngineer()
        self.trainer = MLModelTrainer()
        self.feedback_collector = MLFeedbackCollector()
        self.baseline_metrics = {}

    def should_retrain(self) -> Dict[str, bool]:
        """
        Check if retraining criteria are met.

        Returns:
            Dict with retraining decisions per model type
        """
        stats = self.feedback_collector.get_feedback_stats()

        decisions = {}
        threshold = 50  # Minimum feedback items

        for feedback_type in ['anomaly_detection', 'priority_classification', 'review_time_prediction']:
            unused_count = stats.get(feedback_type, {}).get('unused', 0)
            decisions[feedback_type] = unused_count >= threshold

        return decisions

    def retrain_with_feedback(
        self,
        model_type: str,
        session,
        entity: str,
        period: str
    ) -> Dict:
        """
        Retrain model incorporating user feedback.

        Args:
            model_type: 'anomaly_detection', 'priority_classification', or 'review_time_prediction'
            session: Database session
            entity: Entity code
            period: Period code

        Returns:
            Dict with retraining results
        """
        # Fetch new feedback
        feedback_items = self.feedback_collector.get_feedback_for_retraining(model_type)

        if not feedback_items:
            return {'status': 'skipped', 'reason': 'No new feedback'}

        # Extract features for all accounts
        df = self.feature_engineer.extract_features(session, entity, period)
        X, _ = self.feature_engineer.fit_transform(df)

        # Augment training data with feedback corrections
        feedback_accounts = [f['account_code'] for f in feedback_items]
        feedback_corrections = {f['account_code']: f['corrected_value'] for f in feedback_items}

        # Map feedback to dataset
        df['feedback_correction'] = df['account_code'].map(feedback_corrections)

        # Create augmented target
        if model_type == 'anomaly_detection':
            from src.ml.target_engineering import create_anomaly_target
            y_base = create_anomaly_target(df)
            # Blend base target with feedback (70% base, 30% feedback)
            y = np.where(df['feedback_correction'].notna(),
                        df['feedback_correction'] * 0.3 + y_base * 0.7,
                        y_base)
        elif model_type == 'priority_classification':
            from src.ml.target_engineering import create_priority_target
            y = create_priority_target(df)
            # Override with feedback where available
            feedback_priority_map = {a: f['corrected_value'] for a, f in
                                      zip(df['account_code'], feedback_items) if a in feedback_accounts}
            y = df['account_code'].map(feedback_priority_map).fillna(y).values
        else:
            from src.ml.target_engineering import create_time_to_review_target
            y = create_time_to_review_target(df)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train new model
        with mlflow.start_run(run_name=f"retrain_{model_type}_{datetime.now().strftime('%Y%m%d')}"):
            if model_type == 'anomaly_detection':
                result = self.trainer.train_anomaly_detector(X, y, test_size=0.2)
            elif model_type == 'priority_classification':
                result = self.trainer.train_priority_classifier(X, y, test_size=0.2)
            else:
                result = self.trainer.train_attention_classifier(X, y, test_size=0.2)

            # Log feedback metadata
            mlflow.log_params({
                'feedback_count': len(feedback_items),
                'feedback_type': model_type,
                'retrain_date': datetime.now().isoformat()
            })

            new_metrics = result['metrics']

        # Compare with baseline
        if model_type in self.baseline_metrics:
            improvement = self._calculate_improvement(self.baseline_metrics[model_type], new_metrics)

            if improvement < 0.02:  # Less than 2% improvement
                return {
                    'status': 'rejected',
                    'reason': 'New model did not outperform baseline',
                    'improvement': improvement,
                    'baseline_metrics': self.baseline_metrics[model_type],
                    'new_metrics': new_metrics
                }

        # Mark feedback as used
        feedback_ids = [str(f['_id']) for f in feedback_items]
        self.feedback_collector.mark_feedback_used(feedback_ids)

        # Save new model
        self.trainer.save_models()

        return {
            'status': 'success',
            'feedback_count': len(feedback_items),
            'new_metrics': new_metrics,
            'model_version': self._get_next_version(model_type)
        }

    def _calculate_improvement(self, baseline: Dict, new: Dict) -> float:
        """Calculate relative improvement between baseline and new model."""
        # Use primary metric based on model type
        if 'r2' in baseline:
            return (new['r2'] - baseline['r2']) / (baseline['r2'] + 1e-10)
        elif 'accuracy' in baseline:
            return (new['accuracy'] - baseline['accuracy']) / (baseline['accuracy'] + 1e-10)
        elif 'roc_auc' in baseline:
            return (new['roc_auc'] - baseline['roc_auc']) / (baseline['roc_auc'] + 1e-10)
        else:
            return 0.0

    def _get_next_version(self, model_type: str) -> str:
        """Get next version number for model."""
        # Query MLflow for existing versions
        client = mlflow.tracking.MlflowClient()
        try:
            versions = client.search_model_versions(f"name='{model_type}'")
            latest = max([int(v.version) for v in versions])
            return f"v{latest + 1}"
        except:
            return "v1.0"

    def rollback_model(self, model_type: str, version: str):
        """Rollback to previous model version."""
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_type,
            version=version,
            stage="Production"
        )
        print(f"Rolled back {model_type} to version {version}")
```

**Acceptance Criteria**:
- ✅ Retraining pipeline executes end-to-end without errors
- ✅ Safety rail: New model rejected if <2% improvement
- ✅ Feedback marked as used after successful retraining
- ✅ Model versioning tracked in MLflow
- ✅ Rollback function tested

---

### 3.4 Testing & Deployment Strategy

**Testing Checklist**:
```python
# tests/test_ml_pipeline.py - CREATE

def test_feature_extraction():
    """Test feature engineering pipeline."""
    pass

def test_model_training():
    """Test all 3 models train successfully."""
    pass

def test_feedback_collection():
    """Test feedback storage and retrieval."""
    pass

def test_continual_learning():
    """Test retraining with feedback."""
    pass

def test_model_versioning():
    """Test MLflow model registry."""
    pass
```

**Deployment Plan**:
1. Train baseline models on initial seed data
2. Deploy to production (Streamlit app)
3. Collect feedback for 1 week
4. Trigger first retraining
5. A/B test new model (10% traffic)
6. Full rollout if metrics improve

---

## Part 3 Status Summary
Coverage: Complete ML pipeline with feature engineering (30 features), 3 model types, feedback collection UI, continual learning orchestration, safety rails, and testing strategy.

---

## Part 4: RAG & Vector Store for Conversational AI

**Duration**: 3-4 hours
**Priority**: 🟡 MEDIUM-HIGH - Enables "agentic" behavior and natural language queries
**Goal**: Build production-ready RAG system for context-aware AI assistant

### 4.1 Vector Store Architecture & Document Ingestion

#### **4.1.1 Document Corpus & Chunking Strategy** 🔴
**Purpose**: Prepare knowledge base for semantic search and retrieval.

**Document Sources**:
```yaml
Knowledge Base Sources:
  1. Project Documentation
     - README.md
     - Architecture docs (Architecture.md, Storage-Architecture.md)
     - ADRs (ADR-001, ADR-002)
     - Implementation guides
     - API documentation

  2. Accounting Domain Knowledge
     - GL account definitions
     - Trial balance concepts
     - Variance analysis methodologies
     - Review process SOPs
     - SLA policies

  3. System Metadata
     - Master Chart of Accounts (2736 entries)
     - GL account descriptions (501 active accounts)
     - Validation rules & expectations
     - Email templates

  4. Historical Context
     - Past review sessions (MongoDB)
     - Audit trail logs
     - User feedback summaries
     - FAQ from user queries

Total Documents: ~50-100 documents, ~200-500 chunks
```

**Chunking Strategy**:
```yaml
Chunking Configuration:
  Method: Recursive Character Text Splitter
  Chunk Size: 1000 characters
  Chunk Overlap: 200 characters (20% for context continuity)
  Separators: ["\n\n", "\n", ". ", " ", ""]

Metadata per Chunk:
  - source_file: Original document path
  - doc_type: documentation | accounting_knowledge | metadata | historical
  - chunk_index: Position in document
  - entity: If entity-specific (ABEX, AGEL, APL)
  - period: If period-specific
  - created_at: Timestamp
  - version: Document version
```

**Implementation**:
```python
# src/rag/document_processor.py - CREATE NEW FILE

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

class DocumentProcessor:
    """Process and chunk documents for vector store ingestion."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        self.processed_hashes = set()

    def load_documentation(self, docs_dir: str = "docs/") -> List[Document]:
        """
        Load all documentation files from docs directory.

        Args:
            docs_dir: Path to documentation directory

        Returns:
            List of LangChain Document objects
        """
        docs_path = Path(docs_dir)
        documents = []

        # Recursively find all markdown files
        for md_file in docs_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Create document with metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': str(md_file),
                        'doc_type': self._infer_doc_type(md_file),
                        'filename': md_file.name,
                        'created_at': datetime.utcnow().isoformat()
                    }
                )
                documents.append(doc)
            except Exception as e:
                print(f"Error loading {md_file}: {e}")

        return documents

    def load_accounting_knowledge(self) -> List[Document]:
        """
        Load accounting domain knowledge from curated sources.

        Returns:
            List of accounting concept documents
        """
        knowledge_base = [
            {
                'title': 'General Ledger Account Definition',
                'content': """
                A General Ledger (GL) account is a record used in accounting to sort and store
                balance sheet and income statement transactions. Each GL account has:
                - Account Code: Unique identifier (e.g., 101000, 201500)
                - Account Name: Descriptive label (e.g., Cash & Cash Equivalents)
                - Category: Assets, Liabilities, Revenue, Expenses, or Equity
                - Balance: Current financial amount (Debit or Credit)
                - Department: Organizational unit responsible

                GL accounts form the foundation of financial reporting and must be reviewed
                periodically for accuracy and completeness.
                """
            },
            {
                'title': 'Trial Balance Concept',
                'content': """
                A Trial Balance is a bookkeeping worksheet showing all ledger account balances
                at a specific date. Key principles:
                - Must balance: Total Debits = Total Credits
                - Prepared at period end (monthly, quarterly, annually)
                - Used to detect errors before financial statement preparation
                - Contains: Account Code, Account Name, Debit Balance, Credit Balance

                If trial balance doesn't balance, there are errors requiring investigation.
                """
            },
            {
                'title': 'Variance Analysis Methodology',
                'content': """
                Variance Analysis compares actual financial results to budgets or prior periods:
                - Period-over-Period: Current vs Previous (e.g., March 2024 vs Feb 2024)
                - Budget vs Actual: Planned vs Realized performance
                - Key metrics: Absolute variance, Percentage variance, Cumulative variance

                Significant variances (>10% or >₹50,000) require explanation and may indicate:
                - Business growth or decline
                - Seasonal patterns
                - Operational changes
                - Errors or irregularities requiring correction
                """
            },
            {
                'title': 'SLA and Review Process',
                'content': """
                Service Level Agreements (SLA) for GL account reviews:
                - Critical accounts: 2 business days
                - High priority: 5 business days
                - Medium priority: 10 business days
                - Low priority: 15 business days

                Review process:
                1. Assignment to reviewer based on department and workload
                2. Upload of supporting documentation (invoices, reconciliations)
                3. Review and validation by assigned user
                4. Approval or flagging for issues
                5. Documentation in audit trail

                Overdue reviews trigger escalation to department heads.
                """
            },
            {
                'title': 'Supporting Documentation Requirements',
                'content': """
                All GL account balances require supporting documentation:
                - Bank reconciliations for cash accounts
                - Ageing reports for receivables/payables
                - Fixed asset registers for PPE accounts
                - Invoices and contracts for revenue/expenses
                - Journal entry support for manual postings

                Documents must be:
                - Uploaded to system within SLA deadline
                - In accepted formats (PDF, Excel, images)
                - Clearly labeled with account code and period
                - Retained for audit purposes (7 years minimum)
                """
            }
        ]

        documents = []
        for item in knowledge_base:
            doc = Document(
                page_content=f"# {item['title']}\n\n{item['content'].strip()}",
                metadata={
                    'source': 'accounting_knowledge_base',
                    'doc_type': 'accounting_knowledge',
                    'title': item['title'],
                    'created_at': datetime.utcnow().isoformat()
                }
            )
            documents.append(doc)

        return documents

    def load_gl_metadata(self, session) -> List[Document]:
        """
        Load GL account metadata as searchable documents.

        Args:
            session: Database session

        Returns:
            List of GL account description documents
        """
        from src.db.postgres import get_all_gl_accounts

        accounts = get_all_gl_accounts(session)
        documents = []

        for account in accounts[:100]:  # Limit to 100 to avoid overwhelming vector store
            content = f"""
            Account Code: {account.account_code}
            Account Name: {account.account_name}
            Category: {account.category}
            Department: {account.department}
            Balance: ₹{account.balance:,.2f}
            Criticality: {account.criticality}
            Entity: {account.entity}
            Period: {account.period}

            This is a {account.category} account managed by the {account.department} department.
            Current balance is {'debit' if account.balance >= 0 else 'credit'}.
            """

            doc = Document(
                page_content=content.strip(),
                metadata={
                    'source': 'gl_accounts_metadata',
                    'doc_type': 'metadata',
                    'account_code': account.account_code,
                    'category': account.category,
                    'entity': account.entity,
                    'created_at': datetime.utcnow().isoformat()
                }
            )
            documents.append(doc)

        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks for vector store.

        Args:
            documents: List of Document objects

        Returns:
            List of chunked Document objects with metadata
        """
        chunked_docs = []

        for doc in documents:
            # Check if already processed (using content hash)
            content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()
            if content_hash in self.processed_hashes:
                continue

            # Split document into chunks
            chunks = self.text_splitter.split_text(doc.page_content)

            # Create Document objects for each chunk
            for i, chunk_text in enumerate(chunks):
                chunk_doc = Document(
                    page_content=chunk_text,
                    metadata={
                        **doc.metadata,
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'content_hash': content_hash
                    }
                )
                chunked_docs.append(chunk_doc)

            self.processed_hashes.add(content_hash)

        return chunked_docs

    def _infer_doc_type(self, file_path: Path) -> str:
        """Infer document type from file path."""
        path_str = str(file_path).lower()

        if 'adr' in path_str:
            return 'adr'
        elif 'architecture' in path_str:
            return 'architecture'
        elif 'guide' in path_str or 'tutorial' in path_str:
            return 'guide'
        elif 'phase' in path_str or 'implementation' in path_str:
            return 'implementation'
        elif 'test' in path_str:
            return 'testing'
        else:
            return 'documentation'
```

**Acceptance Criteria**:
- ✅ Document processor loads all markdown files from docs/
- ✅ Accounting knowledge base with 5+ domain concepts
- ✅ GL account metadata documents generated
- ✅ Chunking produces 200-500 chunks with proper metadata
- ✅ Content deduplication via hashing

---

#### **4.1.2 Vector Store Setup & Embeddings** 🔴
**Purpose**: Configure ChromaDB/FAISS for semantic search with embeddings.

**Vector Store Configuration**:
```yaml
Vector Store: ChromaDB (Primary) + FAISS (Backup)
Embedding Model: sentence-transformers/all-MiniLM-L6-v2
  - Dimensions: 384
  - Max sequence length: 256 tokens
  - Speed: ~2000 docs/sec on CPU
  - Quality: 0.82 semantic similarity benchmark

Collection Structure:
  - gl_knowledge: General GL and accounting concepts
  - project_docs: Technical implementation documentation
  - account_metadata: Specific GL account information
  - historical_context: Past reviews, queries, feedback

Persistence: data/vectors/chromadb/
```

**Implementation**:
```python
# src/rag/vector_store_manager.py - CREATE NEW FILE

from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

class VectorStoreManager:
    """Manage ChromaDB vector store for RAG system."""

    def __init__(self, persist_directory: str = "data/vectors/chromadb"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize embedding function
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.collections = {}

    def create_or_get_collection(
        self,
        collection_name: str,
        reset: bool = False
    ) -> chromadb.Collection:
        """
        Create or retrieve a ChromaDB collection.

        Args:
            collection_name: Name of collection
            reset: If True, delete existing and create fresh

        Returns:
            ChromaDB Collection object
        """
        if reset:
            try:
                self.client.delete_collection(collection_name)
            except:
                pass

        # Get or create collection
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"}  # Cosine similarity
        )

        self.collections[collection_name] = collection
        return collection

    def add_documents_to_collection(
        self,
        collection_name: str,
        documents: List[Document]
    ) -> int:
        """
        Add documents to vector store collection.

        Args:
            collection_name: Target collection
            documents: List of LangChain Document objects

        Returns:
            Number of documents added
        """
        collection = self.create_or_get_collection(collection_name)

        # Prepare data for ChromaDB
        ids = [f"{collection_name}_{i}" for i in range(len(documents))]
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        # Add to collection (ChromaDB handles embedding internally)
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

        return len(documents)

    def query_collection(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query vector store for similar documents.

        Args:
            collection_name: Collection to query
            query_text: Natural language query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {'doc_type': 'accounting_knowledge'})

        Returns:
            List of result dictionaries with documents and scores
        """
        if collection_name not in self.collections:
            collection = self.create_or_get_collection(collection_name)
        else:
            collection = self.collections[collection_name]

        # Query with optional filtering
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=filter_metadata if filter_metadata else None
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })

        return formatted_results

    def hybrid_search(
        self,
        query_text: str,
        collections: List[str],
        n_results_per_collection: int = 3
    ) -> List[Dict]:
        """
        Search across multiple collections and merge results.

        Args:
            query_text: Natural language query
            collections: List of collection names to search
            n_results_per_collection: Results per collection

        Returns:
            Merged and deduplicated results
        """
        all_results = []

        for coll_name in collections:
            try:
                results = self.query_collection(coll_name, query_text, n_results_per_collection)
                all_results.extend(results)
            except Exception as e:
                print(f"Error querying {coll_name}: {e}")

        # Sort by distance (lower is better)
        all_results.sort(key=lambda x: x.get('distance', float('inf')))

        # Deduplicate by content
        seen_content = set()
        unique_results = []
        for result in all_results:
            content = result['document'][:100]  # Use first 100 chars as fingerprint
            if content not in seen_content:
                unique_results.append(result)
                seen_content.add(content)

        return unique_results[:n_results_per_collection * len(collections)]

    def get_collection_stats(self) -> Dict[str, int]:
        """Get document counts for all collections."""
        stats = {}
        for collection in self.client.list_collections():
            stats[collection.name] = collection.count()
        return stats

    def reset_all_collections(self):
        """Delete all collections and start fresh."""
        for collection in self.client.list_collections():
            self.client.delete_collection(collection.name)
        self.collections = {}
        print("All collections reset.")
```

**Acceptance Criteria**:
- ✅ ChromaDB initialized with persistent storage
- ✅ Embedding model loads and generates 384-dim vectors
- ✅ Collections created: gl_knowledge, project_docs, account_metadata
- ✅ Query returns top-K relevant documents with similarity scores
- ✅ Hybrid search across collections with deduplication

---

### 4.2 RAG Pipeline Implementation

#### **4.2.1 Retrieval-Augmented Generation System** 🔴
**Purpose**: Build RAG pipeline that retrieves context and generates responses.

**RAG Architecture**:
```yaml
RAG Pipeline Flow:
  1. Query Processing
     - User query → Embedding model
     - Query expansion (synonyms, related terms)

  2. Retrieval
     - Semantic search across vector stores
     - Hybrid search (semantic + keyword)
     - Re-ranking by relevance score

  3. Context Assembly
     - Top-K documents retrieved (K=5)
     - Metadata filtering (entity, period, doc_type)
     - Deduplication and merging

  4. Prompt Construction
     - System prompt with role definition
     - Retrieved context injection
     - User query
     - Few-shot examples (optional)

  5. Generation
     - LLM call (Gemini 1.5 Flash)
     - Streaming response
     - Citation tracking

  6. Post-processing
     - Format markdown
     - Add source citations
     - Validate against hallucination
```

**Implementation**:
```python
# src/rag/rag_pipeline.py - CREATE NEW FILE

from typing import List, Dict, Optional, Tuple
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document as LCDocument

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for GL account queries."""

    def __init__(self, vector_store_manager, api_key: str):
        self.vector_store = vector_store_manager

        # Initialize LLM (Gemini)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3,  # Lower temp for factual responses
            max_output_tokens=1024
        )

        # Define system prompt
        self.system_prompt = """You are an AI assistant for Project Aura, an intelligent GL account review system for Adani Group's finance operations.

Your role:
- Answer questions about GL accounts, financial processes, and system usage
- Provide accurate information based on the context provided
- Cite sources when referencing specific documentation
- Admit when you don't know something rather than guessing
- Be concise but thorough in explanations

Context Guidelines:
- Use the retrieved documents as your primary information source
- If context is insufficient, ask for clarification
- Mention relevant GL account codes when applicable
- Reference specific sections of documentation when helpful

Response Format:
- Start with a direct answer
- Provide supporting details
- List sources at the end if applicable
"""

        self.qa_prompt_template = """Context from documentation:
{context}

Question: {question}

Answer: """

    def retrieve_context(
        self,
        query: str,
        collections: List[str] = ['gl_knowledge', 'project_docs'],
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Tuple[List[Dict], str]:
        """
        Retrieve relevant context for a query.

        Args:
            query: User's natural language query
            collections: Collections to search
            top_k: Number of documents to retrieve
            filter_metadata: Optional filters

        Returns:
            Tuple of (results_list, formatted_context_string)
        """
        # Perform hybrid search
        results = self.vector_store.hybrid_search(
            query_text=query,
            collections=collections,
            n_results_per_collection=top_k // len(collections) + 1
        )

        # Format context for prompt
        context_parts = []
        for i, result in enumerate(results[:top_k], 1):
            source = result['metadata'].get('source', 'Unknown')
            doc_type = result['metadata'].get('doc_type', 'Unknown')
            content = result['document']

            context_parts.append(f"""
[Source {i}: {source} ({doc_type})]
{content}
---
""")

        context_string = "\n".join(context_parts)

        return results, context_string

    def generate_response(
        self,
        query: str,
        context: str
    ) -> Dict[str, any]:
        """
        Generate response using LLM with retrieved context.

        Args:
            query: User question
            context: Retrieved context string

        Returns:
            Dict with response and metadata
        """
        # Construct prompt
        prompt = self.qa_prompt_template.format(
            context=context,
            question=query
        )

        # Add system prompt
        full_prompt = f"{self.system_prompt}\n\n{prompt}"

        # Generate response
        try:
            response = self.llm.invoke(full_prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            answer = f"Error generating response: {str(e)}"

        return {
            'answer': answer,
            'query': query,
            'context_used': context
        }

    def query(
        self,
        question: str,
        collections: Optional[List[str]] = None,
        filter_metadata: Optional[Dict] = None,
        include_sources: bool = True
    ) -> Dict:
        """
        End-to-end RAG query.

        Args:
            question: User's natural language question
            collections: Collections to search (default: all)
            filter_metadata: Metadata filters
            include_sources: Include source documents in response

        Returns:
            Dict with answer, sources, and metadata
        """
        # Default collections
        if collections is None:
            collections = ['gl_knowledge', 'project_docs', 'account_metadata']

        # Retrieve context
        results, context = self.retrieve_context(
            query=question,
            collections=collections,
            top_k=5,
            filter_metadata=filter_metadata
        )

        # Generate response
        response = self.generate_response(question, context)

        # Add sources if requested
        if include_sources:
            sources = []
            for result in results[:5]:
                sources.append({
                    'source': result['metadata'].get('source', 'Unknown'),
                    'doc_type': result['metadata'].get('doc_type', 'Unknown'),
                    'relevance_score': 1 - result.get('distance', 0)  # Convert distance to similarity
                })
            response['sources'] = sources

        return response

    def query_with_entity_context(
        self,
        question: str,
        entity: str,
        period: Optional[str] = None
    ) -> Dict:
        """
        Query with entity-specific context filtering.

        Args:
            question: User question
            entity: Entity code (ABEX, AGEL, APL)
            period: Optional period filter

        Returns:
            Response dict with entity-filtered results
        """
        # Build metadata filter
        filter_metadata = {'entity': entity}
        if period:
            filter_metadata['period'] = period

        return self.query(
            question=question,
            filter_metadata=filter_metadata,
            include_sources=True
        )

    def batch_query(self, questions: List[str]) -> List[Dict]:
        """Process multiple queries in batch."""
        responses = []
        for question in questions:
            response = self.query(question)
            responses.append(response)
        return responses
```

**Acceptance Criteria**:
- ✅ RAG pipeline retrieves relevant context for queries
- ✅ LLM generates coherent responses using context
- ✅ Source citations included in responses
- ✅ Entity-specific filtering works correctly
- ✅ Batch query processing supported

---

#### **4.2.2 LangChain Agent with Structured Tools** 🔴
**Purpose**: Enhance agent.py with RAG-powered tools and structured routing.

**Enhanced Agent Architecture**:
```yaml
Agent Components:
  1. RAG Query Tool
     - Natural language knowledge retrieval
     - Cites documentation sources

  2. GL Account Lookup Tool
     - Fetch specific account details
     - Returns structured data

  3. Analytics Tool
     - Run variance analysis
     - Calculate hygiene scores
     - Generate reports

  4. Assignment Tool
     - Get reviewer assignments
     - Check SLA status

  5. Feedback Tool
     - Submit ML feedback
     - Query feedback stats

Tool Selection Strategy:
  - Pydantic schemas for input validation
  - Deterministic routing based on query pattern
  - Fallback to RAG for ambiguous queries
```

**Implementation**:
```python
# src/agent.py - ENHANCE EXISTING FILE

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Optional, List

class GLAccountQuery(BaseModel):
    """Schema for GL account lookup queries."""
    account_code: Optional[str] = Field(None, description="GL account code (e.g., '101000')")
    entity: Optional[str] = Field(None, description="Entity code (ABEX, AGEL, APL)")
    period: Optional[str] = Field(None, description="Period (e.g., '2024-03')")

class AnalyticsQuery(BaseModel):
    """Schema for analytics queries."""
    analysis_type: str = Field(..., description="Type: variance, hygiene, sla, or review_status")
    entity: str = Field(..., description="Entity code")
    period: str = Field(..., description="Period")
    compare_period: Optional[str] = Field(None, description="Period to compare against")

class RAGQuery(BaseModel):
    """Schema for RAG knowledge queries."""
    question: str = Field(..., description="Natural language question")
    collections: Optional[List[str]] = Field(None, description="Collections to search")

def create_enhanced_agent(rag_pipeline, session):
    """
    Create LangChain agent with RAG and structured tools.

    Args:
        rag_pipeline: RAGPipeline instance
        session: Database session

    Returns:
        AgentExecutor instance
    """
    # Tool 1: RAG Query
    def rag_query_tool(question: str) -> str:
        """Query the knowledge base for documentation and accounting concepts."""
        response = rag_pipeline.query(question)
        answer = response['answer']
        sources = response.get('sources', [])

        if sources:
            source_text = "\n\nSources:\n" + "\n".join([
                f"- {s['source']} ({s['doc_type']})" for s in sources[:3]
            ])
            return answer + source_text
        return answer

    # Tool 2: GL Account Lookup
    def gl_account_lookup_tool(account_code: str, entity: str = "ABEX") -> str:
        """Look up specific GL account details."""
        from src.db.postgres import get_gl_account_by_code

        account = get_gl_account_by_code(session, account_code, entity)
        if not account:
            return f"GL account {account_code} not found for entity {entity}."

        return f"""
GL Account Details:
- Code: {account.account_code}
- Name: {account.account_name}
- Category: {account.category}
- Balance: ₹{account.balance:,.2f}
- Department: {account.department}
- Criticality: {account.criticality}
- Review Status: {account.review_status}
- Entity: {account.entity}
- Period: {account.period}
"""

    # Tool 3: Analytics Tool
    def analytics_tool(analysis_type: str, entity: str, period: str, compare_period: str = None) -> str:
        """Run analytics: variance, hygiene, sla, or review_status."""
        from src.analytics import (
            calculate_variance_analysis,
            calculate_gl_hygiene_score,
            calculate_review_status_summary
        )

        if analysis_type == "variance" and compare_period:
            result = calculate_variance_analysis(entity, period, compare_period)
            return f"Variance Analysis: {result['variance_summary']}"

        elif analysis_type == "hygiene":
            result = calculate_gl_hygiene_score(entity, period)
            return f"GL Hygiene Score: {result['overall_score']:.0f}/100 (Grade: {result['grade']})"

        elif analysis_type == "review_status":
            result = calculate_review_status_summary(entity, period)
            overall = result['overall']
            return f"""Review Status:
- Total Accounts: {overall['total_accounts']}
- Reviewed: {overall['reviewed']} ({overall['completion_pct']:.1f}%)
- Pending: {overall['pending']}
- Flagged: {overall['flagged']}
"""

        else:
            return f"Unknown analysis type: {analysis_type}"

    # Tool 4: Assignment Lookup
    def assignment_tool(account_code: str = None, user_email: str = None) -> str:
        """Check reviewer assignments for account or user."""
        from src.db.postgres import get_user_assignments

        if user_email:
            assignments = get_user_assignments(session, user_email)
            if not assignments:
                return f"No assignments found for {user_email}."

            return f"User {user_email} has {len(assignments)} assignments."

        elif account_code:
            # Would query responsibility_matrix for specific account
            return f"Assignment lookup for account {account_code} (not yet implemented)."

        return "Please provide either account_code or user_email."

    # Create Tool objects
    tools = [
        Tool(
            name="RAG_Query",
            func=rag_query_tool,
            description="Query the knowledge base for documentation, accounting concepts, and system help. Use for questions about GL accounts, processes, or terminology."
        ),
        Tool(
            name="GL_Account_Lookup",
            func=gl_account_lookup_tool,
            description="Look up details for a specific GL account by account code and entity. Returns balance, category, department, status, etc."
        ),
        Tool(
            name="Analytics",
            func=analytics_tool,
            description="Run analytics: variance analysis, hygiene scoring, SLA compliance, or review status. Requires analysis_type, entity, and period."
        ),
        Tool(
            name="Assignment_Lookup",
            func=assignment_tool,
            description="Check reviewer assignments for a GL account or user. Provide account_code or user_email."
        )
    ]

    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.2,
        max_output_tokens=1024
    )

    # Agent prompt
    agent_prompt = PromptTemplate.from_template("""You are an AI assistant for Project Aura, helping users with GL account review tasks.

You have access to the following tools:
{tools}

Tool Names: {tool_names}

When answering:
1. Understand the user's intent
2. Choose the most appropriate tool
3. Use the tool to gather information
4. Provide a clear, helpful response

Question: {input}
{agent_scratchpad}
""")

    # Create agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=agent_prompt
    )

    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    return agent_executor
```

**Acceptance Criteria**:
- ✅ Agent initialized with 4+ structured tools
- ✅ RAG tool retrieves and cites documentation
- ✅ GL lookup tool returns account details
- ✅ Analytics tool calculates metrics on-demand
- ✅ Agent routes queries to correct tools
- ✅ Handles multi-step reasoning (e.g., "What's the hygiene score for ABEX and why?")

---

### 4.3 Conversational UI Integration

#### **4.3.1 Streamlit Chat Interface** 🔴
**Purpose**: Build user-facing chat interface for AI assistant.

**Implementation**:
```python
# src/dashboards/ai_assistant_page.py - CREATE

import streamlit as st
from datetime import datetime

def render_ai_assistant_page(rag_pipeline, agent_executor):
    """Render conversational AI assistant page."""
    st.title("🤖 AI Assistant")
    st.caption("Ask questions about GL accounts, processes, or system usage")

    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI assistant for GL account reviews. How can I help you today?"}
        ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Use agent for complex queries, RAG for simple lookups
                    if any(word in prompt.lower() for word in ['what', 'how', 'why', 'explain']):
                        response = rag_pipeline.query(prompt)
                        answer = response['answer']

                        # Show sources
                        if response.get('sources'):
                            answer += "\n\n**Sources:**\n"
                            for source in response['sources'][:3]:
                                answer += f"- {source['source']}\n"
                    else:
                        # Use agent for action queries
                        result = agent_executor.invoke({"input": prompt})
                        answer = result.get('output', 'No response generated.')

                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Suggested queries
    st.sidebar.subheader("💡 Suggested Questions")
    suggestions = [
        "What is a trial balance?",
        "How do I calculate variance?",
        "What are the SLA deadlines for reviews?",
        "Show me GL account 101000 details",
        "What's the hygiene score for ABEX in 2024-03?"
    ]

    for suggestion in suggestions:
        if st.sidebar.button(suggestion, key=f"suggest_{suggestion[:20]}"):
            st.session_state.messages.append({"role": "user", "content": suggestion})
            st.rerun()
```

**Acceptance Criteria**:
- ✅ Chat interface with message history
- ✅ Real-time response generation
- ✅ Source citations displayed
- ✅ Suggested questions for quick access
- ✅ Error handling for failed queries

---

### 4.4 Testing & Performance

**Unit Tests**:
```python
# tests/test_rag_pipeline.py - CREATE

def test_document_processing():
    """Test document loading and chunking."""
    pass

def test_vector_store_ingestion():
    """Test ChromaDB document insertion."""
    pass

def test_semantic_search():
    """Test query retrieval accuracy."""
    pass

def test_rag_response_generation():
    """Test end-to-end RAG pipeline."""
    pass

def test_agent_tool_routing():
    """Test agent selects correct tools."""
    pass
```

**Performance Benchmarks**:
- Document embedding: <5 seconds for 100 documents
- Query retrieval: <500ms
- RAG response generation: <3 seconds
- Agent multi-step reasoning: <5 seconds

---

## Part 4 Status Summary
Coverage: Complete RAG system with document processing, ChromaDB vector store, RAG pipeline with Gemini LLM, enhanced LangChain agent with 4 structured tools, conversational UI, and testing strategy.

---

## Part 5: Email Automation System

**Duration**: 2-3 hours
**Priority**: 🟡 MEDIUM - Enhances workflow automation and user engagement
**Goal**: Build automated email notification system for review lifecycle events

### 5.1 Email Template Engine

#### **5.1.1 Template Design & Management** 🔴
**Purpose**: Create reusable email templates with dynamic content injection.

**Template Types**:
```yaml
Email Templates:
  1. Assignment Notification
     - Trigger: New GL account assigned to reviewer
     - Recipients: Assigned reviewer
     - Content: Account details, SLA deadline, action required

  2. Upload Reminder
     - Trigger: Supporting docs not uploaded (SLA - 2 days)
     - Recipients: Assigned reviewer
     - Content: Missing docs list, deadline warning

  3. Review Completion Notification
     - Trigger: Review status changed to "Reviewed"
     - Recipients: Department head, finance team
     - Content: Account summary, reviewer comments

  4. Approval Notification
     - Trigger: Account approved by approver
     - Recipients: Reviewer, department head
     - Content: Approval details, next steps

  5. SLA Breach Alert
     - Trigger: Review deadline passed without completion
     - Recipients: Reviewer, department head, escalation list
     - Content: Overdue details, business impact

  6. Weekly Summary Report
     - Trigger: Every Monday 9 AM
     - Recipients: All stakeholders
     - Content: Weekly stats, pending reviews, hygiene score
```

**Template Structure**:
```yaml
Template Schema:
  template_id: unique_identifier
  name: Human-readable name
  subject: Email subject with variables
  body_html: HTML template with Jinja2 syntax
  body_text: Plain text fallback
  variables: List of required variables (account_code, reviewer_name, etc.)
  category: assignment | reminder | notification | alert | report
  priority: high | medium | low
  attachments_allowed: boolean
```

**Implementation**:
```python
# src/email/template_engine.py - CREATE NEW FILE

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template
import json

class EmailTemplateEngine:
    """Manage email templates with Jinja2 rendering."""

    def __init__(self, templates_dir: str = "src/email/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Register custom filters
        self.env.filters['currency'] = self._format_currency
        self.env.filters['date'] = self._format_date

        # Template registry
        self.templates = self._load_template_registry()

    def _load_template_registry(self) -> Dict:
        """Load template metadata registry."""
        registry_file = self.templates_dir / "registry.json"

        if registry_file.exists():
            with open(registry_file, 'r') as f:
                return json.load(f)

        # Default registry
        return {
            'assignment_notification': {
                'name': 'Assignment Notification',
                'subject': '🔔 New GL Account Assignment: {{ account_code }}',
                'template_file': 'assignment_notification.html',
                'variables': ['account_code', 'account_name', 'reviewer_name', 'deadline', 'balance'],
                'category': 'assignment',
                'priority': 'high'
            },
            'upload_reminder': {
                'name': 'Upload Reminder',
                'subject': '⏰ Reminder: Upload Supporting Documents for {{ account_code }}',
                'template_file': 'upload_reminder.html',
                'variables': ['account_code', 'reviewer_name', 'deadline', 'days_remaining'],
                'category': 'reminder',
                'priority': 'medium'
            },
            'review_completion': {
                'name': 'Review Completion Notification',
                'subject': '✅ GL Account Review Completed: {{ account_code }}',
                'template_file': 'review_completion.html',
                'variables': ['account_code', 'account_name', 'reviewer_name', 'completion_date', 'comments'],
                'category': 'notification',
                'priority': 'medium'
            },
            'approval_notification': {
                'name': 'Approval Notification',
                'subject': '✨ GL Account Approved: {{ account_code }}',
                'template_file': 'approval_notification.html',
                'variables': ['account_code', 'approver_name', 'approval_date'],
                'category': 'notification',
                'priority': 'medium'
            },
            'sla_breach_alert': {
                'name': 'SLA Breach Alert',
                'subject': '🚨 URGENT: SLA Breach for GL Account {{ account_code }}',
                'template_file': 'sla_breach_alert.html',
                'variables': ['account_code', 'reviewer_name', 'deadline', 'days_overdue', 'escalation_level'],
                'category': 'alert',
                'priority': 'high'
            },
            'weekly_summary': {
                'name': 'Weekly Summary Report',
                'subject': '📊 Weekly GL Review Summary - {{ week_ending }}',
                'template_file': 'weekly_summary.html',
                'variables': ['week_ending', 'total_accounts', 'reviewed', 'pending', 'hygiene_score'],
                'category': 'report',
                'priority': 'low'
            }
        }

    def render_template(
        self,
        template_id: str,
        context: Dict,
        format: str = 'html'
    ) -> Dict[str, str]:
        """
        Render email template with context data.

        Args:
            template_id: Template identifier
            context: Dictionary with template variables
            format: 'html' or 'text'

        Returns:
            Dict with 'subject' and 'body'
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found in registry")

        template_meta = self.templates[template_id]

        # Validate required variables
        missing_vars = set(template_meta['variables']) - set(context.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        # Render subject
        subject_template = Template(template_meta['subject'])
        subject = subject_template.render(**context)

        # Render body
        template_file = template_meta['template_file']
        if format == 'text':
            template_file = template_file.replace('.html', '.txt')

        try:
            body_template = self.env.get_template(template_file)
            body = body_template.render(**context)
        except Exception as e:
            # Fallback to simple template
            body = self._generate_fallback_body(template_id, context)

        return {
            'subject': subject,
            'body': body,
            'format': format,
            'priority': template_meta['priority']
        }

    def _generate_fallback_body(self, template_id: str, context: Dict) -> str:
        """Generate simple fallback email body."""
        body = f"<h2>Notification: {template_id.replace('_', ' ').title()}</h2>\n\n"
        body += "<ul>\n"
        for key, value in context.items():
            body += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>\n"
        body += "</ul>\n"
        body += "\n<p>This is an automated notification from Project Aura.</p>"
        return body

    def _format_currency(self, value: float) -> str:
        """Format number as Indian currency."""
        return f"₹{value:,.2f}"

    def _format_date(self, value: str) -> str:
        """Format date string."""
        try:
            dt = datetime.fromisoformat(value)
            return dt.strftime("%B %d, %Y")
        except:
            return value

    def create_template_file(self, template_id: str, html_content: str):
        """Save HTML template file."""
        template_meta = self.templates.get(template_id)
        if not template_meta:
            raise ValueError(f"Template {template_id} not in registry")

        template_file = self.templates_dir / template_meta['template_file']
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Template saved: {template_file}")
```

**Sample HTML Template**:
```html
<!-- src/email/templates/assignment_notification.html - CREATE -->

<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background: #0066cc; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .account-details { background: white; padding: 15px; border-left: 4px solid #0066cc; margin: 20px 0; }
        .action-button { display: inline-block; padding: 12px 24px; background: #0066cc; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        .deadline { color: #d9534f; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔔 New GL Account Assignment</h1>
    </div>

    <div class="content">
        <p>Hello <strong>{{ reviewer_name }}</strong>,</p>

        <p>You have been assigned a new GL account for review in Project Aura.</p>

        <div class="account-details">
            <h3>Account Details</h3>
            <p><strong>Account Code:</strong> {{ account_code }}</p>
            <p><strong>Account Name:</strong> {{ account_name }}</p>
            <p><strong>Balance:</strong> {{ balance|currency }}</p>
            <p><strong>Entity:</strong> {{ entity }}</p>
            <p><strong>Period:</strong> {{ period }}</p>
            <p class="deadline"><strong>⏰ Review Deadline:</strong> {{ deadline|date }}</p>
        </div>

        <p>Please complete the following actions:</p>
        <ul>
            <li>Upload supporting documentation (bank statements, reconciliations, invoices)</li>
            <li>Review account balance accuracy</li>
            <li>Flag any discrepancies or issues</li>
            <li>Mark as reviewed once complete</li>
        </ul>

        <center>
            <a href="{{ app_url }}/review/{{ account_code }}" class="action-button">
                Start Review Now →
            </a>
        </center>

        <p><small>If you cannot complete this review by the deadline, please contact your department head immediately.</small></p>
    </div>

    <div class="footer">
        <p>This is an automated notification from Project Aura | Adani Group Finance Operations</p>
        <p>Do not reply to this email.</p>
    </div>
</body>
</html>
```

**Acceptance Criteria**:
- ✅ Template engine loads 6+ template types
- ✅ Jinja2 rendering with variable substitution
- ✅ Custom filters for currency and date formatting
- ✅ HTML and plain text versions supported
- ✅ Fallback template generation for missing files

---

### 5.2 SMTP Email Sender

#### **5.2.1 Email Delivery Service** 🔴
**Purpose**: Send emails via SMTP with retry logic and tracking.

**SMTP Configuration**:
```yaml
SMTP Settings:
  Provider: Gmail SMTP / SendGrid / AWS SES
  Host: smtp.gmail.com
  Port: 587 (TLS) or 465 (SSL)
  Authentication: Required
  Max Recipients: 50 per email
  Rate Limit: 100 emails/hour (configurable)
  Retry Policy: 3 attempts with exponential backoff
```

**Implementation**:
```python
# src/email/email_sender.py - CREATE NEW FILE

import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Dict, Optional
from datetime import datetime
import os

from src.db.mongodb import log_email_event

class EmailSender:
    """Send emails via SMTP with tracking and retry logic."""

    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = 587,
        smtp_user: str = None,
        smtp_password: str = None,
        from_email: str = None,
        from_name: str = "Project Aura"
    ):
        # Load from environment if not provided
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.getenv('SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.from_email = from_email or os.getenv('FROM_EMAIL', self.smtp_user)
        self.from_name = from_name

        # Validate configuration
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            raise ValueError("SMTP configuration incomplete. Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD env vars.")

        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[Dict]] = None,
        priority: str = 'medium',
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Send email with retry logic.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text fallback (optional)
            cc_emails: CC recipients
            bcc_emails: BCC recipients
            attachments: List of dicts with 'filename' and 'content' keys
            priority: 'high', 'medium', or 'low'
            metadata: Additional metadata to log

        Returns:
            Dict with status and tracking info
        """
        email_id = f"email_{int(datetime.utcnow().timestamp())}"

        # Prepare message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.from_email}>"
        msg['To'] = ', '.join(to_emails)

        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)

        # Set priority
        if priority == 'high':
            msg['X-Priority'] = '1'
            msg['Importance'] = 'high'

        # Attach text and HTML parts
        if body_text:
            part_text = MIMEText(body_text, 'plain')
            msg.attach(part_text)

        part_html = MIMEText(body_html, 'html')
        msg.attach(part_html)

        # Attach files
        if attachments:
            for attachment in attachments:
                part = MIMEApplication(attachment['content'])
                part.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])
                msg.attach(part)

        # Send with retries
        all_recipients = to_emails + (cc_emails or []) + (bcc_emails or [])

        for attempt in range(self.max_retries):
            try:
                # Connect to SMTP server
                if self.smtp_port == 465:
                    server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
                else:
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                    server.starttls()

                # Authenticate
                server.login(self.smtp_user, self.smtp_password)

                # Send email
                server.send_message(msg)
                server.quit()

                # Log success
                log_result = self._log_email(
                    email_id=email_id,
                    to_emails=to_emails,
                    subject=subject,
                    status='sent',
                    attempt=attempt + 1,
                    metadata=metadata
                )

                return {
                    'email_id': email_id,
                    'status': 'sent',
                    'recipients': len(all_recipients),
                    'timestamp': datetime.utcnow().isoformat()
                }

            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    # Log failure
                    self._log_email(
                        email_id=email_id,
                        to_emails=to_emails,
                        subject=subject,
                        status='failed',
                        attempt=attempt + 1,
                        error=str(e),
                        metadata=metadata
                    )

                    return {
                        'email_id': email_id,
                        'status': 'failed',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }

    def send_bulk_emails(
        self,
        emails: List[Dict],
        batch_size: int = 10,
        delay_between_batches: int = 5
    ) -> Dict:
        """
        Send multiple emails in batches.

        Args:
            emails: List of email dicts with send_email() parameters
            batch_size: Emails per batch
            delay_between_batches: Seconds to wait between batches

        Returns:
            Summary statistics
        """
        results = {'sent': 0, 'failed': 0, 'total': len(emails)}

        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]

            for email_data in batch:
                result = self.send_email(**email_data)

                if result['status'] == 'sent':
                    results['sent'] += 1
                else:
                    results['failed'] += 1

            # Delay between batches (rate limiting)
            if i + batch_size < len(emails):
                time.sleep(delay_between_batches)

        return results

    def _log_email(
        self,
        email_id: str,
        to_emails: List[str],
        subject: str,
        status: str,
        attempt: int,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Log email event to MongoDB."""
        event_data = {
            'email_id': email_id,
            'recipients': to_emails,
            'subject': subject,
            'status': status,
            'attempt': attempt,
            'timestamp': datetime.utcnow(),
            'from_email': self.from_email
        }

        if error:
            event_data['error'] = error

        if metadata:
            event_data['metadata'] = metadata

        try:
            log_email_event(event_data)
        except Exception as e:
            print(f"Failed to log email event: {e}")
```

**Acceptance Criteria**:
- ✅ SMTP connection with TLS/SSL support
- ✅ Email sending with HTML/text formats
- ✅ Attachment support for PDFs and Excel files
- ✅ Retry logic with exponential backoff (3 attempts)
- ✅ Email tracking logged to MongoDB
- ✅ Bulk email sending with rate limiting

---

### 5.3 Notification Triggers

#### **5.3.1 Event-Driven Notification System** 🔴
**Purpose**: Automatically trigger emails based on system events.

**Trigger Configuration**:
```yaml
Notification Triggers:
  1. On Assignment Created
     - Event: responsibility_matrix record inserted
     - Template: assignment_notification
     - Recipients: assigned_user_email
     - Timing: Immediate

  2. Upload Reminder (2 days before deadline)
     - Event: Daily cron job
     - Condition: supporting_docs empty AND (deadline - now) <= 2 days
     - Template: upload_reminder
     - Recipients: assigned_user_email
     - Timing: 9:00 AM daily

  3. Review Completion
     - Event: gl_account.review_status = 'Reviewed'
     - Template: review_completion
     - Recipients: department_head, finance_team
     - Timing: Immediate

  4. Approval
     - Event: gl_account.approval_status = 'Approved'
     - Template: approval_notification
     - Recipients: reviewer, department_head
     - Timing: Immediate

  5. SLA Breach
     - Event: Daily cron job
     - Condition: deadline < now AND review_status != 'Reviewed'
     - Template: sla_breach_alert
     - Recipients: reviewer, department_head, escalation_list
     - Timing: 10:00 AM daily

  6. Weekly Summary
     - Event: Weekly cron (Monday 9:00 AM)
     - Template: weekly_summary
     - Recipients: all_stakeholders
     - Timing: Weekly
```

**Implementation**:
```python
# src/email/notification_manager.py - CREATE NEW FILE

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.email.template_engine import EmailTemplateEngine
from src.email.email_sender import EmailSender
from src.db.postgres import get_postgres_session
from src.db.mongodb import save_notification_log

class NotificationManager:
    """Manage automated email notifications based on system events."""

    def __init__(self, template_engine: EmailTemplateEngine, email_sender: EmailSender):
        self.template_engine = template_engine
        self.email_sender = email_sender
        self.session = get_postgres_session()

    def trigger_assignment_notification(
        self,
        account_code: str,
        entity: str,
        reviewer_email: str,
        reviewer_name: str,
        deadline: datetime
    ) -> Dict:
        """
        Send notification when GL account assigned to reviewer.

        Args:
            account_code: GL account code
            entity: Entity code
            reviewer_email: Reviewer's email
            reviewer_name: Reviewer's name
            deadline: Review deadline

        Returns:
            Email send result
        """
        from src.db.postgres import get_gl_account_by_code

        # Get account details
        account = get_gl_account_by_code(self.session, account_code, entity)
        if not account:
            return {'status': 'failed', 'error': 'Account not found'}

        # Prepare context
        context = {
            'account_code': account.account_code,
            'account_name': account.account_name,
            'reviewer_name': reviewer_name,
            'balance': account.balance,
            'entity': account.entity,
            'period': account.period,
            'deadline': deadline.isoformat(),
            'app_url': os.getenv('APP_URL', 'http://localhost:8501')
        }

        # Render template
        email_content = self.template_engine.render_template(
            'assignment_notification',
            context
        )

        # Send email
        result = self.email_sender.send_email(
            to_emails=[reviewer_email],
            subject=email_content['subject'],
            body_html=email_content['body'],
            priority='high',
            metadata={
                'trigger': 'assignment',
                'account_code': account_code,
                'entity': entity
            }
        )

        # Log notification
        self._log_notification(
            notification_type='assignment',
            recipient=reviewer_email,
            account_code=account_code,
            status=result['status']
        )

        return result

    def trigger_upload_reminders(self) -> Dict:
        """
        Send reminders for accounts with missing supporting docs.
        Runs daily via cron job.

        Returns:
            Summary of reminders sent
        """
        from src.db.postgres import get_accounts_needing_upload_reminder

        # Query accounts with approaching deadlines and no supporting docs
        accounts = get_accounts_needing_upload_reminder(
            self.session,
            days_before_deadline=2
        )

        emails_to_send = []

        for account, assignment in accounts:
            context = {
                'account_code': account.account_code,
                'reviewer_name': assignment.user_name,
                'deadline': assignment.review_deadline.isoformat(),
                'days_remaining': (assignment.review_deadline - datetime.utcnow()).days,
                'app_url': os.getenv('APP_URL', 'http://localhost:8501')
            }

            email_content = self.template_engine.render_template(
                'upload_reminder',
                context
            )

            emails_to_send.append({
                'to_emails': [assignment.user_email],
                'subject': email_content['subject'],
                'body_html': email_content['body'],
                'priority': 'medium',
                'metadata': {
                    'trigger': 'upload_reminder',
                    'account_code': account.account_code
                }
            })

        # Send bulk emails
        result = self.email_sender.send_bulk_emails(emails_to_send)

        return {
            'trigger': 'upload_reminder',
            'total': result['total'],
            'sent': result['sent'],
            'failed': result['failed']
        }

    def trigger_sla_breach_alerts(self) -> Dict:
        """
        Send alerts for overdue reviews.
        Runs daily via cron job.

        Returns:
            Summary of alerts sent
        """
        from src.db.postgres import get_overdue_accounts

        # Query overdue accounts
        overdue_accounts = get_overdue_accounts(self.session)

        emails_to_send = []

        for account, assignment in overdue_accounts:
            days_overdue = (datetime.utcnow() - assignment.review_deadline).days
            escalation_level = 'critical' if days_overdue > 5 else 'high'

            context = {
                'account_code': account.account_code,
                'reviewer_name': assignment.user_name,
                'deadline': assignment.review_deadline.isoformat(),
                'days_overdue': days_overdue,
                'escalation_level': escalation_level,
                'app_url': os.getenv('APP_URL', 'http://localhost:8501')
            }

            email_content = self.template_engine.render_template(
                'sla_breach_alert',
                context
            )

            # Send to reviewer and department head
            recipients = [assignment.user_email]
            if assignment.department_head_email:
                recipients.append(assignment.department_head_email)

            emails_to_send.append({
                'to_emails': recipients,
                'subject': email_content['subject'],
                'body_html': email_content['body'],
                'priority': 'high',
                'metadata': {
                    'trigger': 'sla_breach',
                    'account_code': account.account_code,
                    'days_overdue': days_overdue
                }
            })

        # Send bulk emails
        result = self.email_sender.send_bulk_emails(emails_to_send)

        return {
            'trigger': 'sla_breach',
            'total': result['total'],
            'sent': result['sent'],
            'failed': result['failed']
        }

    def trigger_weekly_summary(self, recipient_list: List[str]) -> Dict:
        """
        Send weekly summary report to stakeholders.
        Runs weekly via cron job (Monday 9:00 AM).

        Args:
            recipient_list: List of stakeholder emails

        Returns:
            Email send result
        """
        from src.analytics import calculate_review_status_summary, calculate_gl_hygiene_score

        # Calculate stats for all entities
        week_ending = datetime.utcnow().strftime('%Y-%m-%d')

        # Aggregate stats (simplified - in production, query across all entities)
        total_accounts = 501
        reviewed = 375
        pending = 100
        flagged = 26
        hygiene_score = 82

        context = {
            'week_ending': week_ending,
            'total_accounts': total_accounts,
            'reviewed': reviewed,
            'pending': pending,
            'flagged': flagged,
            'hygiene_score': hygiene_score,
            'completion_pct': round((reviewed / total_accounts) * 100, 1),
            'app_url': os.getenv('APP_URL', 'http://localhost:8501')
        }

        email_content = self.template_engine.render_template(
            'weekly_summary',
            context
        )

        # Send to all stakeholders
        result = self.email_sender.send_email(
            to_emails=recipient_list,
            subject=email_content['subject'],
            body_html=email_content['body'],
            priority='low',
            metadata={
                'trigger': 'weekly_summary',
                'week_ending': week_ending
            }
        )

        return result

    def _log_notification(
        self,
        notification_type: str,
        recipient: str,
        account_code: str,
        status: str
    ):
        """Log notification to MongoDB."""
        log_data = {
            'notification_type': notification_type,
            'recipient': recipient,
            'account_code': account_code,
            'status': status,
            'timestamp': datetime.utcnow()
        }

        try:
            save_notification_log(log_data)
        except Exception as e:
            print(f"Failed to log notification: {e}")
```

**Cron Job Configuration** (for scheduled triggers):
```python
# scripts/email_cron_jobs.py - CREATE NEW FILE

from apscheduler.schedulers.blocking import BlockingScheduler
from src.email.notification_manager import NotificationManager
from src.email.template_engine import EmailTemplateEngine
from src.email.email_sender import EmailSender

def setup_email_cron_jobs():
    """Configure scheduled email notification jobs."""

    # Initialize components
    template_engine = EmailTemplateEngine()
    email_sender = EmailSender()
    notification_manager = NotificationManager(template_engine, email_sender)

    scheduler = BlockingScheduler()

    # Daily upload reminders (9:00 AM)
    scheduler.add_job(
        notification_manager.trigger_upload_reminders,
        'cron',
        hour=9,
        minute=0,
        id='upload_reminders'
    )

    # Daily SLA breach alerts (10:00 AM)
    scheduler.add_job(
        notification_manager.trigger_sla_breach_alerts,
        'cron',
        hour=10,
        minute=0,
        id='sla_breach_alerts'
    )

    # Weekly summary (Monday 9:00 AM)
    stakeholders = [
        'finance.head@adanigroup.com',
        'cfo@adanigroup.com'
    ]

    scheduler.add_job(
        lambda: notification_manager.trigger_weekly_summary(stakeholders),
        'cron',
        day_of_week='mon',
        hour=9,
        minute=0,
        id='weekly_summary'
    )

    print("Email cron jobs configured:")
    print("- Upload reminders: Daily at 9:00 AM")
    print("- SLA breach alerts: Daily at 10:00 AM")
    print("- Weekly summary: Monday at 9:00 AM")

    scheduler.start()

if __name__ == '__main__':
    setup_email_cron_jobs()
```

**Acceptance Criteria**:
- ✅ Assignment notification triggered on responsibility_matrix insert
- ✅ Upload reminder cron job (daily 9 AM) for accounts approaching deadline
- ✅ SLA breach alert cron job (daily 10 AM) for overdue accounts
- ✅ Weekly summary cron job (Monday 9 AM) for all stakeholders
- ✅ Event-driven notifications for review completion and approval
- ✅ All notifications logged to MongoDB

---

### 5.4 Email Tracking & Analytics

#### **5.4.1 MongoDB Email Logging** 🔴
**Purpose**: Track email delivery status and user engagement.

**Implementation**:
```python
# src/db/mongodb.py - ADD TO EXISTING FILE

def log_email_event(event_data: Dict) -> str:
    """Log email send event to MongoDB."""
    collection = get_mongo_database()['email_logs']
    result = collection.insert_one(event_data)
    return str(result.inserted_id)

def save_notification_log(log_data: Dict) -> str:
    """Log notification trigger to MongoDB."""
    collection = get_mongo_database()['notification_logs']
    result = collection.insert_one(log_data)
    return str(result.inserted_id)

def get_email_stats(start_date: datetime, end_date: datetime) -> Dict:
    """Get email statistics for date range."""
    collection = get_mongo_database()['email_logs']

    pipeline = [
        {
            '$match': {
                'timestamp': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
        },
        {
            '$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }
        }
    ]

    results = list(collection.aggregate(pipeline))

    stats = {
        'sent': 0,
        'failed': 0,
        'total': 0
    }

    for result in results:
        status = result['_id']
        count = result['count']
        stats[status] = count
        stats['total'] += count

    return stats
```

**Acceptance Criteria**:
- ✅ All email sends logged to `email_logs` collection
- ✅ Notification triggers logged to `notification_logs` collection
- ✅ Email statistics aggregation by status and date range
- ✅ Query functions for email history by recipient or account

---

### 5.5 Streamlit UI Integration

#### **5.5.1 Notification Settings Page** 🔴
**Purpose**: Allow users to configure email preferences.

**Implementation**:
```python
# src/dashboards/notification_settings_page.py - CREATE

import streamlit as st
from src.email.notification_manager import NotificationManager

def render_notification_settings_page():
    """Render notification settings page."""
    st.title("📧 Notification Settings")
    st.caption("Configure your email notification preferences")

    # User email preferences
    st.subheader("Email Preferences")

    col1, col2 = st.columns(2)

    with col1:
        enable_assignment = st.checkbox("Assignment Notifications", value=True)
        enable_reminders = st.checkbox("Upload Reminders", value=True)
        enable_completion = st.checkbox("Review Completion", value=True)

    with col2:
        enable_approval = st.checkbox("Approval Notifications", value=True)
        enable_sla_breach = st.checkbox("SLA Breach Alerts", value=True)
        enable_weekly = st.checkbox("Weekly Summary", value=False)

    # Email frequency
    st.subheader("Email Frequency")
    frequency = st.select_slider(
        "Digest Frequency",
        options=['Real-time', 'Hourly', 'Daily', 'Weekly'],
        value='Real-time'
    )

    # Test email
    st.subheader("Test Notifications")
    if st.button("Send Test Email"):
        with st.spinner("Sending test email..."):
            # Send test email logic here
            st.success("✅ Test email sent successfully!")

    # Email history
    st.subheader("Recent Notifications")

    # Mock data - in production, query MongoDB
    history_data = [
        {'date': '2024-03-15', 'type': 'Assignment', 'subject': 'New GL Account Assignment: 101000', 'status': 'Sent'},
        {'date': '2024-03-14', 'type': 'Reminder', 'subject': 'Upload Supporting Documents', 'status': 'Sent'},
        {'date': '2024-03-13', 'type': 'SLA Breach', 'subject': 'URGENT: SLA Breach for 201500', 'status': 'Sent'}
    ]

    st.dataframe(history_data, use_container_width=True)

    # Save settings
    if st.button("Save Settings", type="primary"):
        st.success("✅ Notification settings saved successfully!")
```

**Acceptance Criteria**:
- ✅ User interface for email preference configuration
- ✅ Test email sending capability
- ✅ Email history display from MongoDB
- ✅ Settings persistence to user profile

---

### 5.6 Testing & Performance

**Unit Tests**:
```python
# tests/test_email_system.py - CREATE

def test_template_rendering():
    """Test Jinja2 template rendering with context."""
    pass

def test_email_sending():
    """Test SMTP email delivery (mock server)."""
    pass

def test_notification_triggers():
    """Test event-driven notification logic."""
    pass

def test_bulk_email_rate_limiting():
    """Test bulk email sending with rate limits."""
    pass

def test_email_logging():
    """Test MongoDB email event logging."""
    pass
```

**Performance Benchmarks**:
- Template rendering: <100ms
- Email sending (single): <2 seconds
- Bulk email (100 recipients): <60 seconds (with rate limiting)
- MongoDB logging: <50ms

---

## Part 5 Status Summary
Coverage: Complete email automation system with Jinja2 template engine (6 templates), SMTP email sender with retry logic, event-driven notification manager (6 trigger types), cron job scheduling, MongoDB tracking, Streamlit settings UI, and testing strategy.

---

# VI. Overall Testing & Integration Strategy

## 6.1 Comprehensive Testing Framework

### 6.1.1 Unit Testing Strategy 🔴
**Coverage Target**: ≥80% across all modules

**Test Organization**:
```
tests/
├── unit/
│   ├── test_analytics.py           # Analytics calculations
│   ├── test_insights.py            # Insights generation
│   ├── test_visualizations.py      # Chart generation
│   ├── test_ml_model.py           # ML training & prediction
│   ├── test_rag_pipeline.py       # RAG retrieval & generation
│   ├── test_email_system.py       # Email sending & templates
│   └── test_db_operations.py     # Database CRUD
├── integration/
│   ├── test_data_pipeline.py      # CSV → PostgreSQL → MongoDB
│   ├── test_review_workflow.py    # End-to-end review process
│   ├── test_agent_tools.py        # LangChain agent routing
│   └── test_report_generation.py # Report → PDF/Excel export
├── e2e/
│   ├── test_streamlit_flows.py    # UI user journeys
│   └── test_email_workflows.py   # Notification delivery
└── fixtures/
    ├── sample_data.py             # Test data generators
    └── mock_responses.py          # API mocks
```

**Critical Test Cases**:
```python
# tests/unit/test_analytics.py - ENHANCED

import pytest
from src.analytics import (
    calculate_variance_analysis,
    calculate_gl_hygiene_score,
    calculate_review_status_summary
)

class TestVarianceAnalysis:
    """Test variance calculation logic."""

    def test_variance_calculation_with_growth(self):
        """Test positive variance (revenue growth)."""
        result = calculate_variance_analysis(
            entity='ABEX',
            current_period='2024-03',
            compare_period='2024-02'
        )

        assert 'variance_summary' in result
        assert result['variance_pct'] >= 0
        assert result['total_accounts'] > 0

    def test_variance_calculation_with_decline(self):
        """Test negative variance (expense reduction)."""
        # Mock data with declining balance
        pass

    def test_variance_significant_accounts(self):
        """Test identification of accounts with >10% variance."""
        result = calculate_variance_analysis(
            entity='ABEX',
            current_period='2024-03',
            compare_period='2024-02'
        )

        significant = result.get('significant_accounts', [])
        for account in significant:
            assert abs(account['variance_pct']) >= 10

class TestGLHygieneScore:
    """Test hygiene scoring algorithm."""

    def test_hygiene_score_perfect(self):
        """Test hygiene score for fully compliant entity."""
        # Mock: All accounts reviewed, docs uploaded, no SLA breaches
        result = calculate_gl_hygiene_score(entity='ABEX', period='2024-03')
        assert result['overall_score'] >= 90
        assert result['grade'] in ['A', 'A+']

    def test_hygiene_score_poor(self):
        """Test hygiene score for non-compliant entity."""
        # Mock: Missing docs, overdue reviews, SLA breaches
        result = calculate_gl_hygiene_score(entity='TEST', period='2024-03')
        assert result['overall_score'] < 60
        assert result['grade'] in ['D', 'F']

    def test_hygiene_score_components(self):
        """Test individual component scores."""
        result = calculate_gl_hygiene_score(entity='ABEX', period='2024-03')

        components = result['components']
        assert 'review_completion' in components
        assert 'documentation_completeness' in components
        assert 'sla_compliance' in components
        assert 'variance_resolution' in components

class TestReviewStatusSummary:
    """Test review status aggregation."""

    def test_status_summary_aggregation(self):
        """Test correct counting of review statuses."""
        result = calculate_review_status_summary(entity='ABEX', period='2024-03')

        overall = result['overall']
        assert overall['total_accounts'] == (
            overall['reviewed'] + overall['pending'] + overall['flagged']
        )

    def test_status_summary_by_criticality(self):
        """Test grouping by criticality levels."""
        result = calculate_review_status_summary(entity='ABEX', period='2024-03')

        by_criticality = result['by_criticality']
        assert 'Critical' in by_criticality
        assert 'High' in by_criticality
```

```python
# tests/integration/test_review_workflow.py - CREATE

import pytest
from datetime import datetime, timedelta

class TestEndToEndReviewWorkflow:
    """Test complete review workflow from assignment to approval."""

    @pytest.mark.integration
    def test_complete_review_cycle(self, db_session, test_user):
        """
        Test full review workflow:
        1. Assign GL account to reviewer
        2. Reviewer uploads supporting docs
        3. Reviewer marks as reviewed
        4. Approver approves account
        5. Verify audit trail
        """
        # Step 1: Create assignment
        from src.db.postgres import create_responsibility_assignment

        assignment = create_responsibility_assignment(
            db_session,
            user_id=test_user.id,
            account_code='101000',
            entity='ABEX',
            review_deadline=datetime.utcnow() + timedelta(days=5)
        )

        assert assignment.id is not None

        # Step 2: Upload supporting doc
        from src.db.mongodb import save_supporting_document

        doc_id = save_supporting_document({
            'account_code': '101000',
            'entity': 'ABEX',
            'period': '2024-03',
            'file_name': 'bank_reconciliation.pdf',
            'file_type': 'pdf',
            'uploaded_by': test_user.email,
            'uploaded_at': datetime.utcnow()
        })

        assert doc_id is not None

        # Step 3: Mark as reviewed
        from src.db.postgres import update_gl_account_status

        updated = update_gl_account_status(
            db_session,
            account_code='101000',
            entity='ABEX',
            review_status='Reviewed',
            reviewed_by=test_user.email
        )

        assert updated.review_status == 'Reviewed'

        # Step 4: Approve
        approved = update_gl_account_status(
            db_session,
            account_code='101000',
            entity='ABEX',
            approval_status='Approved',
            approved_by='approver@adanigroup.com'
        )

        assert approved.approval_status == 'Approved'

        # Step 5: Verify audit trail
        from src.db.mongodb import get_audit_trail

        audit_logs = get_audit_trail(
            account_code='101000',
            entity='ABEX',
            period='2024-03'
        )

        assert len(audit_logs) >= 4  # Assignment, upload, review, approval

        # Verify events
        events = [log['event_type'] for log in audit_logs]
        assert 'assignment_created' in events
        assert 'document_uploaded' in events
        assert 'status_updated' in events
```

```python
# tests/e2e/test_streamlit_flows.py - CREATE

import pytest
from unittest.mock import Mock, patch

class TestStreamlitUserJourneys:
    """Test complete user journeys in Streamlit app."""

    @pytest.mark.e2e
    def test_reviewer_dashboard_flow(self):
        """
        Test reviewer user journey:
        1. Login
        2. View assigned accounts
        3. Select account for review
        4. Upload supporting doc
        5. Mark as reviewed
        """
        # Mock Streamlit session state
        # Simulate page navigation
        # Verify UI components render correctly
        pass

    @pytest.mark.e2e
    def test_analytics_dashboard_flow(self):
        """
        Test analytics viewing:
        1. Navigate to Financial Dashboard
        2. Select entity and period
        3. View variance charts
        4. Download report as PDF
        """
        pass

    @pytest.mark.e2e
    def test_ai_assistant_flow(self):
        """
        Test conversational AI:
        1. Navigate to AI Assistant page
        2. Ask question about GL account
        3. Verify RAG retrieval
        4. Verify response with sources
        """
        pass
```

**Test Execution**:
```bash
# Run all tests
pytest tests/ -v --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run integration tests (requires DB)
pytest tests/integration/ -v -m integration

# Run E2E tests
pytest tests/e2e/ -v -m e2e

# Run with coverage threshold enforcement
pytest tests/ --cov=src --cov-fail-under=80
```

---

### 6.1.2 Integration Testing 🔴
**Focus**: Cross-module interactions and data flow

**Key Integration Points**:
```yaml
Integration Test Scenarios:
  1. Data Ingestion Pipeline
     - CSV upload → PostgreSQL insert → MongoDB audit log
     - Verify data consistency across stores
     - Test rollback on failure

  2. ML Model Training → Inference
     - Feature extraction from PostgreSQL
     - Model training with MLflow tracking
     - Prediction endpoint integration
     - Feedback loop → Retraining

  3. RAG Query → Agent → Database
     - User query → Vector store retrieval
     - Agent tool selection → DB query
     - Response generation → UI display

  4. Review Workflow → Email Notifications
     - Assignment creation → Email sent
     - SLA breach → Alert triggered
     - Review completion → Notification to stakeholders

  5. Report Generation → Export
     - Analytics calculation → Report rendering
     - PDF generation with charts
     - Excel export with formulas
     - Email delivery with attachments
```

**Sample Integration Test**:
```python
# tests/integration/test_data_pipeline.py - CREATE

import pytest
from pathlib import Path
import pandas as pd

class TestDataIngestionPipeline:
    """Test CSV → PostgreSQL → MongoDB pipeline."""

    @pytest.mark.integration
    def test_csv_to_postgres_ingestion(self, db_session, sample_csv_path):
        """Test complete data ingestion flow."""
        from src.data_ingestion import ingest_trial_balance_csv
        from src.db.postgres import get_all_gl_accounts

        # Ingest CSV
        result = ingest_trial_balance_csv(sample_csv_path, entity='TEST', period='2024-03')

        assert result['status'] == 'success'
        assert result['records_inserted'] > 0

        # Verify PostgreSQL insertion
        accounts = get_all_gl_accounts(db_session, entity='TEST', period='2024-03')
        assert len(accounts) == result['records_inserted']

        # Verify MongoDB audit log
        from src.db.mongodb import get_audit_trail

        audit_logs = get_audit_trail(entity='TEST', period='2024-03')
        assert len(audit_logs) > 0
        assert any(log['event_type'] == 'data_ingestion' for log in audit_logs)

    @pytest.mark.integration
    def test_ingestion_validation_failure_rollback(self, db_session, invalid_csv_path):
        """Test rollback on validation failure."""
        from src.data_ingestion import ingest_trial_balance_csv

        # Attempt to ingest invalid CSV
        result = ingest_trial_balance_csv(invalid_csv_path, entity='TEST', period='2024-03')

        assert result['status'] == 'failed'
        assert 'validation_errors' in result

        # Verify no partial data committed
        from src.db.postgres import get_all_gl_accounts
        accounts = get_all_gl_accounts(db_session, entity='TEST', period='2024-03')
        assert len(accounts) == 0  # Rollback successful
```

---

### 6.1.3 Performance Testing 🟡
**Goal**: Ensure system meets performance benchmarks

**Performance Test Cases**:
```python
# tests/performance/test_benchmarks.py - CREATE

import pytest
import time
from memory_profiler import profile

class TestPerformanceBenchmarks:
    """Test system performance against defined benchmarks."""

    @pytest.mark.performance
    def test_analytics_calculation_speed(self, db_session):
        """Benchmark: Analytics calculation <3 seconds."""
        from src.analytics import calculate_variance_analysis

        start_time = time.time()

        result = calculate_variance_analysis(
            entity='ABEX',
            current_period='2024-03',
            compare_period='2024-02'
        )

        elapsed = time.time() - start_time

        assert elapsed < 3.0  # Must complete in <3 seconds
        assert result is not None

    @pytest.mark.performance
    def test_chart_rendering_speed(self):
        """Benchmark: Chart rendering <2 seconds."""
        from src.visualizations import create_variance_waterfall_chart
        import pandas as pd

        # Generate test data
        data = pd.DataFrame({
            'category': ['Revenue', 'COGS', 'OpEx', 'Net Income'],
            'value': [1000000, -600000, -200000, 200000]
        })

        start_time = time.time()

        fig = create_variance_waterfall_chart(data, 'Test Chart')

        elapsed = time.time() - start_time

        assert elapsed < 2.0  # Must render in <2 seconds
        assert fig is not None

    @pytest.mark.performance
    def test_rag_query_speed(self, rag_pipeline):
        """Benchmark: RAG query response <3 seconds."""
        start_time = time.time()

        response = rag_pipeline.query("What is a trial balance?")

        elapsed = time.time() - start_time

        assert elapsed < 3.0  # Must respond in <3 seconds
        assert 'answer' in response

    @pytest.mark.performance
    @profile
    def test_ml_training_memory_usage(self, sample_training_data):
        """Benchmark: ML training memory <2GB."""
        from src.ml_model import train_and_log_model

        # Train model and monitor memory
        model = train_and_log_model(sample_training_data)

        assert model is not None
        # Memory profiler will report peak usage

    @pytest.mark.performance
    def test_report_generation_speed(self):
        """Benchmark: Report generation <5 seconds."""
        from src.reports import GLAccountStatusReport

        start_time = time.time()

        report = GLAccountStatusReport(entity='ABEX', period='2024-03')
        pdf_bytes = report.generate_pdf()

        elapsed = time.time() - start_time

        assert elapsed < 5.0  # Must generate in <5 seconds
        assert len(pdf_bytes) > 0
```

**Load Testing** (using Locust):
```python
# tests/performance/locustfile.py - CREATE

from locust import HttpUser, task, between

class StreamlitUser(HttpUser):
    """Simulate concurrent Streamlit users."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    @task(3)
    def view_dashboard(self):
        """Load overview dashboard."""
        self.client.get("/")

    @task(2)
    def view_analytics(self):
        """Load financial analytics page."""
        self.client.get("/?page=Financial_Dashboard")

    @task(1)
    def query_ai_assistant(self):
        """Ask AI assistant a question."""
        self.client.post("/ai_assistant", json={
            'query': 'What is the hygiene score for ABEX?'
        })

# Run: locust -f tests/performance/locustfile.py --host=http://localhost:8501
```

---

## 6.2 Integration Points & Dependencies

### 6.2.1 Module Dependency Map 🔴

```yaml
Module Dependencies:
  src/data_ingestion.py:
    - Depends on: src/db/postgres.py, src/db/mongodb.py, src/db/storage.py
    - Used by: Streamlit upload page, CLI scripts
    - Integration: CSV → PostgreSQL (gl_accounts) → MongoDB (audit_trail)

  src/data_validation.py:
    - Depends on: src/db/postgres.py, Great Expectations
    - Used by: data_ingestion.py, analytics.py
    - Integration: PostgreSQL → GX validation → MongoDB (validation_results)

  src/analytics.py:
    - Depends on: src/db/postgres.py
    - Used by: visualizations.py, reports.py, agent.py
    - Integration: PostgreSQL queries → Analytics calculations → Parquet cache

  src/insights.py:
    - Depends on: src/analytics.py, src/db/postgres.py
    - Used by: visualizations.py, reports.py
    - Integration: Analytics → Insight generation → Dashboard display

  src/visualizations.py:
    - Depends on: src/analytics.py, src/insights.py
    - Used by: app.py (Streamlit dashboards)
    - Integration: Analytics/Insights → Plotly charts → Streamlit rendering

  src/ml_model.py:
    - Depends on: src/db/postgres.py, MLflow
    - Used by: agent.py, feedback_handler.py
    - Integration: PostgreSQL features → Model training → MLflow tracking → Predictions

  src/vector_store.py:
    - Depends on: ChromaDB, sentence-transformers
    - Used by: rag_pipeline.py, agent.py
    - Integration: Documents → Embeddings → ChromaDB → Semantic search

  src/rag/rag_pipeline.py:
    - Depends on: vector_store.py, LangChain, Gemini API
    - Used by: agent.py, app.py (AI Assistant page)
    - Integration: Query → Vector store retrieval → LLM generation → Response

  src/agent.py:
    - Depends on: rag_pipeline.py, analytics.py, ml_model.py, db/postgres.py
    - Used by: app.py (AI Assistant page)
    - Integration: User query → Tool selection → Data retrieval → Response

  src/email/notification_manager.py:
    - Depends on: template_engine.py, email_sender.py, db/postgres.py, db/mongodb.py
    - Used by: app.py (workflow triggers), cron jobs
    - Integration: Event trigger → Template render → SMTP send → MongoDB log

  src/reports/:
    - Depends on: analytics.py, insights.py, visualizations.py
    - Used by: app.py (report generation page), email attachments
    - Integration: Analytics → Report rendering → PDF/Excel export → Email/download

  src/app.py:
    - Depends on: ALL modules (orchestrator)
    - Entry point for Streamlit UI
    - Integration: User interactions → Module calls → UI updates
```

### 6.2.2 Database Integration Matrix 🔴

```yaml
PostgreSQL Tables:
  gl_accounts:
    - Written by: data_ingestion.py, app.py (status updates)
    - Read by: analytics.py, insights.py, ml_model.py, agent.py, reports.py
    - Indexes: (account_code, entity, period), (criticality), (review_status)

  responsibility_matrix:
    - Written by: app.py (assignment page), notification_manager.py
    - Read by: app.py (reviewer dashboard), agent.py, email notifications
    - Foreign Keys: user_id → users.id

  users:
    - Written by: app.py (user management)
    - Read by: All modules (authentication, assignment)
    - Indexes: (email), (department)

  master_chart_of_accounts:
    - Written by: data_ingestion.py (initial load)
    - Read by: data_validation.py (account code validation), app.py
    - Static reference data

MongoDB Collections:
  supporting_docs:
    - Written by: app.py (document upload)
    - Read by: app.py (document viewer), reports.py, agent.py
    - Indexes: (account_code, entity, period)

  audit_trail:
    - Written by: ALL modules (log_audit_event)
    - Read by: app.py (audit log viewer), reports.py
    - Indexes: (account_code, timestamp), (user_email)

  validation_results:
    - Written by: data_validation.py
    - Read by: analytics.py (hygiene score), reports.py
    - Indexes: (gl_code, period)

  email_logs:
    - Written by: email_sender.py
    - Read by: app.py (notification settings page), analytics
    - Indexes: (recipient, timestamp), (status)

  review_sessions:
    - Written by: agent.py, rag_pipeline.py
    - Read by: ml_model.py (feedback learning), analytics
    - Indexes: (session_id, user_email)

File System:
  data/raw/:
    - Written by: data_ingestion.py (CSV storage)
    - Read by: data_ingestion.py (reprocessing)

  data/processed/:
    - Written by: analytics.py (Parquet cache)
    - Read by: analytics.py, visualizations.py (fast loading)

  data/supporting_docs/:
    - Written by: app.py (file upload)
    - Read by: app.py (file download), reports.py (attachment)

  data/vectors/chromadb/:
    - Written by: vector_store_manager.py (embeddings)
    - Read by: rag_pipeline.py (semantic search)
```

---

## 6.3 Deployment Checklist

### 6.3.1 Pre-Deployment Tasks 🔴

```yaml
Environment Setup:
  ✅ 1. Database Initialization
     - Run scripts/init-postgres.sql
     - Create MongoDB collections with indexes
     - Verify connectivity from app

  ✅ 2. Environment Variables
     - PostgreSQL: POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
     - MongoDB: MONGO_URI
     - APIs: GOOGLE_API_KEY (Gemini), SMTP credentials
     - App: APP_URL, SECRET_KEY

  ✅ 3. Dependencies Installation
     - conda env update -f environment.yml --prune
     - Verify all packages installed: pip list

  ✅ 4. Data Seeding
     - python scripts/seed_sample_data.py
     - Verify 24+ test records in PostgreSQL
     - Load master chart of accounts (2736 entries)

  ✅ 5. Vector Store Initialization
     - python scripts/init_vector_store.py
     - Load documentation embeddings (200-500 chunks)
     - Verify ChromaDB collection counts

Code Quality:
  ✅ 6. Linting & Formatting
     - make lint (ruff check)
     - make format (black + isort)
     - Fix all linting errors

  ✅ 7. Type Checking
     - make type-check (mypy --strict)
     - Resolve type errors

  ✅ 8. Security Scan
     - pip-audit (check for vulnerable packages)
     - bandit -r src/ (security linting)
     - Review secrets exposure

Testing:
  ✅ 9. Unit Tests
     - pytest tests/unit/ -v
     - Coverage ≥80%

  ✅ 10. Integration Tests
     - pytest tests/integration/ -v -m integration
     - All DB integrations passing

  ✅ 11. E2E Tests
     - pytest tests/e2e/ -v -m e2e
     - All user flows working

Performance:
  ✅ 12. Performance Benchmarks
     - pytest tests/performance/ -v -m performance
     - All benchmarks met (<3s analytics, <2s charts, <5s reports)

  ✅ 13. Load Testing
     - locust -f tests/performance/locustfile.py
     - 50 concurrent users, <5s response time

Documentation:
  ✅ 14. API Documentation
     - Generate API docs: pdoc3 --html src/
     - Review completeness

  ✅ 15. User Guide
     - Update README.md with usage instructions
     - Create demo video / screenshots

  ✅ 16. Deployment Guide
     - Document infrastructure requirements
     - Provide step-by-step deployment steps
```

### 6.3.2 Deployment Steps 🔴

```bash
# Step 1: Clone repository
git clone https://github.com/ksawesome/finnovate-hackathon.git
cd finnovate-hackathon

# Step 2: Create conda environment
conda env update -f environment.yml --prune
conda activate finnovate-hackathon

# Step 3: Set environment variables (create .env file)
cat > .env << EOF
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=finnovate
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_password

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=finnovate

# APIs
GOOGLE_API_KEY=your_gemini_api_key

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=projectaura@adanigroup.com

# App
APP_URL=http://localhost:8501
SECRET_KEY=your_secret_key_here
EOF

# Step 4: Initialize databases
.\scripts\local_db_setup.ps1  # Windows
# OR
bash scripts/local_db_setup.sh  # Linux/Mac

# Step 5: Seed sample data
python scripts/seed_sample_data.py

# Step 6: Initialize vector store
python scripts/init_vector_store.py

# Step 7: Run tests
pytest tests/ -v --cov=src --cov-fail-under=80

# Step 8: Start application
streamlit run src/app.py --server.port=8501

# Step 9: Start email cron jobs (separate terminal)
python scripts/email_cron_jobs.py
```

### 6.3.3 Production Deployment (Optional) 🟡

```yaml
Infrastructure:
  - Hosting: Azure VM / AWS EC2 (4 vCPU, 16GB RAM)
  - PostgreSQL: Azure Database for PostgreSQL (General Purpose tier)
  - MongoDB: MongoDB Atlas (M10 cluster)
  - Storage: Azure Blob Storage / AWS S3 for supporting docs
  - Reverse Proxy: Nginx with SSL (Let's Encrypt)

Docker Deployment:
  - docker-compose up -d
  - Services: app, postgres, mongodb, nginx
  - Volumes: data/, logs/, vectors/
  - Networks: app-network (internal)

Monitoring:
  - Application: Streamlit Cloud metrics
  - Databases: Azure Monitor / AWS CloudWatch
  - Logs: Centralized logging (ELK Stack / Azure Monitor)
  - Alerts: Email/SMS on errors, downtime

Backup Strategy:
  - PostgreSQL: Daily automated backups (7-day retention)
  - MongoDB: Continuous backup with point-in-time recovery
  - File System: Daily snapshots to cloud storage
  - Vector Store: Weekly backups of ChromaDB data/
```

---

## 6.4 Timeline & Task Breakdown

### 6.4.1 Day 2 Execution Plan (8-10 hours) 🔴

```yaml
Phase 2A: Morning Session (4 hours) - Part 0 & Part 1
  08:00 - 08:30 (30 min): Gap Closure Preparation
    - Review Phase 1 completion status
    - Set up development environment
    - Pull latest code from git

  08:30 - 10:00 (90 min): Analytics & Insights Enhancement
    - Implement calculate_variance_analysis() (45 min)
    - Implement calculate_gl_hygiene_score() (45 min)
    - Unit tests for analytics functions (30 min)

  10:00 - 11:00 (60 min): Report Generation System
    - Create GLAccountStatusReport class (30 min)
    - Create VarianceAnalysisReport class (30 min)
    - Test PDF generation (15 min)

  11:00 - 12:00 (60 min): Visualization Enhancement
    - Implement 5 new chart types (waterfall, gauge, sunburst, gantt, heatmap)
    - Each chart: 12 min
    - Test rendering performance

Phase 2B: Afternoon Session (4 hours) - Part 2 & Part 3
  13:00 - 14:00 (60 min): Streamlit Dashboard Pages
    - Create Overview Dashboard (20 min)
    - Create Financial Dashboard (20 min)
    - Create Review Progress Dashboard (20 min)

  14:00 - 15:00 (60 min): ML Feature Engineering
    - Implement GLFeatureEngineer class (30 min)
    - Extract 30 features from GL data (30 min)
    - Test feature extraction

  15:00 - 16:00 (60 min): ML Model Training
    - Implement MLModelTrainer class (20 min)
    - Train anomaly detector (15 min)
    - Train priority classifier (15 min)
    - Log to MLflow (10 min)

  16:00 - 17:00 (60 min): Continual Learning Pipeline
    - Implement feedback collection UI (20 min)
    - Create ContinualLearningPipeline class (25 min)
    - Test retraining with feedback (15 min)

Phase 2C: Evening Session (2 hours) - Part 4 & Part 5 (if time permits)
  17:00 - 18:00 (60 min): RAG System
    - Initialize ChromaDB vector store (15 min)
    - Load documentation embeddings (15 min)
    - Implement RAG pipeline (30 min)

  18:00 - 19:00 (60 min): Email Automation
    - Create email templates (20 min)
    - Implement EmailSender class (20 min)
    - Configure notification triggers (20 min)

Phase 2D: Final Tasks (1 hour)
  19:00 - 19:30 (30 min): Integration & Testing
    - Run full test suite
    - Fix critical bugs
    - Verify all features work end-to-end

  19:30 - 20:00 (30 min): Documentation & Demo Prep
    - Update README with new features
    - Create demo script
    - Commit and push to GitHub
```

### 6.4.2 Priority Matrix 🔴

```yaml
Critical Path (Must Have for Demo):
  🔴 HIGH PRIORITY:
    - Part 0: Gap Closure (Analytics, Insights, Visualizations) - 2 hours
    - Part 1: Report Generation (Status Report, Variance Report) - 1.5 hours
    - Part 2: Dashboard Pages (Overview, Financial, Review Progress) - 1.5 hours
    - Part 3: ML Learning Loop (Feature engineering, Model training) - 2 hours
    - Testing & Integration - 1 hour
    Total: 8 hours (fits within Day 2)

  🟡 MEDIUM PRIORITY:
    - Part 1: Additional Reports (Hygiene, SLA, Executive Summary) - 1 hour
    - Part 2: Advanced Charts (Radar, Trend, Export capabilities) - 1 hour
    - Part 3: Feedback UI & Continual Learning - 1 hour
    Total: 3 hours (if time permits)

  🟢 LOW PRIORITY (Nice to Have):
    - Part 4: RAG & Vector Store - 2 hours
    - Part 5: Email Automation - 2 hours
    Total: 4 hours (Day 3 overflow or skip for hackathon)

Fallback Strategy:
  - If running behind: Focus on HIGH priority items only
  - If ahead of schedule: Add MEDIUM priority items
  - Email automation: Can demonstrate manually instead of automated triggers
  - RAG system: Can use simple Q&A without vector store
```

---

## 6.5 Success Metrics & KPIs

### 6.5.1 Technical Metrics 🔴

```yaml
Code Quality:
  ✅ Test Coverage: ≥80%
  ✅ Linting Errors: 0 (ruff)
  ✅ Type Coverage: ≥70% (mypy)
  ✅ Security Issues: 0 critical (bandit)

Performance:
  ✅ Page Load Time: <3 seconds (Streamlit pages)
  ✅ Chart Rendering: <2 seconds (Plotly visualizations)
  ✅ Analytics Calculation: <3 seconds (variance, hygiene score)
  ✅ Report Generation: <5 seconds (PDF/Excel export)
  ✅ RAG Query Response: <3 seconds (end-to-end)
  ✅ ML Inference: <500ms (single prediction)

Scalability:
  ✅ Concurrent Users: 50 users, <5s response time
  ✅ Database Queries: <100ms (indexed queries)
  ✅ File Upload: 10MB files, <10s processing
  ✅ Email Sending: 100 emails/hour (rate limited)

Reliability:
  ✅ Uptime: 99.5% (during hackathon demo period)
  ✅ Error Rate: <1% (exceptions handled gracefully)
  ✅ Data Consistency: 100% (no data loss or corruption)
```

### 6.5.2 Business Metrics 🔴

```yaml
Feature Completeness:
  ✅ Phase 0 Gaps Closed: 7/7 (100%)
  ✅ Report Types: 6 (Status, Variance, Hygiene, Reviewer Perf, SLA, Executive)
  ✅ Dashboard Pages: 5 (Overview, Financial, Review, Quality, Risk)
  ✅ Chart Types: 13 (Waterfall, Gauge, Sunburst, Gantt, Heatmap, etc.)
  ✅ ML Models: 3 (Anomaly detection, Priority classification, Attention classification)
  ✅ Email Templates: 6 (Assignment, Reminder, Completion, Approval, Breach, Summary)

User Experience:
  ✅ Navigation: Intuitive multi-page Streamlit app
  ✅ Responsiveness: All pages load <3s
  ✅ Error Handling: User-friendly error messages
  ✅ Help System: AI Assistant for natural language queries
  ✅ Accessibility: Clear labels, proper contrast, keyboard navigation

Data Quality:
  ✅ Trial Balance Validation: 100% accuracy (must balance to nil)
  ✅ GL Hygiene Score: >80 for compliant entities
  ✅ Variance Detection: Flags accounts with >10% variance
  ✅ SLA Compliance: Tracks deadline adherence

Innovation & Differentiation:
  ✅ AI-Powered Insights: ML-driven anomaly detection and priority scoring
  ✅ Conversational Interface: RAG-powered Q&A for accounting queries
  ✅ Automated Workflows: Email notifications, report generation, review assignments
  ✅ Tri-Store Architecture: Optimized storage for structured, semi-structured, and unstructured data
  ✅ Continual Learning: ML models improve with user feedback
```

### 6.5.3 Demo Success Criteria 🔴

```yaml
Demo Storyline (10-15 minutes):
  Act 1: Problem Statement (2 min)
    - Show complexity: 1,000+ entities, 501 GL accounts
    - Manual review pain points: SLA breaches, missing docs, no insights

  Act 2: System Walkthrough (8 min)
    Scene 1: Data Ingestion & Validation (1.5 min)
      ✅ Upload trial balance CSV
      ✅ Automatic validation with Great Expectations
      ✅ Data stored across PostgreSQL, MongoDB, Parquet

    Scene 2: Interactive Dashboards (2 min)
      ✅ Overview Dashboard: 501 accounts, 375 reviewed, hygiene score 82
      ✅ Financial Dashboard: Variance waterfall chart, period comparison
      ✅ Review Progress: SLA compliance gauge, overdue alerts

    Scene 3: Automated Reports (1.5 min)
      ✅ Generate GL Status Report (PDF download)
      ✅ Variance Analysis Report with charts
      ✅ Executive Summary with actionable insights

    Scene 4: AI-Powered Features (2 min)
      ✅ ML anomaly detection: Flag suspicious account balances
      ✅ Priority scoring: Rank accounts by review urgency
      ✅ Attention classifier: Predict accounts needing deep review

    Scene 5: Conversational AI Assistant (1 min)
      ✅ Ask: "What is the hygiene score for ABEX in March 2024?"
      ✅ Ask: "Which accounts have significant variance?"
      ✅ Show RAG retrieval with source citations

  Act 3: Competitive Advantages (2 min)
    ✅ State-of-the-Art Tech Stack: Gemini AI, ChromaDB, MLflow, Great Expectations
    ✅ Production-Ready: 80%+ test coverage, performance benchmarks met
    ✅ Scalable Architecture: Tri-store design, async processing
    ✅ User-Centric: Intuitive UI, helpful AI assistant, automated workflows

  Act 4: Q&A (3-5 min)
    ✅ Technical questions: Answer with confidence
    ✅ Business value: Emphasize time savings, error reduction, compliance
    ✅ Future roadmap: Mention extensibility to other Adani Group processes

Judging Criteria Alignment:
  ✅ Innovation: RAG-powered AI, continual learning ML, tri-store architecture
  ✅ Technical Excellence: 80%+ test coverage, <3s page loads, production-ready code
  ✅ Business Impact: Automates manual review, reduces SLA breaches, improves hygiene
  ✅ Completeness: All 5 parts implemented (or HIGH priority items complete)
  ✅ Presentation: Clear demo flow, confident delivery, answers all questions
```

---

# VII. Conclusion & Next Steps

## Summary of Phase 2 Implementation Plan

This comprehensive Phase 2 Implementation Plan covers **5 major parts** with **60+ detailed components**:

### Part 0: Phase 1 Gap Closure
- ✅ 7 gap categories identified and prioritized
- ✅ Analytics enhancement (variance, hygiene scoring, review status)
- ✅ Insights generation (anomalies, trends, recommendations)
- ✅ Visualization expansion (13 chart types)
- ✅ Streamlit app completion (7 pages)
- ✅ Unit tests and documentation

### Part 1: Automated Report Generation
- ✅ 6 report types: Status, Variance Analysis, GL Hygiene, Reviewer Performance, SLA Compliance, Executive Summary
- ✅ Multi-format export: PDF (ReportLab), Excel (openpyxl), CSV
- ✅ Report orchestration engine with scheduling
- ✅ Email delivery with attachments
- ✅ Performance: <5s generation time

### Part 2: Interactive Visualization & Dashboard
- ✅ 5 dashboard pages: Overview, Financial, Review Progress, Quality Metrics, Risk Analysis
- ✅ 13 Plotly chart types: Waterfall, Gauge, Sunburst, Gantt, Heatmap, Radar, Trend, Pie, Bar, Scatter, Line, Table, Export
- ✅ Drill-down capabilities and filters (entity, period, department)
- ✅ Real-time data refresh
- ✅ Performance: <3s page load, <2s chart rendering

### Part 3: ML Learning Loop
- ✅ Feature engineering: 30 features from GL data (temporal, statistical, contextual, metadata)
- ✅ 3 production models: Anomaly detection (Isolation Forest), Priority classification (XGBoost), Attention classification (Gradient Boosting)
- ✅ MLflow experiment tracking with hyperparameter tuning
- ✅ Feedback collection UI (thumbs up/down, text feedback)
- ✅ Continual learning pipeline with safety rails and rollback
- ✅ Performance: R² > 0.6, Accuracy > 75%, ROC-AUC > 0.80

### Part 4: RAG & Vector Store
- ✅ Document processing: 200-500 chunks from 4 sources (docs, accounting knowledge, GL metadata, historical)
- ✅ ChromaDB vector store with sentence-transformers embeddings (384 dims)
- ✅ RAG pipeline: Query → Retrieval → Generation with Gemini 1.5 Flash
- ✅ Enhanced LangChain agent with 4 structured tools (RAG Query, GL Lookup, Analytics, Assignment)
- ✅ Conversational UI in Streamlit with chat history
- ✅ Performance: <500ms retrieval, <3s RAG response

### Part 5: Email Automation System
- ✅ Jinja2 template engine with 6 templates (Assignment, Reminder, Completion, Approval, Breach, Summary)
- ✅ SMTP email sender with retry logic (3 attempts, exponential backoff)
- ✅ Event-driven notification manager (6 trigger types)
- ✅ Cron job scheduling with APScheduler (daily/weekly)
- ✅ MongoDB tracking (email_logs, notification_logs)
- ✅ Streamlit settings UI for user preferences
- ✅ Performance: <100ms rendering, <2s sending, <60s bulk (100 emails)

## Implementation Readiness

**Code Artifacts Provided**:
- ✅ 40+ complete Python classes with docstrings
- ✅ 20+ database functions (PostgreSQL + MongoDB)
- ✅ 13 chart implementations with Plotly
- ✅ 6 HTML email templates with styling
- ✅ 30+ unit test templates
- ✅ Cron job configuration scripts
- ✅ Deployment checklists and commands

**Total Lines of Code**: ~6,500+ lines of implementation-ready specifications

**Estimated Development Time**: 8-10 hours (fits within Day 2 of 6-day plan)

## Competitive Advantages

1. **State-of-the-Art Technology Stack**
   - Gemini 1.5 Flash for LLM
   - ChromaDB for vector store
   - MLflow for ML tracking
   - Great Expectations for data validation
   - Plotly for interactive visualizations

2. **Production-Ready Quality**
   - 80%+ test coverage
   - Performance benchmarks met
   - Error handling and retry logic
   - Comprehensive logging and monitoring

3. **User-Centric Design**
   - Intuitive multi-page Streamlit app
   - Conversational AI assistant
   - Automated workflows and notifications
   - Real-time dashboards and reports

4. **Scalable Architecture**
   - Tri-store design (PostgreSQL, MongoDB, File System)
   - Async processing and caching
   - Microservices-ready (Docker support)
   - Cloud-native deployment options

## Final Recommendations

### For Hackathon Demo:
1. **Focus on HIGH priority items** (Parts 0-3): 8 hours
2. **Implement critical features first**: Analytics, Reports, Dashboards, ML
3. **Demo storyline**: Problem → Solution → AI Features → Competitive Edge
4. **Backup plan**: If time-constrained, skip Email (Part 5) or simplify RAG (Part 4)

### For Production Deployment:
1. **Complete all 5 parts**: Allocate 2-3 days
2. **Security hardening**: Secrets management, RBAC, audit logs
3. **Infrastructure setup**: Azure/AWS, managed databases, monitoring
4. **User training**: Create documentation, video tutorials, onboarding guide

### For Post-Hackathon Development:
1. **Mobile app**: React Native frontend for on-the-go reviews
2. **Advanced analytics**: Predictive forecasting, anomaly trends over time
3. **Integration**: SAP/Oracle ERP connectors, Power BI dashboards
4. **Multi-tenancy**: Support for multiple Adani Group entities with isolated data

---

**Document Metadata**:
- **Title**: Phase 2 Implementation Plan - Project Aura
- **Author**: AI Assistant (with human oversight)
- **Date**: Day 1 → Day 2 Transition
- **Version**: 1.0 (Complete)
- **Status**: Ready for Execution ✅

**GitHub Commit Message**:
```
feat: Complete Phase 2 Implementation Plan (Parts 0-5)

- Part 0: Gap Closure with 7 categories
- Part 1: Report Generation (6 types, PDF/Excel export)
- Part 2: Dashboards & Visualizations (5 pages, 13 charts)
- Part 3: ML Learning Loop (30 features, 3 models, continual learning)
- Part 4: RAG & Vector Store (ChromaDB, semantic search, AI assistant)
- Part 5: Email Automation (6 templates, SMTP, cron jobs)
- Testing Strategy: Unit, Integration, E2E, Performance
- Deployment Guide: Local and production setup
- Timeline: 8-10 hour execution plan for Day 2

Ready for implementation! 🚀
```

---

**END OF PHASE 2 IMPLEMENTATION PLAN**
