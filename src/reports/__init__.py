"""
Report Generation Module

Automated report generation engine for GL account analysis, variance reports,
hygiene dashboards, reviewer performance, SLA compliance, and executive summaries.
"""

from pathlib import Path
from typing import Any, Dict, Literal

# Report type registry
REPORT_TYPES = {}


def register_report(report_type: str):
    """Decorator to register report classes."""

    def decorator(cls):
        REPORT_TYPES[report_type] = cls
        return cls

    return decorator


def generate_report(
    kind: Literal[
        "status", "variance", "hygiene", "reviewer_performance", "sla", "executive_summary"
    ],
    entity: str,
    period: str,
    output_dir: str = "data/reports",
    **kwargs,
) -> dict[str, str]:
    """
    Generate a report of specified type.

    Args:
        kind: Report type identifier
        entity: Entity code (e.g., "Entity001")
        period: Period in YYYY-MM format
        output_dir: Output directory for generated files
        **kwargs: Additional report-specific parameters

    Returns:
        Dict mapping format to file path (e.g., {'pdf': 'path/to/report.pdf'})

    Raises:
        ValueError: If report kind is not recognized

    Example:
        >>> files = generate_report('status', 'Entity001', '2024-03')
        >>> print(files['pdf'])  # Path to generated PDF
    """
    if kind not in REPORT_TYPES:
        raise ValueError(
            f"Unknown report type: {kind}. " f"Supported types: {list(REPORT_TYPES.keys())}"
        )

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Instantiate and generate report
    report_class = REPORT_TYPES[kind]
    report = report_class(entity=entity, period=period, output_dir=output_dir, **kwargs)

    return report.generate()


def list_available_reports() -> list:
    """List all available report types."""
    return list(REPORT_TYPES.keys())


# Base report class
class BaseReport:
    """Base class for all report types."""

    def __init__(self, entity: str, period: str, output_dir: str = "data/reports", **kwargs):
        """
        Initialize report.

        Args:
            entity: Entity code
            period: Period (YYYY-MM)
            output_dir: Output directory
            **kwargs: Additional parameters
        """
        self.entity = entity
        self.period = period
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.kwargs = kwargs

        # Report metadata
        self.report_type = self.__class__.__name__
        self.generated_at = None
        self.generated_files = {}

    def generate(self) -> dict[str, str]:
        """
        Generate report in all supported formats.

        Returns:
            Dict mapping format to file path

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def _get_output_path(self, format: str, suffix: str = "") -> Path:
        """
        Get output file path for given format.

        Args:
            format: File format (pdf, csv, excel, json, png, md)
            suffix: Optional suffix for filename

        Returns:
            Path object
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.report_type}_{self.entity}_{self.period}"
        if suffix:
            filename += f"_{suffix}"
        filename += f"_{timestamp}.{format}"
        return self.output_dir / filename


# Import report classes (will be available after implementation)
try:
    from .executive_summary_report import ExecutiveSummaryReport
    from .hygiene_report import GLHygieneDashboardReport
    from .reviewer_performance_report import ReviewerPerformanceReport
    from .sla_compliance_report import SLAComplianceReport
    from .status_report import GLAccountStatusReport
    from .variance_report import VarianceAnalysisReport
except ImportError:
    # Reports not yet implemented
    pass


__all__ = [
    "generate_report",
    "list_available_reports",
    "BaseReport",
    "REPORT_TYPES",
]
