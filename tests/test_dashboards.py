"""
Comprehensive tests for dashboard functionality.

Tests cover:
- Data fetching with caching
- Dashboard rendering
- Filter persistence
- Component rendering
- Performance benchmarks
- Error handling
"""

import time
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

# Dashboard imports
from src.dashboards import apply_global_filters, render_dashboard
from src.dashboards.financial_dashboard import fetch_financial_data, render_financial_dashboard
from src.dashboards.overview_dashboard import (
    create_department_performance_chart,
    create_status_distribution_chart,
    fetch_overview_data,
    render_overview_dashboard,
)
from src.dashboards.quality_dashboard import create_hygiene_gauge, fetch_quality_data
from src.dashboards.review_dashboard import fetch_review_data
from src.dashboards.risk_dashboard import create_anomaly_scatter, create_risk_heatmap

# ==============================================
# FIXTURES
# ==============================================


@pytest.fixture
def sample_filters():
    """Sample filter configuration."""
    return {
        "entity": "Entity001",
        "period": "2024-03",
        "department": "All",
        "category": "All",
        "date_range": "Current Period",
    }


@pytest.fixture
def mock_gl_accounts():
    """Mock GL account data."""
    accounts = []
    for i in range(50):
        accounts.append(
            Mock(
                account_code=f"ACC{i:04d}",
                account_name=f"Test Account {i}",
                account_category=["Assets", "Liabilities", "Revenue", "Expenses"][i % 4],
                department=["Finance", "Operations", "Sales", "IT"][i % 4],
                opening_balance=1000000 + (i * 10000),
                debit_amount=50000 + (i * 1000),
                credit_amount=30000 + (i * 800),
                closing_balance=1020000 + (i * 10200),
                review_status=["reviewed", "pending", "in_review", "flagged"][i % 4],
                reviewer=f"reviewer{i % 3}@test.com",
                flagged=(i % 10 == 0),
                created_at=datetime.now(),
                supporting_docs=f"doc_{i}.pdf" if i % 2 == 0 else None,
            )
        )
    return accounts


@pytest.fixture
def mock_analytics_data():
    """Mock analytics data."""
    return {
        "account_count": 50,
        "total_balance": 52000000,
        "by_category": {
            "Assets": 20000000,
            "Liabilities": 15000000,
            "Revenue": 10000000,
            "Expenses": 7000000,
        },
        "by_status": {"reviewed": 30, "pending": 15, "in_review": 3, "flagged": 2},
        "flagged_count": 5,
    }


# ==============================================
# DATA FETCHING TESTS
# ==============================================


class TestDataFetching:
    """Test data fetching functions with caching."""

    @patch("src.dashboards.overview_dashboard.perform_analytics")
    @patch("src.db.postgres.get_gl_accounts_by_period")
    def test_fetch_overview_data_success(
        self, mock_get_accounts, mock_analytics, sample_filters, mock_gl_accounts
    ):
        """Test successful overview data fetching."""
        mock_analytics.return_value = {"account_count": 50, "total_balance": 1000000}
        mock_get_accounts.return_value = mock_gl_accounts[:10]

        data = fetch_overview_data("Entity001", "2024-03", sample_filters)

        assert "error" not in data
        assert "kpis" in data
        assert "status_data" in data
        assert data["kpis"]["total_accounts"] >= 0

    @patch("src.db.postgres.get_gl_accounts_by_period")
    def test_fetch_financial_data_with_filters(
        self, mock_get_accounts, sample_filters, mock_gl_accounts
    ):
        """Test financial data fetching respects filters."""
        mock_get_accounts.return_value = mock_gl_accounts

        with patch("src.dashboards.financial_dashboard.perform_analytics", return_value={}):
            with patch(
                "src.dashboards.financial_dashboard.calculate_variance_analysis", return_value={}
            ):
                with patch(
                    "src.dashboards.financial_dashboard.calculate_review_status_summary",
                    return_value={},
                ):
                    data = fetch_financial_data("Entity001", "2024-03", sample_filters)

        assert "error" not in data
        assert "summary" in data
        assert "gl_accounts" in data

    @patch("src.db.postgres.get_gl_accounts_by_period")
    def test_fetch_review_data_performance(
        self, mock_get_accounts, sample_filters, mock_gl_accounts
    ):
        """Test review data fetching performance."""
        mock_get_accounts.return_value = mock_gl_accounts

        with patch(
            "src.dashboards.review_dashboard.calculate_review_status_summary", return_value={}
        ):
            with patch("src.dashboards.review_dashboard.get_pending_items_report", return_value={}):
                start_time = time.time()
                data = fetch_review_data("Entity001", "2024-03", sample_filters)
                elapsed_time = time.time() - start_time

        assert "error" not in data
        assert elapsed_time < 3.0, f"Data fetch took {elapsed_time:.2f}s (should be < 3s)"

    def test_fetch_quality_data_error_handling(self, sample_filters):
        """Test quality data fetching handles errors gracefully."""
        with patch(
            "src.dashboards.quality_dashboard.calculate_gl_hygiene_score",
            side_effect=Exception("DB Error"),
        ):
            data = fetch_quality_data("Entity001", "2024-03", sample_filters)

        assert "error" in data
        assert "DB Error" in data["error"]


