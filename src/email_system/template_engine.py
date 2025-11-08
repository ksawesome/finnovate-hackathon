"""
Email Template Engine for Project Aura.

Manages email templates with Jinja2 rendering for automated notifications.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template


class EmailTemplateEngine:
    """Manage email templates with Jinja2 rendering."""

    def __init__(self, templates_dir: str = "src/email/templates"):
        """
        Initialize template engine.

        Args:
            templates_dir: Directory containing email templates
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self.env.filters["currency"] = self._format_currency
        self.env.filters["date"] = self._format_date
        self.env.filters["capitalize_words"] = self._capitalize_words

        # Template registry
        self.templates = self._load_template_registry()

    def _load_template_registry(self) -> dict:
        """Load template metadata registry."""
        registry_file = self.templates_dir / "registry.json"

        if registry_file.exists():
            with open(registry_file) as f:
                return json.load(f)

        # Default registry with 6 template types
        registry = {
            "assignment_notification": {
                "name": "Assignment Notification",
                "subject": "🔔 New GL Account Assignment: {{ account_code }}",
                "template_file": "assignment_notification.html",
                "variables": [
                    "account_code",
                    "account_name",
                    "reviewer_name",
                    "deadline",
                    "balance",
                    "entity",
                ],
                "category": "assignment",
                "priority": "high",
            },
            "upload_reminder": {
                "name": "Upload Reminder",
                "subject": "⏰ Reminder: Upload Supporting Documents for {{ account_code }}",
                "template_file": "upload_reminder.html",
                "variables": [
                    "account_code",
                    "reviewer_name",
                    "deadline",
                    "days_remaining",
                    "docs_required",
                ],
                "category": "reminder",
                "priority": "medium",
            },
            "review_completion": {
                "name": "Review Completion Notification",
                "subject": "✅ GL Account Review Completed: {{ account_code }}",
                "template_file": "review_completion.html",
                "variables": [
                    "account_code",
                    "account_name",
                    "reviewer_name",
                    "completion_date",
                    "comments",
                    "hygiene_score",
                ],
                "category": "notification",
                "priority": "medium",
            },
            "approval_notification": {
                "name": "Approval Notification",
                "subject": "✨ GL Account Approved: {{ account_code }}",
                "template_file": "approval_notification.html",
                "variables": [
                    "account_code",
                    "account_name",
                    "approver_name",
                    "approval_date",
                    "reviewer_name",
                ],
                "category": "notification",
                "priority": "medium",
            },
            "sla_breach_alert": {
                "name": "SLA Breach Alert",
                "subject": "🚨 URGENT: SLA Breach for GL Account {{ account_code }}",
                "template_file": "sla_breach_alert.html",
                "variables": [
                    "account_code",
                    "reviewer_name",
                    "deadline",
                    "days_overdue",
                    "escalation_level",
                    "entity",
                ],
                "category": "alert",
                "priority": "high",
            },
            "weekly_summary": {
                "name": "Weekly Summary Report",
                "subject": "📊 Weekly GL Review Summary - {{ week_ending }}",
                "template_file": "weekly_summary.html",
                "variables": [
                    "week_ending",
                    "total_accounts",
                    "reviewed",
                    "pending",
                    "hygiene_score",
                    "top_accounts",
                ],
                "category": "report",
                "priority": "low",
            },
        }

        # Save default registry
        self._save_registry(registry)
        return registry

    def _save_registry(self, registry: dict):
        """Save template registry to file."""
        registry_file = self.templates_dir / "registry.json"
        with open(registry_file, "w") as f:
            json.dump(registry, f, indent=2)

    def render_template(
        self, template_id: str, context: dict[str, Any], format: str = "html"
    ) -> dict[str, str]:
        """
        Render email template with context data.

        Args:
            template_id: Template identifier (e.g., 'assignment_notification')
            context: Dictionary with template variables
            format: 'html' or 'text'

        Returns:
            Dict with 'subject', 'body', 'format', 'priority'
        """
        if template_id not in self.templates:
            raise ValueError(f"Template '{template_id}' not found in registry")

        template_meta = self.templates[template_id]

        # Validate required variables
        missing_vars = set(template_meta["variables"]) - set(context.keys())
        if missing_vars:
            # Use None for missing optional variables
            for var in missing_vars:
                context[var] = None

        # Add common variables
        context["current_year"] = datetime.now().year
        context["app_name"] = "Project Aura"

        # Render subject
        subject_template = Template(template_meta["subject"])
        subject = subject_template.render(**context)

        # Render body
        template_file = template_meta["template_file"]
        if format == "text":
            template_file = template_file.replace(".html", ".txt")

        try:
            body_template = self.env.get_template(template_file)
            body = body_template.render(**context)
        except Exception as e:
            print(f"Warning: Template rendering failed ({e}), using fallback")
            body = self._generate_fallback_body(template_id, context)

        return {
            "subject": subject,
            "body": body,
            "format": format,
            "priority": template_meta["priority"],
            "category": template_meta["category"],
        }

    def _generate_fallback_body(self, template_id: str, context: dict) -> str:
        """Generate simple fallback email body."""
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Notification: {template_id.replace('_', ' ').title()}</h2>
            <hr>
            <table style="width: 100%; border-collapse: collapse;">
        """

        for key, value in context.items():
            if value is not None and key not in ["current_year", "app_name"]:
                body += f"""
                <tr>
                    <td style="padding: 8px; font-weight: bold;">{key.replace('_', ' ').title()}:</td>
                    <td style="padding: 8px;">{value}</td>
                </tr>
                """

        body += """
            </table>
            <hr>
            <p style="color: #666; font-size: 12px;">
                This is an automated notification from Project Aura.
            </p>
        </body>
        </html>
        """
        return body

    def _format_currency(self, value: float) -> str:
        """Format number as Indian currency."""
        try:
            return f"₹{float(value):,.2f}"
        except:
            return str(value)

    def _format_date(self, value: Any) -> str:
        """Format date string."""
        if isinstance(value, datetime):
            return value.strftime("%B %d, %Y")

        try:
            dt = datetime.fromisoformat(str(value))
            return dt.strftime("%B %d, %Y")
        except:
            return str(value)

    def _capitalize_words(self, value: str) -> str:
        """Capitalize each word."""
        return " ".join(word.capitalize() for word in str(value).split())

    def create_template_file(self, template_id: str, html_content: str):
        """Save HTML template file."""
        template_meta = self.templates.get(template_id)
        if not template_meta:
            raise ValueError(f"Template '{template_id}' not in registry")

        template_file = self.templates_dir / template_meta["template_file"]
        with open(template_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ Template saved: {template_file}")

    def list_templates(self) -> list[dict]:
        """List all available templates."""
        return [
            {
                "id": template_id,
                "name": meta["name"],
                "category": meta["category"],
                "priority": meta["priority"],
                "variables": meta["variables"],
            }
            for template_id, meta in self.templates.items()
        ]

    def get_template_info(self, template_id: str) -> dict:
        """Get detailed template information."""
        if template_id not in self.templates:
            raise ValueError(f"Template '{template_id}' not found")

        return self.templates[template_id]


# Sample usage
if __name__ == "__main__":
    # Initialize engine
    engine = EmailTemplateEngine()

    # List available templates
    print("Available Templates:")
    for template in engine.list_templates():
        print(f"  - {template['id']}: {template['name']} ({template['category']})")

    # Test rendering
    print("\n" + "=" * 80)
    print("Testing Assignment Notification Template")
    print("=" * 80)

    context = {
        "account_code": "10010001",
        "account_name": "Cash and Cash Equivalents",
        "reviewer_name": "John Doe",
        "deadline": "2024-11-15",
        "balance": 1234567.89,
        "entity": "AEML",
    }

    try:
        rendered = engine.render_template("assignment_notification", context)
        print(f"\nSubject: {rendered['subject']}")
        print(f"Priority: {rendered['priority']}")
        print("\nBody Preview:")
        print(rendered["body"][:500] + "...")
    except Exception as e:
        print(f"\nError: {e}")

    print("\n✅ Email Template Engine initialized!")
