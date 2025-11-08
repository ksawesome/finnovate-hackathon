"""
Reviewer Performance Report Generator

Generates reviewer productivity and workload analysis with performance rankings,
bottleneck detection, and capacity utilization metrics.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.db import get_postgres_session
from src.db.postgres import User, get_gl_accounts_by_entity_period, get_responsibility_assignments
from src.reports import BaseReport, register_report


@register_report("reviewer_performance")
class ReviewerPerformanceReport(BaseReport):
    """Generate reviewer performance and productivity report."""

    def generate(self) -> dict[str, str]:
        """
        Generate reviewer performance report in PDF and CSV formats.

        Returns:
            Dict with 'pdf' and 'csv' keys mapping to file paths
        """
        self.generated_at = datetime.now()

        # Fetch data
        data = self._fetch_data()

        # Generate PDF report
        pdf_path = self._generate_pdf(data)
        self.generated_files["pdf"] = str(pdf_path)

        # Generate CSV export
        csv_path = self._generate_csv(data)
        self.generated_files["csv"] = str(csv_path)

        return self.generated_files

    def _fetch_data(self) -> dict:
        """Fetch reviewer assignments and performance metrics."""
        session = get_postgres_session()

        try:
            # Get all responsibility assignments for this entity/period
            assignments = get_responsibility_assignments(session, self.entity, self.period)

            # Get all GL accounts for context
            accounts = get_gl_accounts_by_entity_period(session, self.entity, self.period)

            # Build reviewer metrics
            reviewer_metrics = self._calculate_reviewer_metrics(session, assignments, accounts)

            # Get all reviewers (users)
            all_reviewers = session.query(User).all()

            return {
                "reviewer_metrics": reviewer_metrics,
                "assignments": assignments,
                "accounts": accounts,
                "all_reviewers": all_reviewers,
                "entity": self.entity,
                "period": self.period,
                "generated_at": self.generated_at,
            }
        except Exception as e:
            return {
                "error": str(e),
                "entity": self.entity,
                "period": self.period,
                "generated_at": self.generated_at,
            }
        finally:
            session.close()

    def _calculate_reviewer_metrics(self, session, assignments: list, accounts: list) -> list[dict]:
        """Calculate performance metrics for each reviewer."""
        reviewer_data = {}

        # Build account map for quick lookup
        account_map = {acc.id: acc for acc in accounts}

        # Aggregate by reviewer
        for assignment in assignments:
            reviewer_id = assignment.reviewer_id
            reviewer_name = assignment.reviewer.full_name if assignment.reviewer else "Unknown"

            if reviewer_id not in reviewer_data:
                reviewer_data[reviewer_id] = {
                    "reviewer_id": reviewer_id,
                    "reviewer_name": reviewer_name,
                    "total_assigned": 0,
                    "reviewed": 0,
                    "pending": 0,
                    "flagged": 0,
                    "total_balance": 0,
                    "critical_items": 0,
                    "avg_balance": 0,
                }

            reviewer_data[reviewer_id]["total_assigned"] += 1

            # Get account details
            account = account_map.get(assignment.gl_account_id)
            if account:
                # Count by status
                if account.review_status == "reviewed":
                    reviewer_data[reviewer_id]["reviewed"] += 1
                elif account.review_status == "pending":
                    reviewer_data[reviewer_id]["pending"] += 1

                if account.flagged:
                    reviewer_data[reviewer_id]["flagged"] += 1

                if account.criticality in ["High", "Critical"]:
                    reviewer_data[reviewer_id]["critical_items"] += 1

                # Aggregate balance
                balance = getattr(account, "closing_balance", 0) or 0
                reviewer_data[reviewer_id]["total_balance"] += balance

        # Calculate derived metrics
        metrics_list = []
        for reviewer_id, metrics in reviewer_data.items():
            if metrics["total_assigned"] > 0:
                metrics["completion_rate"] = metrics["reviewed"] / metrics["total_assigned"] * 100
                metrics["avg_balance"] = metrics["total_balance"] / metrics["total_assigned"]
            else:
                metrics["completion_rate"] = 0
                metrics["avg_balance"] = 0

            # Productivity score (weighted)
            # Formula: 40% completion rate + 30% workload + 20% critical handling + 10% flagged resolution
            completion_weight = metrics["completion_rate"] * 0.4

            # Normalize workload (assume 50 items is 100% capacity)
            workload_score = min(metrics["total_assigned"] / 50 * 100, 100) * 0.3

            # Critical handling (assume handling 10 critical items is 100%)
            critical_score = min(metrics["critical_items"] / 10 * 100, 100) * 0.2

            # Flagged resolution (inverse - fewer flagged is better)
            flagged_ratio = (
                metrics["flagged"] / metrics["total_assigned"]
                if metrics["total_assigned"] > 0
                else 0
            )
            flagged_score = max(100 - (flagged_ratio * 100), 0) * 0.1

            metrics["productivity_score"] = (
                completion_weight + workload_score + critical_score + flagged_score
            )

            # Bottleneck detection
            if metrics["pending"] > 20:
                metrics["bottleneck"] = "High"
            elif metrics["pending"] > 10:
                metrics["bottleneck"] = "Medium"
            else:
                metrics["bottleneck"] = "Low"

            metrics_list.append(metrics)

        # Sort by productivity score (descending)
        metrics_list.sort(key=lambda x: x["productivity_score"], reverse=True)

        # Add ranking
        for rank, metrics in enumerate(metrics_list, start=1):
            metrics["rank"] = rank

        return metrics_list

    def _generate_pdf(self, data: dict) -> Path:
        """Generate PDF performance report."""
        output_path = self._get_output_path("pdf")

        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=20,
            textColor=colors.HexColor("#8e44ad"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )

        elements.append(Paragraph("Reviewer Performance Report", title_style))
        elements.append(
            Paragraph(f"Entity: {data['entity']} | Period: {data['period']}", styles["Normal"])
        )
        elements.append(Spacer(1, 0.3 * inch))

        # Check for error
        if "error" in data:
            elements.append(Paragraph(f"Error: {data['error']}", styles["Normal"]))
            doc.build(elements)
            return output_path

        reviewer_metrics = data.get("reviewer_metrics", [])

        # Summary Statistics
        elements.append(Paragraph("Summary Statistics", styles["Heading2"]))

        total_reviewers = len(reviewer_metrics)
        total_assigned = sum(m["total_assigned"] for m in reviewer_metrics)
        total_reviewed = sum(m["reviewed"] for m in reviewer_metrics)
        overall_completion = (total_reviewed / total_assigned * 100) if total_assigned > 0 else 0

        summary_data = [
            ["Metric", "Value"],
            ["Active Reviewers", str(total_reviewers)],
            ["Total Items Assigned", str(total_assigned)],
            ["Items Reviewed", str(total_reviewed)],
            ["Overall Completion Rate", f"{overall_completion:.1f}%"],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 3 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8e44ad")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 1), (1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Top Performers
        elements.append(Paragraph("Top Performers", styles["Heading2"]))

        top_performers = reviewer_metrics[:10]  # Top 10

        perf_data = [
            ["Rank", "Reviewer", "Assigned", "Reviewed", "Completion %", "Productivity Score"]
        ]

        for metrics in top_performers:
            perf_data.append(
                [
                    str(metrics["rank"]),
                    metrics["reviewer_name"][:25],
                    str(metrics["total_assigned"]),
                    str(metrics["reviewed"]),
                    f"{metrics['completion_rate']:.1f}%",
                    f"{metrics['productivity_score']:.1f}",
                ]
            )

        perf_table = Table(
            perf_data,
            colWidths=[0.6 * inch, 2 * inch, 0.9 * inch, 0.9 * inch, 1 * inch, 1.1 * inch],
        )
        perf_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27ae60")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (2, 1), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        elements.append(perf_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Workload Distribution
        elements.append(Paragraph("Workload Distribution", styles["Heading2"]))

        workload_data = [["Reviewer", "Total Assigned", "Pending", "Bottleneck Status"]]

        for metrics in reviewer_metrics:
            workload_data.append(
                [
                    metrics["reviewer_name"][:30],
                    str(metrics["total_assigned"]),
                    str(metrics["pending"]),
                    metrics["bottleneck"],
                ]
            )

        workload_table = Table(
            workload_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch]
        )
        workload_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 1), (2, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        elements.append(workload_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Bottleneck Analysis
        elements.append(Paragraph("Bottleneck Detection", styles["Heading2"]))

        high_bottlenecks = [m for m in reviewer_metrics if m["bottleneck"] == "High"]
        medium_bottlenecks = [m for m in reviewer_metrics if m["bottleneck"] == "Medium"]

        if high_bottlenecks:
            elements.append(
                Paragraph(
                    f"<b>🔴 High Priority:</b> {len(high_bottlenecks)} reviewers with >20 pending items",
                    styles["Normal"],
                )
            )
            for metrics in high_bottlenecks[:5]:
                elements.append(
                    Paragraph(
                        f"• {metrics['reviewer_name']}: {metrics['pending']} pending items",
                        styles["Normal"],
                    )
                )

        if medium_bottlenecks:
            elements.append(Spacer(1, 0.1 * inch))
            elements.append(
                Paragraph(
                    f"<b>⚠ Medium Priority:</b> {len(medium_bottlenecks)} reviewers with 10-20 pending items",
                    styles["Normal"],
                )
            )

        if not high_bottlenecks and not medium_bottlenecks:
            elements.append(Paragraph("✓ No significant bottlenecks detected.", styles["Normal"]))

        elements.append(Spacer(1, 0.3 * inch))

        # Recommendations
        elements.append(Paragraph("Recommendations", styles["Heading2"]))

        recommendations = self._generate_recommendations(reviewer_metrics)

        rec_style = ParagraphStyle(
            "Recommendations", parent=styles["Normal"], leftIndent=20, spaceAfter=10
        )

        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", rec_style))

        # Footer
        elements.append(Spacer(1, 0.3 * inch))
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )
        elements.append(
            Paragraph(
                f"Generated by Project Aura | {data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}",
                footer_style,
            )
        )

        # Build PDF
        doc.build(elements)

        return output_path

    def _generate_recommendations(self, reviewer_metrics: list[dict]) -> list[str]:
        """Generate actionable recommendations based on performance data."""
        recommendations = []

        if not reviewer_metrics:
            return ["No reviewer data available for analysis."]

        # Workload imbalance
        assignments = [m["total_assigned"] for m in reviewer_metrics]
        avg_assignment = sum(assignments) / len(assignments)
        max_assignment = max(assignments)
        min_assignment = min(assignments)

        if max_assignment > avg_assignment * 2:
            recommendations.append(
                f"Workload imbalance detected. Maximum assignment ({max_assignment}) is "
                f"significantly higher than average ({avg_assignment:.0f}). "
                "Consider redistributing work to balance capacity."
            )

        # Low completion rates
        low_performers = [m for m in reviewer_metrics if m["completion_rate"] < 50]
        if low_performers:
            recommendations.append(
                f"{len(low_performers)} reviewers have completion rates below 50%. "
                "Provide additional training or support to improve productivity."
            )

        # High bottlenecks
        high_bottlenecks = [m for m in reviewer_metrics if m["bottleneck"] == "High"]
        if high_bottlenecks:
            recommendations.append(
                f"Address bottlenecks for {len(high_bottlenecks)} reviewers with >20 pending items. "
                "Reassign work or provide temporary support to clear backlog."
            )

        # Flagged items concentration
        high_flagged = [m for m in reviewer_metrics if m["flagged"] > 10]
        if high_flagged:
            recommendations.append(
                f"{len(high_flagged)} reviewers have >10 flagged items. "
                "Investigate root causes and provide targeted guidance."
            )

        # Positive feedback
        if not recommendations:
            recommendations.append(
                "Overall performance is balanced and healthy. "
                "Continue monitoring for any emerging bottlenecks."
            )
            recommendations.append("Recognize top performers to maintain high productivity levels.")

        return recommendations

    def _generate_csv(self, data: dict) -> Path:
        """Generate CSV export of reviewer metrics."""
        output_path = self._get_output_path("csv")

        reviewer_metrics = data.get("reviewer_metrics", [])

        if reviewer_metrics:
            df = pd.DataFrame(reviewer_metrics)

            # Select and order columns
            columns = [
                "rank",
                "reviewer_name",
                "total_assigned",
                "reviewed",
                "pending",
                "flagged",
                "critical_items",
                "completion_rate",
                "productivity_score",
                "bottleneck",
                "total_balance",
                "avg_balance",
            ]

            df = df[columns]

            # Rename for clarity
            df.columns = [
                "Rank",
                "Reviewer Name",
                "Total Assigned",
                "Reviewed",
                "Pending",
                "Flagged Items",
                "Critical Items",
                "Completion Rate (%)",
                "Productivity Score",
                "Bottleneck Status",
                "Total Balance (₹)",
                "Avg Balance (₹)",
            ]

            df.to_csv(output_path, index=False)
        else:
            # Empty DataFrame
            pd.DataFrame(
                columns=["Rank", "Reviewer Name", "Total Assigned", "Reviewed", "Pending"]
            ).to_csv(output_path, index=False)

        return output_path