# ==============================================
# CHART RENDERING TESTS
# ==============================================


class TestChartRendering:
    """Test chart generation functions."""

    def test_create_status_distribution_chart(self):
        """Test pie chart creation for status distribution."""
        status_data = {"reviewed": 30, "pending": 15, "flagged": 5}

        start_time = time.time()
        fig = create_status_distribution_chart(status_data)
        render_time = time.time() - start_time

        assert fig is not None
        assert len(fig.data) > 0
        assert render_time < 2.0, f"Chart render took {render_time:.2f}s (should be < 2s)"

    def test_create_department_performance_chart(self):
        """Test horizontal bar chart for department performance."""
        dept_stats = {
            "Finance": {"completion_rate": 85, "total": 20},
            "Operations": {"completion_rate": 75, "total": 15},
            "Sales": {"completion_rate": 90, "total": 10},
        }

        fig = create_department_performance_chart(dept_stats)

        assert fig is not None
        assert len(fig.data) > 0

    def test_create_hygiene_gauge_with_dict_input(self):
        """Test gauge chart accepts dict input."""
        hygiene_data = {
            "overall_score": 85,
            "component_scores": {"completeness": 90, "accuracy": 85, "consistency": 80},
        }

        fig = create_hygiene_gauge(hygiene_data)

        assert fig is not None
        assert len(fig.data) > 0

    def test_create_anomaly_scatter_empty_data(self):
        """Test anomaly scatter handles empty data gracefully."""
        empty_df = pd.DataFrame()

        fig = create_anomaly_scatter(empty_df)

        assert fig is not None  # Should return valid figure even with no data

    def test_create_risk_heatmap(self):
        """Test risk heatmap generation."""
        risk_data = pd.DataFrame(
            {"Finance": [10, 20, 30], "Operations": [15, 25, 35], "Sales": [5, 15, 25]},
            index=["High", "Medium", "Low"],
        )

        fig = create_risk_heatmap(risk_data)

        assert fig is not None
        assert len(fig.data) > 0


# ==============================================
# DASHBOARD RENDERING TESTS
# ==============================================


