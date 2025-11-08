"""
Notification Service Module

Handles automated email notifications triggered by GL account review lifecycle events.
Integrates with PostgreSQL for account data and MongoDB for audit tracking.

Author: Project Aura Team
Date: November 2024
"""

import logging
from datetime import datetime

from ..db.mongodb import get_mongo_database
from ..db.postgres import get_gl_account_by_code, get_gl_accounts_by_period, get_postgres_session
from .email_service import get_email_service
from .template_engine import EmailTemplateEngine

# Configure logging
logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for automated email notifications based on GL account review events.

    Features:
    - Event-triggered notifications (assignment, reminder, completion, approval, SLA breach)
    - Integration with PostgreSQL (account data) and MongoDB (audit trail)
    - Template-based email rendering
    - Automatic recipient lookup from responsibility matrix
    - Weekly summary reports
    """

    def __init__(self):
        """Initialize NotificationService with email and template engines."""
        self.email_service = get_email_service()
        self.template_engine = EmailTemplateEngine()
        self.db = get_mongo_database()
        self.notification_log = self.db["notification_log"]

        logger.info("NotificationService initialized")

    def on_assignment(
        self,
        account_code: str,
        reviewer_email: str,
        reviewer_name: str,
        deadline: datetime,
        entity: str,
        metadata: dict | None = None,
    ) -> bool:
        """
        Trigger notification when GL account is assigned to reviewer.

        Args:
            account_code: GL account code
            reviewer_email: Reviewer's email address
            reviewer_name: Reviewer's full name
            deadline: Review deadline
            entity: Entity code (e.g., AEML)
            metadata: Additional metadata

        Returns:
            True if notification sent successfully
        """
        try:
            # Get account details from database
            session = get_postgres_session()
            try:
                account = get_gl_account_by_code(session, account_code)

                if not account:
                    logger.error(f"Account not found: {account_code}")
                    return False

                # Prepare template context
                context = {
                    "account_code": account_code,
                    "account_name": account.account_name or "N/A",
                    "reviewer_name": reviewer_name,
                    "deadline": deadline.strftime("%Y-%m-%d"),
                    "balance": float(account.closing_balance or 0),
                    "entity": entity,
                    "app_name": "Project Aura",
                    "current_year": datetime.now().year,
                }

                # Render template
                rendered = self.template_engine.render_template("assignment_notification", context)

                # Send email
                success, message = self.email_service.send_email(
                    to_email=reviewer_email,
                    subject=rendered["subject"],
                    body_html=rendered["body"],
                    metadata={
                        "event": "assignment",
                        "account_code": account_code,
                        "entity": entity,
                        **(metadata or {}),
                    },
                )

                # Log notification
                self._log_notification(
                    event="assignment",
                    recipient=reviewer_email,
                    account_code=account_code,
                    success=success,
                    message=message,
                )

                if success:
                    logger.info(
                        f"Assignment notification sent to {reviewer_email} for {account_code}"
                    )
                else:
                    logger.error(f"Failed to send assignment notification: {message}")

                return success

            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error sending assignment notification: {e}")
            return False

    def on_reminder(
        self,
        account_code: str,
        reviewer_email: str,
        reviewer_name: str,
        deadline: datetime,
        days_remaining: int,
        docs_required: list[str] | None = None,
        metadata: dict | None = None,
    ) -> bool:
        """
        Trigger reminder notification before review deadline.

        Args:
            account_code: GL account code
            reviewer_email: Reviewer's email address
            reviewer_name: Reviewer's full name
            deadline: Review deadline
            days_remaining: Days until deadline
            docs_required: List of required documents
            metadata: Additional metadata

        Returns:
            True if notification sent successfully
        """
        try:
            # Prepare template context
            context = {
                "account_code": account_code,
                "reviewer_name": reviewer_name,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "days_remaining": days_remaining,
                "docs_required": docs_required
                or [
                    "Bank reconciliation statement",
                    "Transaction supporting documents",
                    "Variance explanation notes",
                    "Any other relevant documentation",
                ],
                "app_name": "Project Aura",
                "current_year": datetime.now().year,
            }

            # Render template
            rendered = self.template_engine.render_template("upload_reminder", context)

            # Send email
            success, message = self.email_service.send_email(
                to_email=reviewer_email,
                subject=rendered["subject"],
                body_html=rendered["body"],
                metadata={
                    "event": "reminder",
                    "account_code": account_code,
                    "days_remaining": days_remaining,
                    **(metadata or {}),
                },
            )

            # Log notification
            self._log_notification(
                event="reminder",
                recipient=reviewer_email,
                account_code=account_code,
                success=success,
                message=message,
            )

            if success:
                logger.info(
                    f"Reminder notification sent to {reviewer_email} for {account_code} "
                    f"({days_remaining} days remaining)"
                )

            return success

        except Exception as e:
            logger.error(f"Error sending reminder notification: {e}")
            return False

    def on_review_complete(
        self,
        account_code: str,
        account_name: str,
        reviewer_name: str,
        reviewer_email: str,
        completion_date: datetime,
        comments: str | None = None,
        hygiene_score: int = 0,
        notify_approver: bool = True,
        approver_email: str | None = None,
        metadata: dict | None = None,
    ) -> bool:
        """
        Trigger notification when review is completed.

        Args:
            account_code: GL account code
            account_name: GL account name
            reviewer_name: Reviewer's full name
            reviewer_email: Reviewer's email address
            completion_date: Review completion date
            comments: Reviewer comments
            hygiene_score: Data hygiene score (0-100)
            notify_approver: Whether to notify approver
            approver_email: Approver's email address
            metadata: Additional metadata

        Returns:
            True if notification sent successfully
        """
        try:
            # Prepare template context
            context = {
                "account_code": account_code,
                "account_name": account_name,
                "reviewer_name": reviewer_name,
                "completion_date": completion_date.strftime("%Y-%m-%d"),
                "comments": comments,
                "hygiene_score": hygiene_score,
                "app_name": "Project Aura",
                "current_year": datetime.now().year,
            }

            # Render template
            rendered = self.template_engine.render_template("review_completion", context)

            # Determine recipients
            recipients = [reviewer_email]
            if notify_approver and approver_email:
                recipients.append(approver_email)

            # Send email
            results = self.email_service.send_bulk_email(
                recipients=recipients,
                subject=rendered["subject"],
                body_html=rendered["body"],
                metadata={
                    "event": "review_complete",
                    "account_code": account_code,
                    "hygiene_score": hygiene_score,
                    **(metadata or {}),
                },
            )

            success = len(results["success"]) > 0

            # Log notification
            for email in recipients:
                self._log_notification(
                    event="review_complete",
                    recipient=email,
                    account_code=account_code,
                    success=email in results["success"],
                    message=f"Sent to {len(results['success'])}/{len(recipients)} recipients",
                )

            if success:
                logger.info(
                    f"Review completion notification sent for {account_code} "
                    f"({len(results['success'])}/{len(recipients)} successful)"
                )

            return success

        except Exception as e:
            logger.error(f"Error sending review completion notification: {e}")
            return False

    def on_approval(
        self,
        account_code: str,
        account_name: str,
        reviewer_name: str,
        reviewer_email: str,
        approver_name: str,
        approver_email: str,
        approval_date: datetime,
        metadata: dict | None = None,
    ) -> bool:
        """
        Trigger notification when account is approved.

        Args:
            account_code: GL account code
            account_name: GL account name
            reviewer_name: Reviewer's full name
            reviewer_email: Reviewer's email address
            approver_name: Approver's full name
            approver_email: Approver's email address
            approval_date: Approval date
            metadata: Additional metadata

        Returns:
            True if notification sent successfully
        """
        try:
            # Prepare template context
            context = {
                "account_code": account_code,
                "account_name": account_name,
                "reviewer_name": reviewer_name,
                "approver_name": approver_name,
                "approval_date": approval_date.strftime("%Y-%m-%d"),
                "app_name": "Project Aura",
                "current_year": datetime.now().year,
            }

            # Render template
            rendered = self.template_engine.render_template("approval_notification", context)

            # Send to both reviewer and approver
            results = self.email_service.send_bulk_email(
                recipients=[reviewer_email, approver_email],
                subject=rendered["subject"],
                body_html=rendered["body"],
                metadata={
                    "event": "approval",
                    "account_code": account_code,
                    **(metadata or {}),
                },
            )

            success = len(results["success"]) > 0

            # Log notification
            for email in [reviewer_email, approver_email]:
                self._log_notification(
                    event="approval",
                    recipient=email,
                    account_code=account_code,
                    success=email in results["success"],
                    message=f"Sent to {len(results['success'])}/2 recipients",
                )

            if success:
                logger.info(f"Approval notification sent for {account_code}")

            return success

        except Exception as e:
            logger.error(f"Error sending approval notification: {e}")
            return False

    def on_sla_breach(
        self,
        account_code: str,
        reviewer_name: str,
        reviewer_email: str,
        deadline: datetime,
        days_overdue: int,
        escalation_level: str,
        entity: str,
        manager_emails: list[str] | None = None,
        metadata: dict | None = None,
    ) -> bool:
        """
        Trigger alert when review deadline is breached.

        Args:
            account_code: GL account code
            reviewer_name: Reviewer's full name
            reviewer_email: Reviewer's email address
            deadline: Original deadline
            days_overdue: Days past deadline
            escalation_level: Escalation level (medium, high, critical)
            entity: Entity code
            manager_emails: Manager email addresses for escalation
            metadata: Additional metadata

        Returns:
            True if notification sent successfully
        """
        try:
            # Prepare template context
            context = {
                "account_code": account_code,
                "reviewer_name": reviewer_name,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "days_overdue": days_overdue,
                "escalation_level": escalation_level,
                "entity": entity,
                "app_name": "Project Aura",
                "current_year": datetime.now().year,
            }

            # Render template
            rendered = self.template_engine.render_template("sla_breach_alert", context)

            # Determine recipients based on escalation level
            recipients = [reviewer_email]
            if manager_emails:
                if escalation_level in ["high", "critical"]:
                    recipients.extend(manager_emails)

            # Send email with high priority
            results = self.email_service.send_bulk_email(
                recipients=recipients,
                subject=rendered["subject"],
                body_html=rendered["body"],
                metadata={
                    "event": "sla_breach",
                    "account_code": account_code,
                    "days_overdue": days_overdue,
                    "escalation_level": escalation_level,
                    **(metadata or {}),
                },
            )

            success = len(results["success"]) > 0

            # Log notification
            for email in recipients:
                self._log_notification(
                    event="sla_breach",
                    recipient=email,
                    account_code=account_code,
                    success=email in results["success"],
                    message=f"Escalation: {escalation_level}, {days_overdue} days overdue",
                )

            if success:
                logger.warning(
                    f"SLA breach alert sent for {account_code} "
                    f"({days_overdue} days overdue, {escalation_level} escalation)"
                )

            return success

        except Exception as e:
            logger.error(f"Error sending SLA breach alert: {e}")
            return False

    def send_weekly_summary(
        self,
        recipient_emails: list[str],
        period: str,
        entity: str | None = None,
        metadata: dict | None = None,
    ) -> bool:
        """
        Send weekly summary report to stakeholders.

        Args:
            recipient_emails: List of recipient email addresses
            period: Reporting period (e.g., 'Mar-24')
            entity: Entity filter (optional)
            metadata: Additional metadata

        Returns:
            True if notification sent successfully
        """
        try:
            # Get accounts for period
            session = get_postgres_session()
            try:
                accounts = get_gl_accounts_by_period(session, period)

                # Filter by entity if specified
                if entity:
                    accounts = [a for a in accounts if a.entity == entity]

                # Calculate statistics
                total_accounts = len(accounts)
                reviewed = sum(1 for a in accounts if a.review_status == "reviewed")
                pending = sum(1 for a in accounts if a.review_status == "pending")

                # Calculate average hygiene score
                hygiene_scores = [a.hygiene_score for a in accounts if a.hygiene_score is not None]
                avg_hygiene_score = (
                    int(sum(hygiene_scores) / len(hygiene_scores)) if hygiene_scores else 0
                )

                # Get top accounts requiring attention
                top_accounts = []
                for account in sorted(
                    accounts, key=lambda a: abs(a.closing_balance or 0), reverse=True
                )[:5]:
                    top_accounts.append(
                        {
                            "code": account.gl_account_code,
                            "name": account.account_name or "N/A",
                            "status": account.review_status or "pending",
                            "balance": float(account.closing_balance or 0),
                        }
                    )

                # Prepare template context
                week_ending = datetime.now()
                context = {
                    "week_ending": week_ending.strftime("%Y-%m-%d"),
                    "total_accounts": total_accounts,
                    "reviewed": reviewed,
                    "pending": pending,
                    "hygiene_score": avg_hygiene_score,
                    "top_accounts": top_accounts,
                    "app_name": "Project Aura",
                    "current_year": datetime.now().year,
                }

                # Render template
                rendered = self.template_engine.render_template("weekly_summary", context)

                # Send email
                results = self.email_service.send_bulk_email(
                    recipients=recipient_emails,
                    subject=rendered["subject"],
                    body_html=rendered["body"],
                    metadata={
                        "event": "weekly_summary",
                        "period": period,
                        "entity": entity,
                        "total_accounts": total_accounts,
                        **(metadata or {}),
                    },
                )

                success = len(results["success"]) > 0

                # Log notification
                for email in recipient_emails:
                    self._log_notification(
                        event="weekly_summary",
                        recipient=email,
                        account_code=None,
                        success=email in results["success"],
                        message=f"Period: {period}, Accounts: {total_accounts}",
                    )

                if success:
                    logger.info(
                        f"Weekly summary sent to {len(results['success'])}/{len(recipient_emails)} recipients "
                        f"(Period: {period}, Accounts: {total_accounts})"
                    )

                return success

            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error sending weekly summary: {e}")
            return False

    def check_pending_reminders(self, days_before_deadline: int = 2) -> int:
        """
        Check for accounts requiring reminder notifications.

        Args:
            days_before_deadline: Send reminder this many days before deadline

        Returns:
            Number of reminders sent
        """
        try:
            session = get_postgres_session()
            try:
                # Get all pending accounts
                # Note: This would need to be implemented in postgres.py
                # For now, we'll return 0 as a placeholder
                logger.info(
                    f"Checking for pending reminders ({days_before_deadline} days before deadline)"
                )
                return 0

            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error checking pending reminders: {e}")
            return 0

    def check_sla_breaches(self) -> int:
        """
        Check for SLA breaches and send alerts.

        Returns:
            Number of SLA breach alerts sent
        """
        try:
            session = get_postgres_session()
            try:
                # Get all accounts with breached deadlines
                # Note: This would need to be implemented in postgres.py
                # For now, we'll return 0 as a placeholder
                logger.info("Checking for SLA breaches")
                return 0

            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error checking SLA breaches: {e}")
            return 0

    def _log_notification(
        self,
        event: str,
        recipient: str,
        account_code: str | None,
        success: bool,
        message: str,
    ) -> None:
        """
        Log notification to MongoDB.

        Args:
            event: Event type
            recipient: Recipient email
            account_code: GL account code
            success: Whether notification was sent successfully
            message: Status message
        """
        try:
            log_entry = {
                "event": event,
                "recipient": recipient,
                "account_code": account_code,
                "success": success,
                "message": message,
                "timestamp": datetime.utcnow(),
            }

            self.notification_log.insert_one(log_entry)

        except Exception as e:
            logger.error(f"Error logging notification: {e}")


# Convenience function to get configured notification service
def get_notification_service() -> NotificationService:
    """
    Get configured NotificationService instance.

    Returns:
        NotificationService instance
    """
    return NotificationService()
