"""Unit tests for analytics module."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.analytics import (
    calculate_gl_hygiene_score,
    calculate_review_status_summary,
    calculate_variance_analysis,
    export_analytics_to_csv,
    export_analytics_to_excel,
    get_pending_items_report,
    identify_anomalies_ml,
    perform_analytics,
)


class TestPerformAnalytics:
    """Tests for perform_analytics function."""

    @patch("src.analytics.get_postgres_session")
    def test_perform_analytics_success(self, mock_session):
        """Test successful analytics calculation."""
        # Mock session and query results
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query

        # Mock GL accounts
        mock_accounts = [
            Mock(category="Assets", debit_balance=100000, credit_balance=0),
            Mock(category="Liabilities", debit_balance=0, credit_balance=50000),
            Mock(category="Assets", debit_balance=25000, credit_balance=0),
        ]
        mock_query.all.return_value = mock_accounts

        result = perform_analytics("Entity001", "2024-03")

        assert "by_category" in result
        assert "total_balance" in result
        assert result["total_balance"] == 175000
        assert "Assets" in result["by_category"]

    @patch("src.analytics.get_postgres_session")
    def test_perform_analytics_empty_data(self, mock_session):
        """Test analytics with no accounts."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query
        mock_query.all.return_value = []

        result = perform_analytics("Entity001", "2024-03")

        assert "error" in result
        assert "No accounts found" in result["error"]

    @patch("src.analytics.get_postgres_session")
    def test_perform_analytics_exception(self, mock_session):
        """Test analytics handles exceptions."""
        mock_session.return_value.query.side_effect = Exception("Database error")

        result = perform_analytics("Entity001", "2024-03")

        assert "error" in result


class TestCalculateVarianceAnalysis:
    """Tests for calculate_variance_analysis function."""

    @patch("src.analytics.get_postgres_session")
    def test_variance_analysis_success(self, mock_session):
        """Test successful variance calculation."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query

        # Mock current period accounts
        current_accounts = [
            Mock(
                account_code="100000", account_name="Cash", debit_balance=150000, credit_balance=0
            ),
            Mock(account_code="200000", account_name="AP", debit_balance=0, credit_balance=80000),
        ]
        # Mock previous period accounts
        previous_accounts = [
            Mock(
                account_code="100000", account_name="Cash", debit_balance=100000, credit_balance=0
            ),
            Mock(account_code="200000", account_name="AP", debit_balance=0, credit_balance=60000),
        ]

        mock_query.all.side_effect = [current_accounts, previous_accounts]

        result = calculate_variance_analysis("Entity001", "2024-03", "2024-02")

        assert "accounts_analyzed" in result
        assert "significant_variances" in result
        assert result["accounts_analyzed"] == 2

    @patch("src.analytics.get_postgres_session")
    def test_variance_analysis_no_previous_data(self, mock_session):
        """Test variance analysis with no previous period data."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query

        current_accounts = [Mock(account_code="100000", debit_balance=150000, credit_balance=0)]
        mock_query.all.side_effect = [current_accounts, []]

        result = calculate_variance_analysis("Entity001", "2024-03", "2024-02")

        assert "error" in result or result["accounts_analyzed"] == 0


class TestCalculateReviewStatusSummary:
    """Tests for calculate_review_status_summary function."""

    @patch("src.analytics.get_postgres_session")
    def test_review_status_summary_success(self, mock_session):
        """Test successful status summary."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query

        mock_accounts = [
            Mock(
                criticality="High",
                review_status="Reviewed",
                category="Assets",
                department="Finance",
            ),
            Mock(
                criticality="High", review_status="Pending", category="Assets", department="Finance"
            ),
            Mock(
                criticality="Low",
                review_status="Reviewed",
                category="Expenses",
                department="Operations",
            ),
        ]
        mock_query.all.return_value = mock_accounts

        result = calculate_review_status_summary("Entity001", "2024-03")

        assert "by_criticality" in result
        assert "by_category" in result
        assert "by_department" in result
        assert "overall_completion_rate" in result

    @patch("src.analytics.get_postgres_session")
    def test_review_status_empty_data(self, mock_session):
        """Test status summary with no data."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query
        mock_query.all.return_value = []

        result = calculate_review_status_summary("Entity001", "2024-03")

        assert "error" in result