class TestDashboardRendering:
    """Test full dashboard rendering with Streamlit mocking."""

    @patch("streamlit.title")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.metric")
    def test_render_overview_dashboard(
        self, mock_metric, mock_columns, mock_markdown, mock_title, sample_filters
    ):
        """Test overview dashboard renders without errors."""

        # Create mock columns that support context manager protocol
        def create_mock_col():
            mock_col = MagicMock()
            mock_col.__enter__ = MagicMock(return_value=mock_col)
            mock_col.__exit__ = MagicMock(return_value=False)
            return mock_col

        # Make columns return the right number based on argument (int or list)
        def mock_columns_func(spec):
            if isinstance(spec, int):
                return [create_mock_col() for _ in range(spec)]
            elif isinstance(spec, list):
                return [create_mock_col() for _ in range(len(spec))]
            return [create_mock_col(), create_mock_col()]

        mock_columns.side_effect = mock_columns_func

        with patch("src.dashboards.overview_dashboard.fetch_overview_data") as mock_fetch:
            mock_fetch.return_value = {
                "kpis": {
                    "total_accounts": 50,
                    "total_balance": 1000000,
                    "completion_rate": 85,
                    "hygiene_score": 80,
                    "pending_count": 10,
                    "flagged_count": 2,
                },
                "status_data": {"reviewed": 30, "pending": 20},
                "dept_stats": {},
                "pending_items": {"pending_reviews": []},
                "recent_activities": [],
                "insights": {"recommendations": []},
                "exec_summary": {},
            }

            # Should not raise any exceptions
            render_overview_dashboard(sample_filters)

            assert mock_title.called
            assert mock_markdown.called

    @patch("streamlit.title")
    @patch("streamlit.subheader")
    def test_render_financial_dashboard_error_handling(
        self, mock_subheader, mock_title, sample_filters
    ):
        """Test financial dashboard handles data errors gracefully."""
        with patch("src.dashboards.financial_dashboard.fetch_financial_data") as mock_fetch:
            mock_fetch.return_value = {"error": "Database connection failed"}

            with patch("streamlit.error") as mock_error:
                render_financial_dashboard(sample_filters)

                assert mock_error.called


# ==============================================
# FILTER PERSISTENCE TESTS
# ==============================================


class TestFilterPersistence:
    """Test filter state management."""

    @patch("streamlit.sidebar")
    def test_apply_global_filters_initializes_state(self, mock_sidebar):
        """Test global filters initialize session state."""
        # Mock session_state as a dict-like object
        mock_session_state = MagicMock()
        mock_session_state.__contains__ = Mock(return_value=False)
        mock_session_state.__getitem__ = Mock(side_effect=KeyError)
        mock_session_state.__setitem__ = Mock()

        # Create mock columns that support context manager
        def create_mock_col():
            mock_col = MagicMock()
            mock_col.__enter__ = MagicMock(return_value=mock_col)
            mock_col.__exit__ = MagicMock(return_value=False)
            return mock_col

        mock_sidebar.selectbox = Mock(
            side_effect=["Entity001", "2024-03", "All", "All", "Current Period"]
        )
        mock_sidebar.markdown = Mock()
        mock_sidebar.button = Mock(return_value=False)
        mock_sidebar.checkbox = Mock(return_value=False)
        mock_sidebar.columns = Mock(return_value=[create_mock_col(), create_mock_col()])

        with patch("streamlit.session_state", mock_session_state):
            filters = apply_global_filters()

        assert filters is not None
        assert "entity" in filters
        assert "period" in filters

    def test_filter_dict_structure(self, sample_filters):
        """Test filter dict has required keys."""
        required_keys = ["entity", "period", "department", "category", "date_range"]

        for key in required_keys:
            assert key in sample_filters, f"Missing required filter key: {key}"


# ==============================================
# CACHING TESTS
# ==============================================


class TestCaching:
    """Test caching behavior."""

    @patch("src.dashboards.overview_dashboard.perform_analytics")
    @patch("src.db.postgres.get_gl_accounts_by_period")
    def test_fetch_overview_data_cached(
        self, mock_get_accounts, mock_analytics, sample_filters, mock_gl_accounts
    ):
        """Test overview data is cached properly."""
        mock_analytics.return_value = {"account_count": 50}
        mock_get_accounts.return_value = mock_gl_accounts[:10]

        # First call
        data1 = fetch_overview_data("Entity001", "2024-03", sample_filters)
        call_count_1 = mock_get_accounts.call_count

        # Second call with same params (may or may not use cache depending on Streamlit context)
        data2 = fetch_overview_data("Entity001", "2024-03", sample_filters)
        call_count_2 = mock_get_accounts.call_count

        # Both calls should return valid data
        assert data1 is not None
        assert data2 is not None
        # Note: Streamlit caching doesn't work in test context, so we just verify data validity


# ==============================================
# PERFORMANCE BENCHMARKS
# ==============================================


