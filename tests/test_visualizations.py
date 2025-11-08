"""Unit tests for visualizations module."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.visualizations import (
    create_anomaly_scatter,
    create_category_breakdown_pie,
    create_dashboard_layout,
    create_department_comparison_radar,
    create_hygiene_gauge,
    create_review_status_sunburst,
    create_reviewer_workload_bar,
    create_sla_timeline_gantt,
    create_trend_line_chart,
    create_variance_heatmap,
    create_variance_waterfall_chart,
    export_chart_to_html,
)


class TestVarianceWaterfallChart:
    """Tests for create_variance_waterfall_chart function."""

    def test_waterfall_chart_creation(self):
        """Test waterfall chart with valid data."""
        variance_df = pd.DataFrame(
            {
                "account_name": ["Cash", "Bank", "AP", "AR"],
                "variance": [50000, -20000, 30000, -10000],
            }
        )

        fig = create_variance_waterfall_chart(variance_df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.layout.title.text is not None

    def test_waterfall_chart_empty_data(self):
        """Test waterfall chart with empty DataFrame."""
        variance_df = pd.DataFrame({"account_name": [], "variance": []})

        fig = create_variance_waterfall_chart(variance_df)

        assert isinstance(fig, go.Figure)

    def test_waterfall_chart_large_dataset(self):
        """Test waterfall chart with >15 accounts (should trim to top 15)."""
        variance_df = pd.DataFrame(
            {
                "account_name": [f"Account{i}" for i in range(50)],
                "variance": [1000 * i for i in range(50)],
            }
        )

        fig = create_variance_waterfall_chart(variance_df)

        assert isinstance(fig, go.Figure)
        # Should only show top 15
        assert len(fig.data[0].x) <= 15


class TestHygieneGauge:
    """Tests for create_hygiene_gauge function."""

    def test_gauge_excellent_score(self):
        """Test gauge with excellent score (green zone)."""
        components = {
            "review_completion": 90,
            "documentation_completeness": 88,
            "sla_compliance": 92,
            "variance_resolution": 85,
        }

        fig = create_hygiene_gauge(90, components)

        assert isinstance(fig, go.Figure)
        assert fig.data[0].value == 90
        assert fig.data[0].gauge.bar.color == "#2ecc71"  # Green

    def test_gauge_poor_score(self):
        """Test gauge with poor score (red zone)."""
        components = {}
        fig = create_hygiene_gauge(55, components)

        assert isinstance(fig, go.Figure)
        assert fig.data[0].gauge.bar.color == "#e74c3c"  # Red

    def test_gauge_boundary_scores(self):
        """Test gauge at boundary scores."""
        # Test at 85 (should be green)
        fig1 = create_hygiene_gauge(85, {})
        assert fig1.data[0].gauge.bar.color == "#2ecc71"

        # Test at 70 (should be orange)
        fig2 = create_hygiene_gauge(70, {})
        assert fig2.data[0].gauge.bar.color == "#f39c12"

        # Test at 60 (should be red)
        fig3 = create_hygiene_gauge(60, {})
        assert fig3.data[0].gauge.bar.color == "#e74c3c"


class TestReviewStatusSunburst:
    """Tests for create_review_status_sunburst function."""

    def test_sunburst_chart_creation(self):
        """Test sunburst with hierarchical status data."""
        status_data = {
            "by_criticality": {
                "High": {"Reviewed": 10, "Pending": 5},
                "Medium": {"Reviewed": 20, "Pending": 8},
                "Low": {"Reviewed": 30, "Pending": 2},
            }
        }

        fig = create_review_status_sunburst(status_data)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert len(fig.data[0].labels) > 1  # Should have multiple levels

    def test_sunburst_empty_data(self):
        """Test sunburst with empty data."""
        status_data = {"by_criticality": {}}

        fig = create_review_status_sunburst(status_data)

        assert isinstance(fig, go.Figure)


class TestCategoryBreakdownPie:
    """Tests for create_category_breakdown_pie function."""

    def test_pie_chart_creation(self):
        """Test pie chart with category data."""
        category_data = {
            "Assets": 500000,
            "Liabilities": 300000,
            "Equity": 200000,
            "Revenue": 150000,
            "Expenses": 100000,
        }

        fig = create_category_breakdown_pie(category_data)

        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].labels) == 5
        assert sum(fig.data[0].values) == 1250000

    def test_pie_chart_single_category(self):
        """Test pie chart with single category."""
        category_data = {"Assets": 100000}

        fig = create_category_breakdown_pie(category_data)

        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].labels) == 1


class TestReviewerWorkloadBar:
    """Tests for create_reviewer_workload_bar function."""

    def test_workload_bar_creation(self):
        """Test reviewer workload stacked bar chart."""
        reviewer_stats = [
            {"reviewer": "John Doe", "assigned": 50, "completed": 35, "pending": 15},
            {"reviewer": "Jane Smith", "assigned": 40, "completed": 30, "pending": 10},
            {"reviewer": "Bob Wilson", "assigned": 60, "completed": 45, "pending": 15},
        ]

        fig = create_reviewer_workload_bar(reviewer_stats)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2  # Completed and Pending traces
        assert fig.layout.barmode == "stack"

    def test_workload_bar_empty_data(self):
        """Test workload bar with empty data."""
        reviewer_stats = []

        fig = create_reviewer_workload_bar(reviewer_stats)

        assert isinstance(fig, go.Figure)


class TestAnomalyScatter:
    """Tests for create_anomaly_scatter function."""

    def test_anomaly_scatter_creation(self):
        """Test anomaly scatter plot."""
        anomaly_data = [
            {
                "account_code": "100000",
                "account_name": "Cash",
                "balance": 150000,
                "z_score": 3.5,
                "category": "Assets",
            },
            {
                "account_code": "200000",
                "account_name": "AP",
                "balance": 80000,
                "z_score": 2.8,
                "category": "Liabilities",
            },
        ]

        fig = create_anomaly_scatter(anomaly_data)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1  # At least scatter data

    def test_anomaly_scatter_no_anomalies(self):
        """Test scatter plot with no anomalies."""
        anomaly_data = []

        fig = create_anomaly_scatter(anomaly_data)

        assert isinstance(fig, go.Figure)
        # Should have annotation saying "No anomalies"


class TestTrendLineChart:
    """Tests for create_trend_line_chart function."""

    def test_trend_chart_creation(self):
        """Test multi-line trend chart."""
        trend_data = {
            "Balance": [100000, 120000, 150000],
            "Hygiene Score": [70, 75, 82],
            "Completion Rate": [65, 72, 80],
        }
        periods = ["2024-01", "2024-02", "2024-03"]

        fig = create_trend_line_chart(trend_data, periods)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3  # Three metrics

    def test_trend_chart_single_period(self):
        """Test trend chart with single period."""
        trend_data = {"Balance": [100000]}
        periods = ["2024-03"]

        fig = create_trend_line_chart(trend_data, periods)

        assert isinstance(fig, go.Figure)


class TestSLATimelineGantt:
    """Tests for create_sla_timeline_gantt function."""

    def test_gantt_chart_creation(self):
        """Test Gantt chart for SLA timelines."""
        assignments = [
            {"account_code": "100000", "status": "Reviewed", "duration": 3},
            {"account_code": "200000", "status": "Pending", "duration": 5},
            {"account_code": "300000", "status": "Overdue", "duration": 8},
        ]

        fig = create_sla_timeline_gantt(assignments)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3  # One bar per assignment

    def test_gantt_empty_assignments(self):
        """Test Gantt chart with no assignments."""
        assignments = []

        fig = create_sla_timeline_gantt(assignments)

        assert isinstance(fig, go.Figure)


class TestVarianceHeatmap:
    """Tests for create_variance_heatmap function."""

    def test_heatmap_creation(self):
        """Test variance heatmap."""
        variance_data = pd.DataFrame(
            {"2024-01": [10, -5, 20], "2024-02": [15, -8, 18], "2024-03": [12, -3, 25]},
            index=["Cash", "Bank", "AP"],
        )

        fig = create_variance_heatmap(variance_data)

        assert isinstance(fig, go.Figure)
        assert fig.data[0].type == "heatmap"

    def test_heatmap_empty_data(self):
        """Test heatmap with empty DataFrame."""
        variance_data = pd.DataFrame()

        fig = create_variance_heatmap(variance_data)

        assert isinstance(fig, go.Figure)


class TestDepartmentComparisonRadar:
    """Tests for create_department_comparison_radar function."""

    def test_radar_chart_creation(self):
        """Test radar chart for department comparison."""
        dept_metrics = {
            "Finance": {
                "completion_rate": 85,
                "hygiene_score": 78,
                "sla_compliance": 90,
                "doc_completeness": 82,
            },
            "Operations": {
                "completion_rate": 72,
                "hygiene_score": 68,
                "sla_compliance": 75,
                "doc_completeness": 70,
            },
        }

        fig = create_department_comparison_radar(dept_metrics)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2  # Two departments

    def test_radar_single_department(self):
        """Test radar chart with single department."""
        dept_metrics = {
            "Finance": {
                "completion_rate": 85,
                "hygiene_score": 78,
                "sla_compliance": 90,
                "doc_completeness": 82,
            }
        }

        fig = create_department_comparison_radar(dept_metrics)

        assert isinstance(fig, go.Figure)


class TestExportChartToHTML:
    """Tests for export_chart_to_html function."""

    def test_export_html_success(self, tmp_path):
        """Test HTML export."""
        fig = create_category_breakdown_pie({"Assets": 100000, "Liabilities": 50000})
        output_path = tmp_path / "test_chart.html"

        result = export_chart_to_html(fig, str(output_path))

        assert result == str(output_path)
        assert output_path.exists()
        assert output_path.suffix == ".html"

    def test_export_html_creates_directory(self, tmp_path):
        """Test HTML export creates parent directories."""
        output_path = tmp_path / "subdir" / "test_chart.html"
        fig = create_hygiene_gauge(75, {})

        result = export_chart_to_html(fig, str(output_path))

        assert output_path.exists()


class TestCreateDashboardLayout:
    """Tests for create_dashboard_layout function."""

    def test_dashboard_grid_layout(self):
        """Test dashboard with grid layout."""
        charts = [
            create_category_breakdown_pie({"Assets": 100000}),
            create_hygiene_gauge(75, {}),
            create_trend_line_chart({"Balance": [100, 120]}, ["Jan", "Feb"]),
        ]

        fig = create_dashboard_layout(charts, layout="grid", cols=2)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 3  # At least 3 traces from 3 charts

    def test_dashboard_vertical_layout(self):
        """Test dashboard with vertical layout."""
        charts = [create_category_breakdown_pie({"Assets": 100000}), create_hygiene_gauge(75, {})]

        fig = create_dashboard_layout(charts, layout="vertical")

        assert isinstance(fig, go.Figure)

    def test_dashboard_horizontal_layout(self):
        """Test dashboard with horizontal layout."""
        charts = [create_category_breakdown_pie({"Assets": 100000}), create_hygiene_gauge(75, {})]

        fig = create_dashboard_layout(charts, layout="horizontal")

        assert isinstance(fig, go.Figure)

    def test_dashboard_single_chart(self):
        """Test dashboard with single chart."""
        charts = [create_category_breakdown_pie({"Assets": 100000})]

        fig = create_dashboard_layout(charts, layout="grid")

        assert isinstance(fig, go.Figure)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.visualizations", "--cov-report=term-missing"])
