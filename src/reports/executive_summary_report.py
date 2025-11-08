"""
Executive Summary Report Generator

Generates concise one-page leadership dashboard with key metrics,
highlights, concerns, and strategic recommendations.
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.analytics import (
    calculate_gl_hygiene_score,
    calculate_review_status_summary,
    perform_analytics,
)
from src.insights import generate_executive_summary, generate_proactive_insights
from src.reports import BaseReport, register_report
from src.visualizations import create_hygiene_gauge, export_chart_to_png


@register_report("executive_summary")
class ExecutiveSummaryReport(BaseReport):
    """Generate concise executive summary for leadership."""

    def generate(self) -> dict[str, str]:
        """
        Generate executive summary in PDF, Markdown, and PNG formats.

        Returns:
            Dict with 'pdf', 'markdown', and 'png' keys mapping to file paths
        """
        self.generated_at = datetime.now()

        # Fetch data
        data = self._fetch_data()

        # Generate PDF (primary - one page A4)
        pdf_path = self._generate_pdf(data)
        self.generated_files["pdf"] = str(pdf_path)

        # Generate Markdown version
        markdown_path = self._generate_markdown(data)
        self.generated_files["markdown"] = str(markdown_path)

        # Generate PNG charts
        if "hygiene_score" in data and not data["hygiene_score"].get("error"):
            png_path = self._generate_png(data)
            self.generated_files["png"] = str(png_path)

        return self.generated_files

    def _fetch_data(self) -> dict:
        """Fetch executive-level data from all sources."""
        try:
            # Get executive summary from insights
            exec_summary = generate_executive_summary(self.entity, self.period)

            # Get proactive insights
            insights = generate_proactive_insights(self.entity, self.period)

            # Get analytics
            analytics = perform_analytics(self.entity, self.period)

            # Get hygiene score
            hygiene_score = calculate_gl_hygiene_score(self.entity, self.period)

            # Get review status
            review_status = calculate_review_status_summary(self.entity, self.period)

            return {
                "executive_summary": exec_summary,
                "insights": insights,
                "analytics": analytics,
                "hygiene_score": hygiene_score,
                "review_status": review_status,
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

    def _generate_pdf(self, data: dict) -> Path:
        """Generate one-page executive summary PDF (A4)."""
        output_path = self._get_output_path("pdf")

        # Use A4 size for executive reporting
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )

        elements = []
        styles = getSampleStyleSheet()

        # Custom styles for compact layout
        title_style = ParagraphStyle(
            "ExecTitle",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )

        section_style = ParagraphStyle(
            "ExecSection",
            parent=styles["Heading2"],
            fontSize=12,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=6,
            spaceBefore=6,
            fontName="Helvetica-Bold",
        )

        body_style = ParagraphStyle(
            "ExecBody", parent=styles["Normal"], fontSize=9, spaceAfter=4, leading=11
        )

        # Header
        elements.append(Paragraph("Executive Summary", title_style))
        elements.append(
            Paragraph(
                f"{data['entity']} | {data['period']} | Generated: {data['generated_at'].strftime('%Y-%m-%d')}",
                body_style,
            )
        )
        elements.append(Spacer(1, 0.15 * inch))

        # Check for error
        if "error" in data:
            elements.append(Paragraph(f"Error: {data['error']}", body_style))
            doc.build(elements)
            return output_path

        # Key Metrics Cards (3x2 grid)
        elements.append(Paragraph("Key Performance Indicators", section_style))

        analytics = data.get("analytics", {})
        hygiene_score = data.get("hygiene_score", {})
        review_status = data.get("review_status", {})

        metrics_data = [
            [
                self._create_metric_cell(
                    "Total Balance", f"₹{analytics.get('total_balance', 0):,.0f}"
                ),
                self._create_metric_cell("Account Count", str(analytics.get("account_count", 0))),
                self._create_metric_cell(
                    "Hygiene Score", f"{hygiene_score.get('overall_score', 0):.0f}%"
                ),
            ],
            [
                self._create_metric_cell(
                    "Completion Rate", f"{review_status.get('overall_completion_rate', 0):.0f}%"
                ),
                self._create_metric_cell(
                    "Pending Reviews", str(review_status.get("pending_count", 0))
                ),
                self._create_metric_cell("Flagged Items", str(analytics.get("flagged_count", 0))),
            ],
        ]

        # Flatten for table
        metrics_table_data = []
        for row in metrics_data:
            metrics_table_data.append(row)

        metrics_table = Table(metrics_table_data, colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch])
        metrics_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 1.5, colors.HexColor("#bdc3c7")),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ecf0f1")),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        elements.append(metrics_table)
        elements.append(Spacer(1, 0.12 * inch))

        # Executive Summary Section (from insights)
        exec_summary = data.get("executive_summary", {})

        # Highlights
        elements.append(Paragraph("Key Highlights", section_style))
        highlights = exec_summary.get("highlights", [])
        if highlights:
            for highlight in highlights[:4]:  # Top 4 highlights
                elements.append(Paragraph(f"✓ {highlight}", body_style))
        else:
            elements.append(Paragraph("No highlights available.", body_style))

        elements.append(Spacer(1, 0.1 * inch))

        # Concerns
        elements.append(Paragraph("Areas of Concern", section_style))
        concerns = exec_summary.get("concerns", [])
        if concerns:
            for concern in concerns[:4]:  # Top 4 concerns
                elements.append(Paragraph(f"⚠ {concern}", body_style))
        else:
            elements.append(Paragraph("✓ No major concerns identified.", body_style))

        elements.append(Spacer(1, 0.1 * inch))

        # Strategic Recommendations (from insights)
        elements.append(Paragraph("Strategic Recommendations", section_style))

        insights = data.get("insights", {})
        recommendations = insights.get("recommendations", [])

        if recommendations:
            for rec in recommendations[:5]:  # Top 5 recommendations
                priority = rec.get("priority", "Medium")
                action = rec.get("action", "N/A")

                if priority == "High":
                    priority_marker = "🔴"
                elif priority == "Medium":
                    priority_marker = "⚠"
                else:
                    priority_marker = "•"

                elements.append(
                    Paragraph(f"{priority_marker} <b>[{priority}]</b> {action}", body_style)
                )
        else:
            elements.append(Paragraph("Continue current practices.", body_style))

        elements.append(Spacer(1, 0.1 * inch))

        # Status Summary Table (compact)
        elements.append(Paragraph("Status Breakdown", section_style))

        by_status = analytics.get("by_status", {})
        status_data = [["Status", "Count", "Status", "Count"]]

        status_items = list(by_status.items())
        for i in range(0, len(status_items), 2):
            row = []
            row.append(status_items[i][0].title())
            row.append(str(status_items[i][1]))
            if i + 1 < len(status_items):
                row.append(status_items[i + 1][0].title())
                row.append(str(status_items[i + 1][1]))
            else:
                row.extend(["", ""])
            status_data.append(row)

        status_table = Table(
            status_data, colWidths=[1.5 * inch, 0.8 * inch, 1.5 * inch, 0.8 * inch]
        )
        status_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 1), (1, -1), "CENTER"),
                    ("ALIGN", (3, 1), (3, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        elements.append(status_table)

        # Footer
        elements.append(Spacer(1, 0.1 * inch))
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=7,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )
        elements.append(
            Paragraph("Project Aura - Automated GL Review System | Confidential", footer_style)
        )

        # Build PDF (single page)
        doc.build(elements)

        return output_path

    def _create_metric_cell(self, label: str, value: str) -> str:
        """Create a formatted metric cell for the KPI grid."""
        return f"<b>{label}</b><br/><font size=12><b>{value}</b></font>"

    def _generate_markdown(self, data: dict) -> Path:
        """Generate Markdown version for easy sharing."""
        output_path = self._get_output_path("md")

        lines = []

        # Header
        lines.append("# Executive Summary")
        lines.append(f"\n**Entity:** {data['entity']}  ")
        lines.append(f"**Period:** {data['period']}  ")
        lines.append(f"**Generated:** {data['generated_at'].strftime('%Y-%m-%d %H:%M')}  ")
        lines.append("")

        # Check for error
        if "error" in data:
            lines.append(f"\n**Error:** {data['error']}")
            with open(output_path, "w") as f:
                f.write("\n".join(lines))
            return output_path

        # Key Metrics
        lines.append("## Key Performance Indicators")
        lines.append("")

        analytics = data.get("analytics", {})
        hygiene_score = data.get("hygiene_score", {})
        review_status = data.get("review_status", {})

        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Balance | ₹{analytics.get('total_balance', 0):,.0f} |")
        lines.append(f"| Account Count | {analytics.get('account_count', 0)} |")
        lines.append(f"| Hygiene Score | {hygiene_score.get('overall_score', 0):.0f}% |")
        lines.append(
            f"| Completion Rate | {review_status.get('overall_completion_rate', 0):.0f}% |"
        )
        lines.append(f"| Pending Reviews | {review_status.get('pending_count', 0)} |")
        lines.append(f"| Flagged Items | {analytics.get('flagged_count', 0)} |")
        lines.append("")

        # Highlights
        lines.append("## Key Highlights")
        lines.append("")

        exec_summary = data.get("executive_summary", {})
        highlights = exec_summary.get("highlights", [])

        if highlights:
            for highlight in highlights:
                lines.append(f"- ✅ {highlight}")
        else:
            lines.append("- No highlights available.")
        lines.append("")

        # Concerns
        lines.append("## Areas of Concern")
        lines.append("")

        concerns = exec_summary.get("concerns", [])
        if concerns:
            for concern in concerns:
                lines.append(f"- ⚠️ {concern}")
        else:
            lines.append("- ✅ No major concerns identified.")
        lines.append("")

        # Recommendations
        lines.append("## Strategic Recommendations")
        lines.append("")

        insights = data.get("insights", {})
        recommendations = insights.get("recommendations", [])

        if recommendations:
            for rec in recommendations:
                priority = rec.get("priority", "Medium")
                action = rec.get("action", "N/A")

                if priority == "High":
                    priority_icon = "🔴"
                elif priority == "Medium":
                    priority_icon = "⚠️"
                else:
                    priority_icon = "•"

                lines.append(f"{priority_icon} **[{priority}]** {action}")
        else:
            lines.append("- Continue current practices.")
        lines.append("")

        # Status Breakdown
        lines.append("## Status Breakdown")
        lines.append("")

        by_status = analytics.get("by_status", {})

        lines.append("| Status | Count |")
        lines.append("|--------|-------|")
        for status, count in by_status.items():
            lines.append(f"| {status.title()} | {count} |")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("*Generated by Project Aura - Automated GL Review System*")

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return output_path

    def _generate_png(self, data: dict) -> Path:
        """Generate PNG executive dashboard chart."""
        hygiene_score = data.get("hygiene_score", {})
        overall_score = hygiene_score.get("overall_score", 0)

        # Create gauge chart
        fig = create_hygiene_gauge(
            overall_score, f"GL Hygiene Score - {data['entity']} ({data['period']})"
        )

        output_path = self._get_output_path("png", suffix="dashboard")
        export_chart_to_png(fig, str(output_path))

        return output_path