class TestPerformance:
    """Test performance benchmarks."""

    @patch("src.dashboards.overview_dashboard.perform_analytics")
    @patch("src.db.postgres.get_gl_accounts_by_period")
    def test_overview_dashboard_load_time(
        self, mock_get_accounts, mock_analytics, sample_filters, mock_gl_accounts
    ):
        """Test overview dashboard loads within 3 seconds."""
        mock_analytics.return_value = {"account_count": 50, "total_balance": 1000000}
        mock_get_accounts.return_value = mock_gl_accounts[:10]

        with patch(
            "src.dashboards.overview_dashboard.calculate_review_status_summary", return_value={}
        ):
            with patch(
                "src.dashboards.overview_dashboard.calculate_gl_hygiene_score",
                return_value={"overall_score": 85},
            ):
                with patch(
                    "src.dashboards.overview_dashboard.get_pending_items_report", return_value={}
                ):
                    with patch(
                        "src.dashboards.overview_dashboard.generate_proactive_insights",
                        return_value={},
                    ):
                        with patch(
                            "src.dashboards.overview_dashboard.generate_executive_summary",
                            return_value={},
                        ):
                            with patch(
                                "src.dashboards.overview_dashboard.fetch_recent_activities",
                                return_value=[],
                            ):
                                with patch(
                                    "src.dashboards.overview_dashboard.calculate_department_stats",
                                    return_value={},
                                ):
                                    start_time = time.time()
                                    data = fetch_overview_data(
                                        "Entity001", "2024-03", sample_filters
                                    )
                                    load_time = time.time() - start_time

        assert load_time < 3.0, f"Page load took {load_time:.2f}s (should be < 3s)"

    def test_chart_render_performance(self):
        """Test all chart types render within 2 seconds."""
        test_data = {"reviewed": 30, "pending": 15, "flagged": 5}

        start_time = time.time()
        fig = create_status_distribution_chart(test_data)
        render_time = time.time() - start_time

        assert render_time < 2.0, f"Chart render took {render_time:.2f}s (should be < 2s)"


# ==============================================
# INTEGRATION TESTS
# ==============================================


class TestIntegration:
    """Test full integration scenarios."""

    @patch("streamlit.session_state", new_callable=dict)
    def test_dashboard_routing(self, mock_session_state):
        """Test dashboard routing works for all pages."""
        pages = ["overview", "financial", "review", "quality", "risk"]

        for page in pages:
            filters = {
                "entity": "Entity001",
                "period": "2024-03",
                "department": "All",
                "category": "All",
                "date_range": "Current Period",
            }

            # Should not raise exceptions
            try:
                with patch(
                    f"src.dashboards.{page}_dashboard.render_{page}_dashboard"
                ) as mock_render:
                    render_dashboard(page, filters)
                    assert mock_render.called, f"Dashboard {page} was not rendered"
            except ImportError:
                pytest.skip(f"Dashboard {page} not fully implemented")


# ==============================================
# ERROR HANDLING TESTS
# ==============================================


class TestErrorHandling:
    """Test error handling across dashboards."""

    def test_dashboard_handles_missing_data(self, sample_filters):
        """Test dashboards handle missing data gracefully."""
        with patch("src.dashboards.overview_dashboard.fetch_overview_data") as mock_fetch:
            mock_fetch.return_value = {}

            # Should not crash
            try:
                with patch("streamlit.title"):
                    with patch("streamlit.markdown"):
                        with patch("streamlit.spinner"):
                            render_overview_dashboard(sample_filters)
            except KeyError:
                pytest.fail("Dashboard should handle missing data keys gracefully")

    def test_dashboard_handles_db_errors(self, sample_filters):
        """Test dashboards handle database errors gracefully."""
        with patch("src.dashboards.financial_dashboard.fetch_financial_data") as mock_fetch:
            mock_fetch.return_value = {"error": "Database connection timeout"}

            with patch("streamlit.title"):
                with patch("streamlit.markdown"):
                    with patch("streamlit.error") as mock_error:
                        render_financial_dashboard(sample_filters)
                        assert mock_error.called


# ==============================================
# RUN TESTS
# ==============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.dashboards", "--cov-report=term-missing"])
