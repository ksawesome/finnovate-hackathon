"""
GL Hygiene Dashboard Report Generator

Generates comprehensive GL hygiene assessment with quality metrics,
component analysis, trends, and recommendations.
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.analytics import calculate_gl_hygiene_score, perform_analytics
from src.reports import BaseReport, register_report
from src.visualizations import (
    create_component_bar_chart,
    create_hygiene_gauge,
    export_chart_to_html,
    export_chart_to_png,
)


@register_report("hygiene")
class GLHygieneDashboardReport(BaseReport):
    """Generate comprehensive GL hygiene dashboard report."""

    def generate(self) -> dict[str, str]:
        """
        Generate hygiene report in PDF, PNG, and JSON formats.

        Returns:
            Dict with 'pdf', 'png', 'html', and 'json' keys mapping to file paths
        """
        self.generated_at = datetime.now()

        # Fetch data
        data = self._fetch_data()

        # Generate PDF report
        pdf_path = self._generate_pdf(data)
        self.generated_files["pdf"] = str(pdf_path)

        # Generate PNG charts
        if "hygiene_score" in data and not data["hygiene_score"].get("error"):
            png_paths = self._generate_png_charts(data)
            self.generated_files["png"] = png_paths

            # Generate HTML interactive charts
            html_path = self._generate_html_charts(data)
            self.generated_files["html"] = str(html_path)

        # Generate JSON data export
        json_path = self._generate_json(data)
        self.generated_files["json"] = str(json_path)

        return self.generated_files

    def _fetch_data(self) -> dict:
        """Fetch hygiene score and analytics data."""
        try:
            # Get hygiene score breakdown
            hygiene_score = calculate_gl_hygiene_score(self.entity, self.period)

            # Get general analytics
            analytics = perform_analytics(self.entity, self.period)

            return {
                "hygiene_score": hygiene_score,
                "analytics": analytics,
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
        """Generate comprehensive PDF hygiene report."""
        output_path = self._get_output_path("pdf")

        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=22,
            textColor=colors.HexColor("#16a085"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )

        elements.append(Paragraph("GL Hygiene Dashboard", title_style))
        elements.append(
            Paragraph(f"Entity: {data['entity']} | Period: {data['period']}", styles["Normal"])
        )
        elements.append(Spacer(1, 0.3 * inch))

        # Check for error
        if "error" in data:
            elements.append(Paragraph(f"Error: {data['error']}", styles["Normal"]))
            doc.build(elements)
            return output_path

        hygiene_data = data.get("hygiene_score", {})

        # Overall Score Card
        elements.append(Paragraph("Overall Hygiene Score", styles["Heading2"]))

        overall_score = hygiene_data.get("overall_score", 0)
        status = hygiene_data.get("status", "Unknown")

        score_data = [
            ["Metric", "Value", "Status"],
            ["Overall Hygiene Score", f"{overall_score:.1f}%", status],
            ["Accounts Analyzed", str(hygiene_data.get("total_accounts", 0)), "-"],
            ["Assessment Date", data["generated_at"].strftime("%Y-%m-%d %H:%M"), "-"],
        ]

        # Color code based on score
        if overall_score >= 80:
            header_color = colors.HexColor("#27ae60")  # Green
        elif overall_score >= 60:
            header_color = colors.HexColor("#f39c12")  # Orange
        else:
            header_color = colors.HexColor("#e74c3c")  # Red

        score_table = Table(score_data, colWidths=[2.5 * inch, 2 * inch, 1.5 * inch])
        score_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), header_color),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 1), (1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 1), (1, 1), 14),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        elements.append(score_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Component Breakdown
        elements.append(Paragraph("Component Analysis", styles["Heading2"]))

        components = hygiene_data.get("component_scores", {})
        component_data = [["Component", "Score", "Weight", "Status"]]

        for comp_name, comp_info in components.items():
            score = comp_info.get("score", 0)
            weight = comp_info.get("weight", 0) * 100

            if score >= 80:
                comp_status = "✓ Good"
            elif score >= 60:
                comp_status = "⚠ Fair"
            else:
                comp_status = "🔴 Needs Attention"

            component_data.append(
                [
                    comp_name.replace("_", " ").title(),
                    f"{score:.1f}%",
                    f"{weight:.0f}%",
                    comp_status,
                ]
            )

        comp_table = Table(
            component_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch]
        )
        comp_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 1), (2, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        elements.append(comp_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Issue Summary
        elements.append(Paragraph("Quality Issues Detected", styles["Heading2"]))

        issues = hygiene_data.get("issues", [])
        if issues:
            issue_data = [["Severity", "Issue Type", "Count", "Impact"]]

            for issue in issues[:10]:  # Top 10 issues
                severity = issue.get("severity", "Medium")
                issue_type = issue.get("type", "Unknown")
                count = issue.get("count", 0)
                impact = issue.get("impact", "Medium")

                issue_data.append([severity, issue_type, str(count), impact])

            issue_table = Table(issue_data, colWidths=[1.5 * inch, 2.5 * inch, 1 * inch, 2 * inch])
            issue_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e74c3c")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (2, 1), (2, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )

            elements.append(issue_table)
        else:
            elements.append(Paragraph("✓ No critical quality issues detected.", styles["Normal"]))

        elements.append(Spacer(1, 0.3 * inch))

        # Recommendations
        elements.append(Paragraph("Recommendations", styles["Heading2"]))

        recommendations = self._generate_recommendations(hygiene_data)

        rec_style = ParagraphStyle(
            "Recommendations", parent=styles["Normal"], leftIndent=20, spaceAfter=10
        )

        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", rec_style))

        elements.append(Spacer(1, 0.2 * inch))

        # Trend Analysis (if available)
        elements.append(PageBreak())
        elements.append(Paragraph("Hygiene Trend Analysis", styles["Heading2"]))

        analytics = data.get("analytics", {})
        if analytics and not analytics.get("error"):
            trend_text = f"""
            <b>Current Period Metrics:</b><br/>
            • Total Balance: ₹{analytics.get('total_balance', 0):,.0f}<br/>
            • Account Count: {analytics.get('account_count', 0)}<br/>
            • Average Balance: ₹{analytics.get('average_balance', 0):,.0f}<br/>
            <br/>
            For detailed trend analysis across multiple periods, use the Multi-Period Comparison feature.
            """
            elements.append(Paragraph(trend_text, styles["Normal"]))
        else:
            elements.append(
                Paragraph("Trend data not available for this period.", styles["Normal"])
            )

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

    def _generate_recommendations(self, hygiene_data: dict) -> list[str]:
        """Generate actionable recommendations based on hygiene score."""
        recommendations = []

        overall_score = hygiene_data.get("overall_score", 0)
        components = hygiene_data.get("component_scores", {})

        # Overall score recommendations
        if overall_score < 60:
            recommendations.append(
                "CRITICAL: Overall hygiene score is below acceptable threshold. "
                "Immediate attention required across multiple components."
            )
        elif overall_score < 80:
            recommendations.append(
                "Overall hygiene score is moderate. Focus on improvement areas to reach excellent status."
            )
        else:
            recommendations.append(
                "Overall hygiene score is excellent. Maintain current practices and monitor for any degradation."
            )

        # Component-specific recommendations
        for comp_name, comp_info in components.items():
            score = comp_info.get("score", 0)
            if score < 60:
                comp_title = comp_name.replace("_", " ").title()
                recommendations.append(
                    f"Address {comp_title} issues (score: {score:.1f}%). "
                    f"This component significantly impacts overall hygiene."
                )

        # Issue-based recommendations
        issues = hygiene_data.get("issues", [])
        high_severity_issues = [i for i in issues if i.get("severity") == "High"]

        if high_severity_issues:
            recommendations.append(
                f"Resolve {len(high_severity_issues)} high-severity issues immediately. "
                "These pose significant risk to data quality."
            )

        # Default recommendations
        if not recommendations:
            recommendations.append(
                "Continue regular hygiene monitoring and maintain current standards."
            )
            recommendations.append(
                "Consider quarterly deep-dive audits to identify improvement opportunities."
            )

        return recommendations

    def _generate_png_charts(self, data: dict) -> list[str]:
        """Generate PNG chart exports."""
        hygiene_data = data.get("hygiene_score", {})
        png_paths = []

        # 1. Hygiene Gauge Chart
        overall_score = hygiene_data.get("overall_score", 0)
        gauge_fig = create_hygiene_gauge(overall_score, f"GL Hygiene Score - {self.entity}")

        gauge_path = self._get_output_path("png", suffix="gauge")
        export_chart_to_png(gauge_fig, str(gauge_path))
        png_paths.append(str(gauge_path))

        # 2. Component Bar Chart
        components = hygiene_data.get("component_scores", {})
        if components:
            comp_df = pd.DataFrame(
                [
                    {
                        "component": comp_name.replace("_", " ").title(),
                        "score": comp_info.get("score", 0),
                    }
                    for comp_name, comp_info in components.items()
                ]
            )

            bar_fig = create_component_bar_chart(
                comp_df, title=f"Hygiene Component Scores - {self.entity} ({self.period})"
            )

            bar_path = self._get_output_path("png", suffix="components")
            export_chart_to_png(bar_fig, str(bar_path))
            png_paths.append(str(bar_path))

        return png_paths

    def _generate_html_charts(self, data: dict) -> Path:
        """Generate interactive HTML dashboard."""
        hygiene_data = data.get("hygiene_score", {})

        # Create combined dashboard with subplots
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("Overall Hygiene Score", "Component Breakdown"),
            specs=[[{"type": "indicator"}, {"type": "bar"}]],
        )

        # Gauge chart
        overall_score = hygiene_data.get("overall_score", 0)

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=overall_score,
                title={"text": "Hygiene Score (%)"},
                delta={"reference": 80},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 60], "color": "lightgray"},
                        {"range": [60, 80], "color": "lightyellow"},
                        {"range": [80, 100], "color": "lightgreen"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 90,
                    },
                },
            ),
            row=1,
            col=1,
        )

        # Component bar chart
        components = hygiene_data.get("component_scores", {})
        if components:
            comp_names = [comp.replace("_", " ").title() for comp in components.keys()]
            comp_scores = [comp_info.get("score", 0) for comp_info in components.values()]

            fig.add_trace(
                go.Bar(
                    x=comp_names,
                    y=comp_scores,
                    marker_color=[
                        "#27ae60" if s >= 80 else "#f39c12" if s >= 60 else "#e74c3c"
                        for s in comp_scores
                    ],
                    text=[f"{s:.1f}%" for s in comp_scores],
                    textposition="outside",
                ),
                row=1,
                col=2,
            )

        fig.update_layout(
            title_text=f"GL Hygiene Dashboard - {self.entity} ({self.period})",
            showlegend=False,
            height=500,
        )

        output_path = self._get_output_path("html", suffix="dashboard")
        export_chart_to_html(fig, str(output_path))

        return output_path

    def _generate_json(self, data: dict) -> Path:
        """Generate JSON data export."""
        output_path = self._get_output_path("json")

        # Prepare data for JSON serialization
        export_data = {
            "metadata": {
                "entity": data["entity"],
                "period": data["period"],
                "generated_at": data["generated_at"].isoformat(),
                "report_type": "GL Hygiene Dashboard",
            },
            "hygiene_score": data.get("hygiene_score", {}),
            "analytics_summary": {
                "total_balance": data.get("analytics", {}).get("total_balance", 0),
                "account_count": data.get("analytics", {}).get("account_count", 0),
                "average_balance": data.get("analytics", {}).get("average_balance", 0),
            },
        }

        # Write JSON
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        return output_path
