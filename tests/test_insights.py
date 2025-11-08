"""Unit tests for insights module."""

from unittest.mock import Mock, patch

import pytest

from src.insights import (
    compare_multi_period,
    generate_drill_down_report,
    generate_executive_summary,
    generate_proactive_insights,
)


class TestGenerateProactiveInsights:
    """Tests for generate_proactive_insights function."""

    @patch("src.insights.get_pending_items_report")
    @patch("src.insights.identify_anomalies_ml")
    @patch("src.insights.calculate_gl_hygiene_score")
    def test_proactive_insights_critical_items(self, mock_hygiene, mock_anomalies, mock_pending):
        """Test insights generation with critical items."""
        # Mock dependencies
        mock_hygiene.return_value = {"overall_score": 65, "grade": "C"}
        mock_anomalies.return_value = {
            "anomaly_count": 3,
            "critical_count": 1,
            "anomalies": [{"account_code": "100000", "severity": "critical"}],
        }
        mock_pending.return_value = {
            "pending_reviews_count": 10,
            "flagged_items_count": 2,
            "missing_docs_count": 5,
        }

        result = generate_proactive_insights("Entity001", "2024-03")

        assert "insights" in result
        assert len(result["insights"]) >= 3
        assert any(insight["priority"] == "critical" for insight in result["insights"])
        assert all("message" in insight for insight in result["insights"])
        assert all("recommendation" in insight for insight in result["insights"])

    @patch("src.insights.get_pending_items_report")
    @patch("src.insights.identify_anomalies_ml")
    @patch("src.insights.calculate_gl_hygiene_score")
    def test_proactive_insights_good_status(self, mock_hygiene, mock_anomalies, mock_pending):
        """Test insights with good overall status."""
        mock_hygiene.return_value = {"overall_score": 90, "grade": "A"}
        mock_anomalies.return_value = {"anomaly_count": 0}
        mock_pending.return_value = {
            "pending_reviews_count": 0,
            "flagged_items_count": 0,
            "missing_docs_count": 0,
        }

        result = generate_proactive_insights("Entity001", "2024-03")

        assert "insights" in result
        # Should still have at least info-level insights
        assert len(result["insights"]) > 0

    @patch("src.insights.get_pending_items_report")
    @patch("src.insights.identify_anomalies_ml")
    @patch("src.insights.calculate_gl_hygiene_score")
    def test_proactive_insights_error_handling(self, mock_hygiene, mock_anomalies, mock_pending):
        """Test insights handles dependency errors."""
        mock_hygiene.return_value = {"error": "Database error"}
        mock_anomalies.return_value = {"error": "Calculation error"}
        mock_pending.return_value = {"error": "Query error"}

        result = generate_proactive_insights("Entity001", "2024-03")

        # Should gracefully handle errors
        assert "insights" in result or "error" in result


class TestGenerateExecutiveSummary:
    """Tests for generate_executive_summary function."""

    @patch("src.insights.perform_analytics")
    @patch("src.insights.calculate_review_status_summary")
    @patch("src.insights.calculate_gl_hygiene_score")
    def test_executive_summary_excellent(self, mock_hygiene, mock_status, mock_analytics):
        """Test executive summary with excellent status."""
        mock_analytics.return_value = {"total_balance": 1000000, "account_count": 100}
        mock_status.return_value = {"overall_completion_rate": 95.5}
        mock_hygiene.return_value = {"overall_score": 92, "grade": "A"}

        result = generate_executive_summary("Entity001", "2024-03")

        assert "overall_status" in result
        assert result["overall_status"] == "Excellent"
        assert "key_metrics" in result
        assert "highlights" in result
        assert "concerns" in result
        assert "recommendations" in result

    @patch("src.insights.perform_analytics")
    @patch("src.insights.calculate_review_status_summary")
    @patch("src.insights.calculate_gl_hygiene_score")
    def test_executive_summary_needs_attention(self, mock_hygiene, mock_status, mock_analytics):
        """Test executive summary needing attention."""
        mock_analytics.return_value = {"total_balance": 500000, "account_count": 50}
        mock_status.return_value = {"overall_completion_rate": 45.0}
        mock_hygiene.return_value = {"overall_score": 55, "grade": "D"}

        result = generate_executive_summary("Entity001", "2024-03")

        assert result["overall_status"] == "Needs Attention"
        assert len(result["concerns"]) > 0
        assert len(result["recommendations"]) > 0

    @patch("src.insights.perform_analytics")
    def test_executive_summary_no_data(self, mock_analytics):
        """Test executive summary with no data."""
        mock_analytics.return_value = {"error": "No accounts found"}

        result = generate_executive_summary("Entity001", "2024-03")

        assert "error" in result