class TestCalculateGLHygieneScore:
    """Tests for calculate_gl_hygiene_score function."""

    @patch("src.analytics.get_mongo_database")
    @patch("src.analytics.get_postgres_session")
    def test_hygiene_score_perfect(self, mock_pg_session, mock_mongo_db):
        """Test hygiene score with perfect compliance."""
        # Mock PostgreSQL
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_pg_session.return_value.query.return_value = mock_query

        mock_accounts = [
            Mock(
                id=1,
                review_status="Reviewed",
                created_at=datetime.now(),
                reviewed_at=datetime.now(),
            ),
            Mock(
                id=2,
                review_status="Approved",
                created_at=datetime.now(),
                reviewed_at=datetime.now(),
            ),
        ]
        mock_query.all.return_value = mock_accounts

        # Mock MongoDB
        mock_docs_col = Mock()
        mock_docs_col.count_documents.return_value = 2
        mock_validation_col = Mock()
        mock_validation_col.count_documents.return_value = 0

        mock_mongo_db.return_value.__getitem__.side_effect = lambda key: {
            "supporting_docs": mock_docs_col,
            "validation_results": mock_validation_col,
        }[key]

        result = calculate_gl_hygiene_score("Entity001", "2024-03")

        assert "overall_score" in result
        assert "grade" in result
        assert "components" in result
        assert 0 <= result["overall_score"] <= 100

    @patch("src.analytics.get_postgres_session")
    def test_hygiene_score_no_accounts(self, mock_session):
        """Test hygiene score with no accounts."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query
        mock_query.all.return_value = []

        result = calculate_gl_hygiene_score("Entity001", "2024-03")

        assert "error" in result


class TestGetPendingItemsReport:
    """Tests for get_pending_items_report function."""

    @patch("src.analytics.get_mongo_database")
    @patch("src.analytics.get_postgres_session")
    def test_pending_items_report(self, mock_pg_session, mock_mongo_db):
        """Test pending items report."""
        # Mock PostgreSQL
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_pg_session.return_value.query.return_value = mock_query

        mock_pending = [
            Mock(
                account_code="100000",
                account_name="Cash",
                criticality="High",
                review_status="Pending",
            )
        ]
        mock_flagged = [
            Mock(
                account_code="200000",
                account_name="AP",
                criticality="Medium",
                review_status="Flagged",
            )
        ]

        mock_query.all.side_effect = [mock_pending, mock_flagged]

        # Mock MongoDB
        mock_docs_col = Mock()
        mock_docs_col.find.return_value = []
        mock_mongo_db.return_value.__getitem__.return_value = mock_docs_col

        result = get_pending_items_report("Entity001", "2024-03")

        assert "pending_reviews_count" in result
        assert "flagged_items_count" in result
        assert "pending_reviews" in result


class TestIdentifyAnomaliesML:
    """Tests for identify_anomalies_ml function."""

    @patch("src.analytics.get_postgres_session")
    def test_anomalies_detection(self, mock_session):
        """Test anomaly detection with z-score."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query

        # Create accounts with one clear outlier
        mock_accounts = [
            Mock(
                account_code=f"{i}",
                account_name=f"Account{i}",
                category="Assets",
                debit_balance=10000 + i * 100,
                credit_balance=0,
            )
            for i in range(20)
        ]
        # Add outlier
        mock_accounts.append(
            Mock(
                account_code="OUTLIER",
                account_name="Outlier Account",
                category="Assets",
                debit_balance=500000,
                credit_balance=0,
            )
        )

        mock_query.all.return_value = mock_accounts

        result = identify_anomalies_ml("Entity001", "2024-03", threshold=2.0)

        assert "anomaly_count" in result
        assert "anomalies" in result
        assert "categories_analyzed" in result

    @patch("src.analytics.get_postgres_session")
    def test_anomalies_insufficient_data(self, mock_session):
        """Test anomaly detection with insufficient data."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.return_value.query.return_value = mock_query

        # Only 2 accounts (insufficient for z-score)
        mock_accounts = [
            Mock(category="Assets", debit_balance=10000, credit_balance=0),
            Mock(category="Assets", debit_balance=12000, credit_balance=0),
        ]
        mock_query.all.return_value = mock_accounts

        result = identify_anomalies_ml("Entity001", "2024-03")

        assert "error" in result or result["anomaly_count"] == 0


class TestExportFunctions:
    """Tests for export functions."""

    def test_export_analytics_to_csv(self, tmp_path):
        """Test CSV export."""
        analytics_dict = {
            "total_balance": 100000,
            "by_category": {"Assets": 50000, "Liabilities": 50000},
        }

        output_path = tmp_path / "test_export.csv"
        result = export_analytics_to_csv(analytics_dict, str(output_path))

        assert result == str(output_path)
        assert output_path.exists()

    def test_export_analytics_to_excel(self, tmp_path):
        """Test Excel export."""
        analytics_dict = {
            "summary": {"total": 100000},
            "details": [{"account": "100000", "balance": 50000}],
        }

        output_path = tmp_path / "test_export.xlsx"
        result = export_analytics_to_excel(analytics_dict, str(output_path))

        assert result == str(output_path)
        assert output_path.exists()

    def test_export_invalid_path(self):
        """Test export with invalid path."""
        analytics_dict = {"test": "data"}

        # Try to write to invalid path
        result = export_analytics_to_csv(analytics_dict, "/invalid/path/file.csv")

        # Should handle error gracefully
        assert result is not None  # Function should not crash


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.analytics", "--cov-report=term-missing"])
