"""
GL Account Status Report Generator

Generates comprehensive status reports showing pending reviews, missing documentation,
flagged items, and SLA status for GL accounts.
"""

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.analytics import calculate_review_status_summary, get_pending_items_report
from src.db import get_postgres_session
from src.db.postgres import get_gl_accounts_by_entity_period
from src.reports import BaseReport, register_report


@register_report("status")
class GLAccountStatusReport(BaseReport):
    """Generate comprehensive GL account status report."""

    def generate(self) -> dict[str, str]:
        """
        Generate status report in PDF and CSV formats.

        Returns:
            Dict with 'pdf' and 'csv' keys mapping to file paths
        """
        from datetime import datetime as dt

        self.generated_at = dt.now()

        # Fetch data
        data = self._fetch_data()

        # Generate PDF
        pdf_path = self._generate_pdf(data)
        self.generated_files["pdf"] = str(pdf_path)

        # Generate CSV
        csv_path = self._generate_csv(data)
        self.generated_files["csv"] = str(csv_path)

        return self.generated_files

    def _fetch_data(self) -> dict:
        """Fetch all data needed for status report."""
        try:
            # Get pending items
            pending_data = get_pending_items_report(self.entity, self.period)

            # Get review status summary
            status_summary = calculate_review_status_summary(self.entity, self.period)

            # Get all GL accounts for completeness
            session = get_postgres_session()
            try:
                accounts = get_gl_accounts_by_entity_period(session, self.entity, self.period)
            finally:
                session.close()

            return {
                "pending_data": pending_data,
                "status_summary": status_summary,
                "accounts": accounts,
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
        """Generate PDF report."""
        output_path = self._get_output_path("pdf")

        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1f77b4"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=12,
            spaceBefore=12,
        )

        # Title
        elements.append(Paragraph("GL Account Status Report", title_style))
        elements.append(
            Paragraph(
                f"Entity: {data['entity']} | Period: {data['period']} | "
                f"Generated: {data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

        # Check for errors
        if "error" in data:
            elements.append(Paragraph(f"Error: {data['error']}", styles["Normal"]))
            doc.build(elements)
            return output_path

        pending_data = data.get("pending_data", {})
        status_summary = data.get("status_summary", {})

        # Section 1: Executive Summary
        elements.append(Paragraph("1. Executive Summary", heading_style))

        summary_data = [
            ["Metric", "Count", "Status"],
            ["Total Accounts", str(len(data.get("accounts", []))), "✓"],
            [
                "Pending Reviews",
                str(pending_data.get("pending_reviews_count", 0)),
                "⚠" if pending_data.get("pending_reviews_count", 0) > 0 else "✓",
            ],
            [
                "Missing Documentation",
                str(pending_data.get("missing_docs_count", 0)),
                "⚠" if pending_data.get("missing_docs_count", 0) > 0 else "✓",
            ],
            [
                "Flagged Items",
                str(pending_data.get("flagged_items_count", 0)),
                "🔴" if pending_data.get("flagged_items_count", 0) > 0 else "✓",
            ],
            [
                "Completion Rate",
                f"{status_summary.get('overall_completion_rate', 0):.1f}%",
                "✓" if status_summary.get("overall_completion_rate", 0) >= 80 else "⚠",
            ],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 1.5 * inch, 1 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Section 2: Pending Reviews
        elements.append(Paragraph("2. Pending Reviews", heading_style))

        pending_reviews = pending_data.get("pending_reviews", [])
        if pending_reviews:
            review_data = [["Account Code", "Account Name", "Criticality", "Department"]]
            for item in pending_reviews[:10]:  # Top 10
                review_data.append(
                    [
                        item.get("account_code", "N/A"),
                        item.get("account_name", "N/A")[:30],  # Truncate long names
                        item.get("criticality", "N/A"),
                        item.get("department", "N/A"),
                    ]
                )

            review_table = Table(
                review_data, colWidths=[1.2 * inch, 2.5 * inch, 1 * inch, 1.5 * inch]
            )
            review_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e74c3c")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )

            elements.append(review_table)

            if len(pending_reviews) > 10:
                elements.append(
                    Paragraph(
                        f"<i>Showing top 10 of {len(pending_reviews)} pending reviews. "
                        f"See CSV export for complete list.</i>",
                        styles["Normal"],
                    )
                )
        else:
            elements.append(
                Paragraph("✓ No pending reviews. All accounts up to date!", styles["Normal"])
            )

        elements.append(Spacer(1, 0.2 * inch))

        # Section 3: Missing Documentation
        elements.append(Paragraph("3. Missing Documentation", heading_style))

        missing_docs = pending_data.get("missing_docs", [])
        if missing_docs:
            docs_data = [["Account Code", "Account Name", "Criticality", "Balance"]]
            for item in missing_docs[:10]:
                docs_data.append(
                    [
                        item.get("account_code", "N/A"),
                        item.get("account_name", "N/A")[:30],
                        item.get("criticality", "N/A"),
                        f"₹{item.get('balance', 0):,.0f}",
                    ]
                )

            docs_table = Table(docs_data, colWidths=[1.2 * inch, 2.5 * inch, 1 * inch, 1.5 * inch])
            docs_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f39c12")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (3, 1), (3, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )

            elements.append(docs_table)

            if len(missing_docs) > 10:
                elements.append(
                    Paragraph(
                        f"<i>Showing top 10 of {len(missing_docs)} accounts with missing docs.</i>",
                        styles["Normal"],
                    )
                )
        else:
            elements.append(
                Paragraph("✓ All accounts have complete documentation!", styles["Normal"])
            )

        elements.append(Spacer(1, 0.2 * inch))

        # Section 4: Flagged Items
        elements.append(Paragraph("4. Flagged Items", heading_style))

        flagged_items = pending_data.get("flagged_items", [])
        if flagged_items:
            flagged_data = [["Account Code", "Account Name", "Reason", "Priority"]]
            for item in flagged_items[:10]:
                flagged_data.append(
                    [
                        item.get("account_code", "N/A"),
                        item.get("account_name", "N/A")[:30],
                        item.get("flag_reason", "Review needed")[:25],
                        item.get("criticality", "N/A"),
                    ]
                )

            flagged_table = Table(
                flagged_data, colWidths=[1.2 * inch, 2 * inch, 2 * inch, 1 * inch]
            )
            flagged_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#c0392b")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )

            elements.append(flagged_table)
        else:
            elements.append(Paragraph("✓ No flagged items!", styles["Normal"]))

        elements.append(Spacer(1, 0.2 * inch))

        # Section 5: SLA Status
        elements.append(Paragraph("5. SLA Status", heading_style))

        # Calculate SLA metrics
        total_accounts = len(data.get("accounts", []))
        pending_count = pending_data.get("pending_reviews_count", 0)
        on_time = total_accounts - pending_count
        sla_compliance = (on_time / total_accounts * 100) if total_accounts > 0 else 0

        sla_data = [
            ["SLA Metric", "Value", "Target", "Status"],
            ["Total Accounts", str(total_accounts), "-", "✓"],
            [
                "Reviewed On-Time",
                str(on_time),
                f"{total_accounts}",
                "✓" if on_time >= total_accounts * 0.9 else "⚠",
            ],
            ["Pending Reviews", str(pending_count), "0", "✓" if pending_count == 0 else "⚠"],
            [
                "SLA Compliance %",
                f"{sla_compliance:.1f}%",
                "≥90%",
                "✓" if sla_compliance >= 90 else "⚠",
            ],
        ]

        sla_table = Table(sla_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
        sla_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16a085")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        elements.append(sla_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Section 6: Recommendations
        elements.append(Paragraph("6. Recommendations", heading_style))

        recommendations = []

        if pending_count > 0:
            recommendations.append(
                f"• Prioritize review of {pending_count} pending accounts, starting with High criticality items."
            )

        if pending_data.get("missing_docs_count", 0) > 0:
            recommendations.append(
                f"• Request supporting documentation for {pending_data.get('missing_docs_count')} accounts."
            )

        if pending_data.get("flagged_items_count", 0) > 0:
            recommendations.append(
                f"• Investigate {pending_data.get('flagged_items_count')} flagged items for potential issues."
            )

        if sla_compliance < 90:
            recommendations.append(
                f"• SLA compliance at {sla_compliance:.1f}% - implement escalation procedures."
            )

        if not recommendations:
            recommendations.append("• No immediate action required. All accounts are up to date!")

        for rec in recommendations:
            elements.append(Paragraph(rec, styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))

        # Footer
        elements.append(Spacer(1, 0.5 * inch))
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )
        elements.append(
            Paragraph(
                f"Generated by Project Aura | {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"Page 1 of 1",
                footer_style,
            )
        )

        # Build PDF
        doc.build(elements)

        return output_path

    def _generate_csv(self, data: dict) -> Path:
        """Generate CSV export of pending items."""
        output_path = self._get_output_path("csv")

        pending_data = data.get("pending_data", {})

        # Combine all pending items into one DataFrame
        all_items = []

        # Pending reviews
        for item in pending_data.get("pending_reviews", []):
            all_items.append(
                {
                    "Type": "Pending Review",
                    "Account Code": item.get("account_code"),
                    "Account Name": item.get("account_name"),
                    "Category": item.get("category", "N/A"),
                    "Department": item.get("department", "N/A"),
                    "Criticality": item.get("criticality"),
                    "Balance": item.get("balance", 0),
                    "Status": "Pending",
                    "Notes": "Requires review",
                }
            )

        # Missing docs
        for item in pending_data.get("missing_docs", []):
            all_items.append(
                {
                    "Type": "Missing Documentation",
                    "Account Code": item.get("account_code"),
                    "Account Name": item.get("account_name"),
                    "Category": item.get("category", "N/A"),
                    "Department": item.get("department", "N/A"),
                    "Criticality": item.get("criticality"),
                    "Balance": item.get("balance", 0),
                    "Status": "Missing Docs",
                    "Notes": "Upload required",
                }
            )

        # Flagged items
        for item in pending_data.get("flagged_items", []):
            all_items.append(
                {
                    "Type": "Flagged",
                    "Account Code": item.get("account_code"),
                    "Account Name": item.get("account_name"),
                    "Category": item.get("category", "N/A"),
                    "Department": item.get("department", "N/A"),
                    "Criticality": item.get("criticality"),
                    "Balance": item.get("balance", 0),
                    "Status": "Flagged",
                    "Notes": item.get("flag_reason", "Review needed"),
                }
            )

        df = pd.DataFrame(all_items)

        if df.empty:
            # Create empty DataFrame with headers
            df = pd.DataFrame(
                columns=[
                    "Type",
                    "Account Code",
                    "Account Name",
                    "Category",
                    "Department",
                    "Criticality",
                    "Balance",
                    "Status",
                    "Notes",
                ]
            )

        df.to_csv(output_path, index=False)

        return output_path