class TestGenerateDrillDownReport:
    """Tests for generate_drill_down_report function."""

    @patch("src.insights.get_postgres_session")
    def test_drill_down_by_category(self, mock_session):
        """Test drill-down by category."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query

        mock_accounts = [
            Mock(
                account_code="100000",
                account_name="Cash",
                category="Assets",
                debit_balance=100000,
                credit_balance=0,
                review_status="Reviewed",
            ),
            Mock(
                account_code="100001",
                account_name="Bank",
                category="Assets",
                debit_balance=200000,
                credit_balance=0,
                review_status="Pending",
            ),
        ]
        mock_query.all.return_value = mock_accounts

        result = generate_drill_down_report("Entity001", "2024-03", "category", "Assets")

        assert "summary_metrics" in result
        assert "status_distribution" in result
        assert "top_accounts" in result
        assert result["summary_metrics"]["total_accounts"] == 2

    @patch("src.insights.get_postgres_session")
    def test_drill_down_by_department(self, mock_session):
        """Test drill-down by department."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query

        mock_accounts = [
            Mock(
                department="Finance",
                debit_balance=50000,
                credit_balance=0,
                review_status="Reviewed",
            )
        ]
        mock_query.all.return_value = mock_accounts

        result = generate_drill_down_report("Entity001", "2024-03", "department", "Finance")

        assert "summary_metrics" in result
        assert result["summary_metrics"]["total_accounts"] == 1

    @patch("src.insights.get_postgres_session")
    def test_drill_down_no_matches(self, mock_session):
        """Test drill-down with no matching accounts."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query
        mock_query.all.return_value = []

        result = generate_drill_down_report("Entity001", "2024-03", "category", "InvalidCategory")

        assert "error" in result or result["summary_metrics"]["total_accounts"] == 0

    @patch("src.insights.get_postgres_session")
    def test_drill_down_invalid_dimension(self, mock_session):
        """Test drill-down with invalid dimension."""
        result = generate_drill_down_report("Entity001", "2024-03", "invalid_dimension", "Value")

        # Should handle gracefully
        assert "error" in result or "summary_metrics" in result


class TestCompareMultiPeriod:
    """Tests for compare_multi_period function."""

    @patch("src.insights.calculate_gl_hygiene_score")
    @patch("src.insights.calculate_review_status_summary")
    @patch("src.insights.perform_analytics")
    def test_multi_period_comparison_trend_increasing(
        self, mock_analytics, mock_status, mock_hygiene
    ):
        """Test multi-period comparison with increasing trend."""
        # Mock data showing increasing trend
        mock_analytics.side_effect = [
            {"total_balance": 100000, "account_count": 50},
            {"total_balance": 120000, "account_count": 55},
            {"total_balance": 150000, "account_count": 60},
        ]
        mock_status.side_effect = [
            {"overall_completion_rate": 70},
            {"overall_completion_rate": 75},
            {"overall_completion_rate": 80},
        ]
        mock_hygiene.side_effect = [
            {"overall_score": 65},
            {"overall_score": 72},
            {"overall_score": 78},
        ]

        result = compare_multi_period("Entity001", ["2024-01", "2024-02", "2024-03"])

        assert "period_summaries" in result
        assert len(result["period_summaries"]) == 3
        assert "trends" in result
        assert result["trends"]["total_balance"]["direction"] == "increasing"

    @patch("src.insights.calculate_gl_hygiene_score")
    @patch("src.insights.calculate_review_status_summary")
    @patch("src.insights.perform_analytics")
    def test_multi_period_comparison_stable(self, mock_analytics, mock_status, mock_hygiene):
        """Test multi-period comparison with stable trend."""
        mock_analytics.side_effect = [{"total_balance": 100000, "account_count": 50}] * 3
        mock_status.side_effect = [{"overall_completion_rate": 75}] * 3
        mock_hygiene.side_effect = [{"overall_score": 70}] * 3

        result = compare_multi_period("Entity001", ["2024-01", "2024-02", "2024-03"])

        assert result["trends"]["total_balance"]["direction"] == "stable"

    @patch("src.insights.perform_analytics")
    def test_multi_period_single_period(self, mock_analytics):
        """Test multi-period with only one period."""
        mock_analytics.return_value = {"total_balance": 100000}

        result = compare_multi_period("Entity001", ["2024-03"])

        # Should return error or handle gracefully
        assert "error" in result or len(result["period_summaries"]) == 1

    @patch("src.insights.perform_analytics")
    def test_multi_period_empty_periods(self, mock_analytics):
        """Test multi-period with empty periods list."""
        result = compare_multi_period("Entity001", [])

        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.insights", "--cov-report=term-missing"])
