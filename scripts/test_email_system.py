"""
Test Email System

Tests email template rendering and SMTP sending functionality.

Usage:
    python scripts/test_email_system.py

Author: Project Aura Team
Date: November 2024
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.email_system import EmailService, EmailTemplateEngine, get_email_service


def test_template_engine():
    """Test email template rendering."""
    print("\n" + "=" * 60)
    print("TEST 1: Email Template Engine")
    print("=" * 60)

    engine = EmailTemplateEngine()

    # Test 1: List templates
    print("\n✓ Available Templates:")
    templates = engine.list_templates()
    for template in templates:
        print(f"  - {template['id']}: {template['name']}")

    # Test 2: Render assignment notification
    print("\n✓ Rendering Assignment Notification:")
    context = {
        "account_code": "10010001",
        "account_name": "Cash and Cash Equivalents",
        "reviewer_name": "John Doe",
        "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "balance": 1234567.89,
        "entity": "AEML",
        "app_name": "Project Aura",
        "current_year": datetime.now().year,
    }

    result = engine.render_template("assignment_notification", context)
    print(f"  Subject: {result['subject']}")
    print(f"  Priority: {result['priority']}")
    print(f"  Body length: {len(result['body'])} characters")

    # Test 3: Render weekly summary
    print("\n✓ Rendering Weekly Summary:")
    context = {
        "week_ending": datetime.now().strftime("%Y-%m-%d"),
        "total_accounts": 100,
        "reviewed": 75,
        "pending": 25,
        "hygiene_score": 82,
        "top_accounts": [
            {"code": "10010001", "name": "Cash", "status": "pending", "balance": 1234567.89},
            {
                "code": "10010002",
                "name": "Accounts Receivable",
                "status": "overdue",
                "balance": 987654.32,
            },
        ],
        "app_name": "Project Aura",
        "current_year": datetime.now().year,
    }

    result = engine.render_template("weekly_summary", context)
    print(f"  Subject: {result['subject']}")
    print(f"  Body length: {len(result['body'])} characters")

    print("\n✅ Template Engine: ALL TESTS PASSED")
    return True


def test_smtp_connection():
    """Test SMTP connection."""
    print("\n" + "=" * 60)
    print("TEST 2: SMTP Connection")
    print("=" * 60)

    # Check environment variables
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    print(f"\n  SMTP Host: {smtp_host}")
    print(f"  Username: {smtp_username if smtp_username else '(not configured)'}")
    print(f"  Password: {'*' * len(smtp_password) if smtp_password else '(not configured)'}")

    if not smtp_username or not smtp_password:
        print("\n⚠️  SMTP credentials not configured in .env")
        print("  Set SMTP_USERNAME and SMTP_PASSWORD to test email sending")
        return False

    # Test connection
    service = get_email_service()
    success, message = service.test_connection()

    if success:
        print(f"\n✅ SMTP Connection: {message}")
        return True
    else:
        print(f"\n❌ SMTP Connection Failed: {message}")
        return False


def test_email_sending(send_test_email: bool = False):
    """Test email sending (optional)."""
    print("\n" + "=" * 60)
    print("TEST 3: Email Sending")
    print("=" * 60)

    if not send_test_email:
        print("\n⏭️  Skipping actual email send test (set send_test_email=True to enable)")
        return True

    # Get test email from environment
    test_email = os.getenv("TEST_EMAIL", "")

    if not test_email:
        print("\n⚠️  Test email address not configured")
        print("  Set TEST_EMAIL in .env to test email sending")
        return False

    print(f"\n  Sending test email to: {test_email}")

    # Create service and engine
    service = get_email_service()
    engine = EmailTemplateEngine()

    # Render template
    context = {
        "account_code": "TEST-001",
        "account_name": "Test Account",
        "reviewer_name": "Test User",
        "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "balance": 12345.67,
        "entity": "TEST",
        "app_name": "Project Aura",
        "current_year": datetime.now().year,
    }

    rendered = engine.render_template("assignment_notification", context)

    # Send email
    success, message = service.send_email(
        to_email=test_email,
        subject=rendered["subject"],
        body_html=rendered["body"],
        body_text="This is a test email from Project Aura email system.",
        metadata={"test": True, "template": "assignment_notification"},
    )

    if success:
        print(f"\n✅ Email Sent: {message}")
        return True
    else:
        print(f"\n❌ Email Failed: {message}")
        return False


def test_email_log():
    """Test email logging."""
    print("\n" + "=" * 60)
    print("TEST 4: Email Logging")
    print("=" * 60)

    service = get_email_service()

    # Get recent emails
    recent_emails = service.get_email_log(limit=5)

    print(f"\n  Recent emails: {len(recent_emails)}")
    for email in recent_emails[:3]:
        print(f"    - To: {email['to_email']}")
        print(f"      Subject: {email['subject']}")
        print(f"      Status: {email['status']}")
        print(f"      Time: {email['timestamp']}")
        print()

    # Get queue status
    queue_status = service.get_queue_status()
    print(f"  Email Queue:")
    print(f"    Total: {queue_status['total']}")
    print(f"    Queued: {queue_status['queued']}")
    print(f"    Sent: {queue_status['sent']}")

    print("\n✅ Email Logging: TEST PASSED")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PROJECT AURA - EMAIL SYSTEM TESTS")
    print("=" * 60)

    results = []

    # Test 1: Template Engine (always run)
    try:
        results.append(("Template Engine", test_template_engine()))
    except Exception as e:
        print(f"\n❌ Template Engine Test Failed: {e}")
        results.append(("Template Engine", False))

    # Test 2: SMTP Connection (skip if not configured)
    try:
        results.append(("SMTP Connection", test_smtp_connection()))
    except Exception as e:
        print(f"\n❌ SMTP Connection Test Failed: {e}")
        results.append(("SMTP Connection", False))

    # Test 3: Email Sending (skip by default)
    # Uncomment to enable: results.append(("Email Sending", test_email_sending(send_test_email=True)))

    # Test 4: Email Logging
    try:
        results.append(("Email Logging", test_email_log()))
    except Exception as e:
        print(f"\n❌ Email Logging Test Failed: {e}")
        results.append(("Email Logging", False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    print("=" * 60)


if __name__ == "__main__":
    main()
