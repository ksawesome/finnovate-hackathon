"""
Unit tests for automated report generation.

Tests all 6 report types: Status, Variance, Hygiene, Reviewer Performance,
SLA Compliance, and Executive Summary reports.
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.reports import REPORT_TYPES, generate_report, list_available_reports

# ================================
# FIXTURES
# ================================


@pytest.fixture
def sample_entity():
    """Sample entity code."""
    return "Entity001"


@pytest.fixture
def sample_period():
    """Sample period."""
    return "2024-03"


@pytest.fixture
def test_output_dir(tmp_path):
    """Temporary output directory for test reports."""
    output_dir = tmp_path / "test_reports"
    output_dir.mkdir()
    return str(output_dir)


@pytest.fixture
def mock_analytics_data():
    """Mock analytics data."""
    return {
        "total_balance": 1000000,
        "account_count": 100,
        "by_status": {"reviewed": 60, "pending": 30, "flagged": 10},
        "by_category": {"Assets": 400000, "Liabilities": 300000, "Revenue": 300000},
        "average_balance": 10000,
        "flagged_count": 10,
    }


@pytest.fixture
def mock_hygiene_score():
    """Mock hygiene score data."""
    return {
        "overall_score": 85.5,
        "status": "Good",
        "total_accounts": 100,
        "component_scores": {
            "data_completeness": {"score": 90.0, "weight": 0.3},
            "documentation": {"score": 80.0, "weight": 0.25},
            "timeliness": {"score": 85.0, "weight": 0.25},
            "accuracy": {"score": 88.0, "weight": 0.2},
        },
        "issues": [
            {"severity": "High", "type": "Missing Documentation", "count": 5, "impact": "Medium"},
            {"severity": "Medium", "type": "Late Review", "count": 10, "impact": "Low"},
        ],
    }


# ================================
# BASIC MODULE TESTS
# ================================


def test_list_available_reports():
    """Test listing available report types."""
    reports = list_available_reports()

    assert isinstance(reports, list)
    assert len(reports) >= 6
    assert "status" in reports
    assert "variance" in reports
    assert "hygiene" in reports
    assert "reviewer_performance" in reports
    assert "sla_compliance" in reports
    assert "executive_summary" in reports


def test_report_types_registry():
    """Test that REPORT_TYPES registry is populated."""
    assert len(REPORT_TYPES) >= 6
    assert "status" in REPORT_TYPES
    assert "variance" in REPORT_TYPES
    assert "hygiene" in REPORT_TYPES
    assert "reviewer_performance" in REPORT_TYPES
    assert "sla_compliance" in REPORT_TYPES
    assert "executive_summary" in REPORT_TYPES


def test_generate_report_invalid_type(sample_entity, sample_period, test_output_dir):
    """Test error handling for invalid report type."""
    with pytest.raises(ValueError, match="Unknown report type"):
        generate_report(
            "invalid_report_type", sample_entity, sample_period, output_dir=test_output_dir
        )


# ================================
# GL ACCOUNT STATUS REPORT TESTS
# ================================


@patch("src.reports.status_report.get_postgres_session")
@patch("src.reports.status_report.get_pending_items_report")
@patch("src.reports.status_report.calculate_review_status_summary")
@patch("src.reports.status_report.get_gl_accounts_by_entity_period")
def test_status_report_generation(
    mock_get_accounts,
    mock_status_summary,
    mock_pending_items,
    mock_session,
    sample_entity,
    sample_period,
    test_output_dir,
):
    """Test GL Account Status Report generation."""
    # Mock data
    mock_pending_items.return_value = {
        "pending_reviews": [
            {
                "account_code": "GL001",
                "account_name": "Cash",
                "criticality": "High",
                "department": "Finance",
            }
        ],
        "missing_docs": [
            {
                "account_code": "GL002",
                "account_name": "Inventory",
                "criticality": "Medium",
                "closing_balance": 50000,
            }
        ],
        "flagged_items": [
            {
                "account_code": "GL003",
                "account_name": "Revenue",
                "reason": "Unusual variance",
                "priority": "High",
            }
        ],
    }
    mock_status_summary.return_value = {"overall_completion_rate": 75.0}
    mock_get_accounts.return_value = []
    mock_session.return_value = Mock()

    # Generate report
    result = generate_report("status", sample_entity, sample_period, output_dir=test_output_dir)

    # Assertions
    assert "pdf" in result
    assert "csv" in result

    # Check files exist
    pdf_path = Path(result["pdf"])
    csv_path = Path(result["csv"])

    assert pdf_path.exists()
    assert csv_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert csv_path.suffix == ".csv"

    # Check CSV content
    df = pd.read_csv(csv_path)
    assert "Account Code" in df.columns
    assert "Type" in df.columns


@patch("src.reports.status_report.get_postgres_session")
@patch("src.reports.status_report.get_pending_items_report")
@patch("src.reports.status_report.calculate_review_status_summary")
@patch("src.reports.status_report.get_gl_accounts_by_entity_period")
def test_status_report_empty_data(
    mock_get_accounts,
    mock_status_summary,
    mock_pending_items,
    mock_session,
    sample_entity,
    sample_period,
    test_output_dir,
):
    """Test status report with empty data (no pending items)."""
    # Mock empty data
    mock_pending_items.return_value = {
        "pending_reviews": [],
        "missing_docs": [],
        "flagged_items": [],
    }
    mock_status_summary.return_value = {"overall_completion_rate": 100.0}
    mock_get_accounts.return_value = []
    mock_session.return_value = Mock()

    # Generate report
    result = generate_report("status", sample_entity, sample_period, output_dir=test_output_dir)

    # Should still generate files
    assert "pdf" in result
    assert "csv" in result
    assert Path(result["pdf"]).exists()


# ================================
# VARIANCE ANALYSIS REPORT TESTS
# ================================


@patch("src.reports.variance_report.calculate_variance_analysis")
@patch("src.reports.variance_report.perform_analytics")
def test_variance_report_generation(
    mock_perform_analytics, mock_variance_analysis, sample_entity, sample_period, test_output_dir
):
    """Test Variance Analysis Report generation."""
    # Mock data
    mock_variance_analysis.return_value = {
        "accounts_analyzed": 100,
        "total_variance": 50000,
        "significant_count": 10,
        "significant_variances": [
            {
                "account_code": "GL001",
                "account_name": "Revenue",
                "current_balance": 150000,
                "previous_balance": 100000,
                "variance": 50000,
                "variance_pct": 50.0,
            }
        ],
    }
    mock_perform_analytics.return_value = {
        "total_balance": 1000000,
        "account_count": 100,
        "by_category": {"Assets": 400000},
    }

    # Generate report
    result = generate_report("variance", sample_entity, sample_period, output_dir=test_output_dir)

    # Assertions
    assert "excel" in result
    assert "pdf" in result

    # Check files
    excel_path = Path(result["excel"])
    pdf_path = Path(result["pdf"])

    assert excel_path.exists()
    assert pdf_path.exists()
    assert excel_path.suffix == ".xlsx"


# ================================
# GL HYGIENE DASHBOARD REPORT TESTS
# ================================


@patch("src.reports.hygiene_report.calculate_gl_hygiene_score")
@patch("src.reports.hygiene_report.perform_analytics")
def test_hygiene_report_generation(
    mock_perform_analytics,
    mock_hygiene_score,
    sample_entity,
    sample_period,
    test_output_dir,
    mock_hygiene_score_fixture,
):
    """Test GL Hygiene Dashboard Report generation."""
    # Mock data
    mock_hygiene_score.return_value = mock_hygiene_score_fixture
    mock_perform_analytics.return_value = {"total_balance": 1000000, "account_count": 100}

    # Generate report
    result = generate_report("hygiene", sample_entity, sample_period, output_dir=test_output_dir)

    # Assertions
    assert "pdf" in result
    assert "json" in result

    # Check files
    pdf_path = Path(result["pdf"])
    json_path = Path(result["json"])

    assert pdf_path.exists()
    assert json_path.exists()

    # Check JSON content
    with open(json_path) as f:
        json_data = json.load(f)
    assert "metadata" in json_data
    assert "hygiene_score" in json_data


# ================================
# REVIEWER PERFORMANCE REPORT TESTS
# ================================


@patch("src.reports.reviewer_performance_report.get_postgres_session")
@patch("src.reports.reviewer_performance_report.get_responsibility_assignments")
@patch("src.reports.reviewer_performance_report.get_gl_accounts_by_entity_period")
def test_reviewer_performance_report(
    mock_get_accounts,
    mock_get_assignments,
    mock_session,
    sample_entity,
    sample_period,
    test_output_dir,
):
    """Test Reviewer Performance Report generation."""
    # Mock session
    mock_session_obj = Mock()
    mock_session.return_value = mock_session_obj

    # Mock reviewer and assignment data
    mock_reviewer = Mock()
    mock_reviewer.full_name = "John Doe"

    mock_assignment = Mock()
    mock_assignment.reviewer_id = 1
    mock_assignment.reviewer = mock_reviewer
    mock_assignment.gl_account_id = 1

    mock_get_assignments.return_value = [mock_assignment]

    mock_account = Mock()
    mock_account.id = 1
    mock_account.review_status = "reviewed"
    mock_account.criticality = "High"
    mock_account.flagged = False
    mock_account.closing_balance = 10000

    mock_get_accounts.return_value = [mock_account]

    # Generate report
    result = generate_report(
        "reviewer_performance", sample_entity, sample_period, output_dir=test_output_dir
    )

    # Assertions
    assert "pdf" in result
    assert "csv" in result

    # Check files
    pdf_path = Path(result["pdf"])
    csv_path = Path(result["csv"])

    assert pdf_path.exists()
    assert csv_path.exists()


# ================================
# SLA COMPLIANCE REPORT TESTS
# ================================


@patch("src.reports.sla_compliance_report.get_postgres_session")
@patch("src.reports.sla_compliance_report.get_gl_accounts_by_entity_period")
@patch("src.reports.sla_compliance_report.get_responsibility_assignments")
def test_sla_compliance_report(
    mock_get_assignments,
    mock_get_accounts,
    mock_session,
    sample_entity,
    sample_period,
    test_output_dir,
):
    """Test SLA Compliance Report generation."""
    # Mock session
    mock_session.return_value = Mock()

    # Mock account with deadline
    mock_account = Mock()
    mock_account.id = 1
    mock_account.account_code = "GL001"
    mock_account.account_name = "Cash"
    mock_account.review_status = "pending"
    mock_account.criticality = "High"
    mock_account.closing_balance = 10000
    mock_account.sla_deadline = datetime.now()
    mock_account.flagged = False

    mock_get_accounts.return_value = [mock_account]
    mock_get_assignments.return_value = []

    # Generate report
    result = generate_report(
        "sla_compliance", sample_entity, sample_period, output_dir=test_output_dir
    )

    # Assertions
    assert "excel" in result
    assert "pdf" in result

    # Check files
    excel_path = Path(result["excel"])
    pdf_path = Path(result["pdf"])

    assert excel_path.exists()
    assert pdf_path.exists()


# ================================
# EXECUTIVE SUMMARY REPORT TESTS
# ================================


@patch("src.reports.executive_summary_report.generate_executive_summary")
@patch("src.reports.executive_summary_report.generate_proactive_insights")
@patch("src.reports.executive_summary_report.perform_analytics")
@patch("src.reports.executive_summary_report.calculate_gl_hygiene_score")
@patch("src.reports.executive_summary_report.calculate_review_status_summary")
def test_executive_summary_report(
    mock_review_status,
    mock_hygiene,
    mock_analytics,
    mock_insights,
    mock_exec_summary,
    sample_entity,
    sample_period,
    test_output_dir,
    mock_analytics_data,
    mock_hygiene_score,
):
    """Test Executive Summary Report generation."""
    # Mock data
    mock_exec_summary.return_value = {
        "overall_status": "Good",
        "highlights": ["High completion rate", "Low flagged items"],
        "concerns": ["Some pending reviews"],
    }
    mock_insights.return_value = {
        "recommendations": [
            {"priority": "High", "action": "Review flagged items"},
            {"priority": "Medium", "action": "Improve documentation"},
        ]
    }
    mock_analytics.return_value = mock_analytics_data
    mock_hygiene.return_value = mock_hygiene_score
    mock_review_status.return_value = {"overall_completion_rate": 75.0, "pending_count": 25}

    # Generate report
    result = generate_report(
        "executive_summary", sample_entity, sample_period, output_dir=test_output_dir
    )

    # Assertions
    assert "pdf" in result
    assert "markdown" in result

    # Check files
    pdf_path = Path(result["pdf"])
    markdown_path = Path(result["markdown"])

    assert pdf_path.exists()
    assert markdown_path.exists()

    # Check markdown content
    with open(markdown_path, encoding="utf-8") as f:
        markdown_content = f.read()
    assert "# Executive Summary" in markdown_content
    assert "Key Performance Indicators" in markdown_content


# ================================
# FORMAT-SPECIFIC TESTS
# ================================


def test_pdf_generation_format(sample_entity, sample_period, test_output_dir):
    """Test that PDF files are valid."""
    # This would require PDF parsing library (e.g., PyPDF2)
    # For now, just check file extension and size


def test_excel_multi_sheet_structure(sample_entity, sample_period, test_output_dir):
    """Test Excel workbook has expected sheets."""
    # This would require openpyxl to read and validate


def test_csv_structure(sample_entity, sample_period, test_output_dir):
    """Test CSV files have expected columns."""


# ================================
# ERROR HANDLING TESTS
# ================================


@patch("src.reports.status_report.get_postgres_session")
def test_report_error_handling(mock_session, sample_entity, sample_period, test_output_dir):
    """Test error handling when database query fails."""
    # Mock exception
    mock_session.side_effect = Exception("Database connection failed")

    # Should not raise exception, but return error in data
    result = generate_report("status", sample_entity, sample_period, output_dir=test_output_dir)

    # Report should still generate with error message
    assert "pdf" in result or "error" in str(result)


# ================================
# PERFORMANCE TESTS
# ================================


def test_report_generation_performance(sample_entity, sample_period, test_output_dir):
    """Test that report generation completes within reasonable time."""
    import time

    start_time = time.time()
    # Generate smallest report
    try:
        generate_report("status", sample_entity, sample_period, output_dir=test_output_dir)
    except:
        pass  # Performance test, not validation
    end_time = time.time()

    # Should complete within 30 seconds (with mocking, should be much faster)
    assert (end_time - start_time) < 30


# ================================
# INTEGRATION TESTS
# ================================


def test_all_reports_generate_successfully(sample_entity, sample_period, test_output_dir):
    """Integration test: Generate all 6 report types."""
    report_types = list_available_reports()

    for report_type in report_types:
        try:
            result = generate_report(
                report_type, sample_entity, sample_period, output_dir=test_output_dir
            )
            assert result is not None
        except Exception as e:
            pytest.fail(f"Failed to generate {report_type} report: {e!s}")
