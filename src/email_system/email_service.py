"""
Email Service Module

Handles SMTP email sending with retry logic, queue management, and error handling.
Supports Gmail, SendGrid, and custom SMTP servers.

Author: Project Aura Team
Date: November 2024
"""

import logging
import os
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bson import ObjectId

from ..db.mongodb import get_mongo_database

# Configure logging
logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails via SMTP with retry logic and queue management.

    Features:
    - SMTP integration (Gmail, SendGrid, custom)
    - Retry logic with exponential backoff
    - Failed email queue (MongoDB)
    - Bulk email sending
    - Email logging and tracking
    """

    def __init__(
        self,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        smtp_username: str | None = None,
        smtp_password: str | None = None,
        smtp_use_tls: bool = True,
        from_email: str | None = None,
        from_name: str | None = None,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        """
        Initialize EmailService with SMTP configuration.

        Args:
            smtp_host: SMTP server host (e.g., smtp.gmail.com)
            smtp_port: SMTP server port (e.g., 587 for TLS, 465 for SSL)
            smtp_username: SMTP authentication username
            smtp_password: SMTP authentication password
            smtp_use_tls: Whether to use TLS encryption
            from_email: Default sender email address
            from_name: Default sender name
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
        """
        # Load from environment variables if not provided
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = smtp_username or os.getenv("SMTP_USERNAME", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = smtp_use_tls

        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL", self.smtp_username)
        self.from_name = from_name or os.getenv("SMTP_FROM_NAME", "Project Aura")

        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # MongoDB collections
        self.db = get_mongo_database()
        self.email_log_collection = self.db["email_log"]
        self.email_queue_collection = self.db["email_queue"]

        logger.info(f"EmailService initialized with {self.smtp_host}:{self.smtp_port}")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        reply_to: str | None = None,
        attachments: list[dict] | None = None,
        metadata: dict | None = None,
    ) -> tuple[bool, str]:
        """
        Send an email with retry logic.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body (fallback)
            cc: CC recipients
            bcc: BCC recipients
            reply_to: Reply-to address
            attachments: List of attachments (not implemented yet)
            metadata: Additional metadata to log

        Returns:
            Tuple of (success: bool, message: str)
        """
        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            try:
                # Create message
                msg = self._create_message(
                    to_email=to_email,
                    subject=subject,
                    body_html=body_html,
                    body_text=body_text,
                    cc=cc,
                    bcc=bcc,
                    reply_to=reply_to,
                )

                # Send via SMTP
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    if self.smtp_use_tls:
                        server.starttls()

                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)

                    server.send_message(msg)

                # Log success
                self._log_email(
                    to_email=to_email,
                    subject=subject,
                    status="sent",
                    attempt=attempt + 1,
                    metadata=metadata,
                )

                logger.info(f"Email sent successfully to {to_email}: {subject}")
                return True, "Email sent successfully"

            except smtplib.SMTPAuthenticationError as e:
                last_error = f"Authentication failed: {e!s}"
                logger.error(f"SMTP authentication error: {e}")
                # Don't retry auth errors
                break

            except smtplib.SMTPException as e:
                last_error = f"SMTP error: {e!s}"
                logger.warning(f"SMTP error on attempt {attempt + 1}/{self.max_retries}: {e}")

            except Exception as e:
                last_error = f"Unexpected error: {e!s}"
                logger.error(f"Unexpected error sending email: {e}")

            attempt += 1

            if attempt < self.max_retries:
                # Exponential backoff
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)

        # All retries failed - add to queue
        self._add_to_queue(
            to_email=to_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            metadata=metadata,
            error=last_error,
        )

        # Log failure
        self._log_email(
            to_email=to_email,
            subject=subject,
            status="failed",
            attempt=attempt,
            error=last_error,
            metadata=metadata,
        )

        logger.error(f"Failed to send email to {to_email} after {attempt} attempts: {last_error}")
        return False, last_error or "Failed to send email"

    def send_bulk_email(
        self,
        recipients: list[str],
        subject: str,
        body_html: str,
        body_text: str | None = None,
        metadata: dict | None = None,
    ) -> dict[str, list[str]]:
        """
        Send the same email to multiple recipients.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body
            metadata: Additional metadata to log

        Returns:
            Dict with 'success' and 'failed' lists of email addresses
        """
        results = {
            "success": [],
            "failed": [],
        }

        logger.info(f"Sending bulk email to {len(recipients)} recipients: {subject}")

        for recipient in recipients:
            success, message = self.send_email(
                to_email=recipient,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                metadata=metadata,
            )

            if success:
                results["success"].append(recipient)
            else:
                results["failed"].append(recipient)

        logger.info(
            f"Bulk email complete: {len(results['success'])} sent, "
            f"{len(results['failed'])} failed"
        )

        return results

    def retry_queued_emails(self, limit: int = 10) -> dict[str, int]:
        """
        Retry sending failed emails from the queue.

        Args:
            limit: Maximum number of emails to retry

        Returns:
            Dict with counts of successful and failed retries
        """
        queued_emails = list(self.email_queue_collection.find({"status": "queued"}).limit(limit))

        results = {"success": 0, "failed": 0}

        logger.info(f"Retrying {len(queued_emails)} queued emails")

        for email in queued_emails:
            success, message = self.send_email(
                to_email=email["to_email"],
                subject=email["subject"],
                body_html=email["body_html"],
                body_text=email.get("body_text"),
                cc=email.get("cc"),
                bcc=email.get("bcc"),
                reply_to=email.get("reply_to"),
                metadata=email.get("metadata"),
            )

            if success:
                # Remove from queue
                self.email_queue_collection.update_one(
                    {"_id": email["_id"]},
                    {"$set": {"status": "sent", "sent_at": datetime.utcnow()}},
                )
                results["success"] += 1
            else:
                # Update retry count
                self.email_queue_collection.update_one(
                    {"_id": email["_id"]},
                    {
                        "$inc": {"retry_count": 1},
                        "$set": {"last_retry_at": datetime.utcnow()},
                    },
                )
                results["failed"] += 1

        logger.info(f"Queue retry complete: {results['success']} sent, {results['failed']} failed")

        return results

    def get_email_log(
        self,
        status: str | None = None,
        to_email: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        Get email log entries.

        Args:
            status: Filter by status (sent, failed)
            to_email: Filter by recipient email
            limit: Maximum number of entries to return

        Returns:
            List of email log entries
        """
        query = {}

        if status:
            query["status"] = status

        if to_email:
            query["to_email"] = to_email

        emails = list(self.email_log_collection.find(query).sort("timestamp", -1).limit(limit))

        # Convert ObjectId to string for JSON serialization
        for email in emails:
            email["_id"] = str(email["_id"])

        return emails

    def get_queue_status(self) -> dict[str, int]:
        """
        Get email queue statistics.

        Returns:
            Dict with queue counts by status
        """
        total = self.email_queue_collection.count_documents({})
        queued = self.email_queue_collection.count_documents({"status": "queued"})
        sent = self.email_queue_collection.count_documents({"status": "sent"})

        return {
            "total": total,
            "queued": queued,
            "sent": sent,
        }

    def test_connection(self) -> tuple[bool, str]:
        """
        Test SMTP connection and authentication.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.smtp_use_tls:
                    server.starttls()

                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)

                logger.info("SMTP connection test successful")
                return True, "Connection successful"

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False, f"Authentication failed: {e!s}"

        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False, f"Connection failed: {e!s}"

    def _create_message(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        reply_to: str | None = None,
    ) -> MIMEMultipart:
        """
        Create MIME message for email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body
            cc: CC recipients
            bcc: BCC recipients
            reply_to: Reply-to address

        Returns:
            MIMEMultipart message object
        """
        msg = MIMEMultipart("alternative")

        # Set headers
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        if cc:
            msg["Cc"] = ", ".join(cc)

        if bcc:
            msg["Bcc"] = ", ".join(bcc)

        if reply_to:
            msg["Reply-To"] = reply_to

        # Add bodies
        if body_text:
            part_text = MIMEText(body_text, "plain")
            msg.attach(part_text)

        part_html = MIMEText(body_html, "html")
        msg.attach(part_html)

        return msg

    def _log_email(
        self,
        to_email: str,
        subject: str,
        status: str,
        attempt: int,
        error: str | None = None,
        metadata: dict | None = None,
    ) -> ObjectId:
        """
        Log email send attempt to MongoDB.

        Args:
            to_email: Recipient email address
            subject: Email subject
            status: Send status (sent, failed)
            attempt: Attempt number
            error: Error message if failed
            metadata: Additional metadata

        Returns:
            MongoDB ObjectId of log entry
        """
        log_entry = {
            "to_email": to_email,
            "subject": subject,
            "status": status,
            "attempt": attempt,
            "timestamp": datetime.utcnow(),
            "from_email": self.from_email,
        }

        if error:
            log_entry["error"] = error

        if metadata:
            log_entry["metadata"] = metadata

        result = self.email_log_collection.insert_one(log_entry)
        return result.inserted_id

    def _add_to_queue(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        reply_to: str | None = None,
        metadata: dict | None = None,
        error: str | None = None,
    ) -> ObjectId:
        """
        Add failed email to queue for retry.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body
            cc: CC recipients
            bcc: BCC recipients
            reply_to: Reply-to address
            metadata: Additional metadata
            error: Error message

        Returns:
            MongoDB ObjectId of queue entry
        """
        queue_entry = {
            "to_email": to_email,
            "subject": subject,
            "body_html": body_html,
            "body_text": body_text,
            "cc": cc,
            "bcc": bcc,
            "reply_to": reply_to,
            "metadata": metadata,
            "status": "queued",
            "retry_count": 0,
            "created_at": datetime.utcnow(),
            "last_error": error,
        }

        result = self.email_queue_collection.insert_one(queue_entry)
        logger.info(f"Added email to queue: {to_email} - {subject}")
        return result.inserted_id


# Convenience function to get configured email service
def get_email_service() -> EmailService:
    """
    Get configured EmailService instance.

    Returns:
        EmailService instance with environment configuration
    """
    return EmailService()
