"""
Email Package for Project Aura.

Handles email template management, SMTP sending, and automated notifications.
"""

from .email_service import EmailService, get_email_service
from .notification_service import NotificationService, get_notification_service
from .template_engine import EmailTemplateEngine

__all__ = [
    "EmailTemplateEngine",
    "EmailService",
    "get_email_service",
    "NotificationService",
    "get_notification_service",
]
