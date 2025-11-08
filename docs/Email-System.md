# Email Automation System - Documentation

## Overview

The **Email Automation System** provides automated email notifications for GL account review lifecycle events in Project Aura. Built with Python, Jinja2, SMTP, and MongoDB, it delivers responsive, professional emails to stakeholders.

## Features

✅ **6 Email Templates** - Responsive HTML templates for all notification types
✅ **SMTP Integration** - Support for Gmail, SendGrid, and custom SMTP servers
✅ **Retry Logic** - Exponential backoff with 3 automatic retries
✅ **Email Queue** - Failed emails stored in MongoDB for later retry
✅ **Event Triggers** - Automated notifications based on review lifecycle
✅ **Management UI** - Streamlit dashboard for monitoring and testing
✅ **Email Logging** - Complete audit trail in MongoDB

## Architecture

### Components

1. **EmailTemplateEngine** (`src/email/template_engine.py`)
   - Jinja2-based template rendering
   - Custom filters for currency and date formatting
   - 6 registered template types
   - Template validation and fallback

2. **EmailService** (`src/email/email_service.py`)
   - SMTP email sending
   - Retry logic with exponential backoff
   - Email queue management (MongoDB)
   - Connection testing

3. **NotificationService** (`src/email/notification_service.py`)
   - Event-triggered notifications
   - PostgreSQL/MongoDB integration
   - Recipient lookup from responsibility matrix
   - Weekly summary generation

4. **Email Management UI** (`src/dashboards/email_management_page.py`)
   - Email log viewer
   - Template preview
   - Test email sending
   - SMTP configuration display
   - Queue management

## Email Templates

### 1. Assignment Notification
**Trigger:** GL account assigned to reviewer
**Priority:** High
**Recipients:** Assigned reviewer
**Content:** Account details, deadline, balance, required actions

### 2. Upload Reminder
**Trigger:** 2 days before deadline (no documents uploaded)
**Priority:** Medium
**Recipients:** Assigned reviewer
**Content:** Countdown, required documents, SLA warning

### 3. Review Completion
**Trigger:** Review status changed to "Reviewed"
**Priority:** Medium
**Recipients:** Reviewer + Approver
**Content:** Completion details, hygiene score, comments, next steps

### 4. Approval Notification
**Trigger:** Account approved by approver
**Priority:** Medium
**Recipients:** Reviewer + Approver
**Content:** Approval details, team recognition, completion badge

### 5. SLA Breach Alert
**Trigger:** Review deadline exceeded
**Priority:** High/Critical
**Recipients:** Reviewer + Managers (escalation)
**Content:** Days overdue, escalation level, immediate actions required

### 6. Weekly Summary
**Trigger:** Every Monday 9:00 AM
**Priority:** Low
**Recipients:** Managers + Stakeholders
**Content:** Review statistics, hygiene score, top accounts, performance insights

## SMTP Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# Gmail Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Project Aura

# SendGrid Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=verified-sender@yourdomain.com
SMTP_FROM_NAME=Project Aura

# Custom SMTP
SMTP_HOST=smtp.yourserver.com
SMTP_PORT=587
SMTP_USERNAME=smtp-user
SMTP_PASSWORD=smtp-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Project Aura
```

### Gmail Setup

1. **Enable 2-Factor Authentication**
   - Go to Google Account settings
   - Security → 2-Step Verification → Enable

2. **Generate App Password**
   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Project Aura"
   - Copy the 16-character password

3. **Configure .env**
   ```bash
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App password
   ```

### SendGrid Setup

1. **Create SendGrid Account**
   - Sign up at https://sendgrid.com
   - Free tier: 100 emails/day

2. **Verify Sender Identity**
   - Settings → Sender Authentication
   - Verify email address or domain

3. **Generate API Key**
   - Settings → API Keys → Create API Key
   - Name: "Project Aura"
   - Permissions: Full Access
   - Copy the API key

4. **Configure .env**
   ```bash
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx  # API key
   SMTP_FROM_EMAIL=verified-sender@yourdomain.com
   ```

## Usage Examples

### 1. Send Assignment Notification

```python
from datetime import datetime, timedelta
from src.email import get_notification_service

# Initialize service
notif_service = get_notification_service()

# Send assignment notification
success = notif_service.on_assignment(
    account_code="10010001",
    reviewer_email="john.doe@example.com",
    reviewer_name="John Doe",
    deadline=datetime.now() + timedelta(days=7),
    entity="AEML",
    metadata={"assigned_by": "system"}
)

print(f"Notification sent: {success}")
```

### 2. Send Weekly Summary

```python
from src.email import get_notification_service

notif_service = get_notification_service()

# Send to multiple recipients
recipients = [
    "manager1@example.com",
    "manager2@example.com",
    "cfo@example.com"
]

success = notif_service.send_weekly_summary(
    recipient_emails=recipients,
    period="Mar-24",
    entity="AEML"
)

print(f"Weekly summary sent: {success}")
```

### 3. Preview Template

```python
from datetime import datetime
from src.email import EmailTemplateEngine

engine = EmailTemplateEngine()

# Sample context
context = {
    "account_code": "10010001",
    "account_name": "Cash and Cash Equivalents",
    "reviewer_name": "John Doe",
    "deadline": "2024-11-15",
    "balance": 1234567.89,
    "entity": "AEML",
    "app_name": "Project Aura",
    "current_year": datetime.now().year,
}

# Render template
rendered = engine.render_template("assignment_notification", context)

print(f"Subject: {rendered['subject']}")
print(f"Priority: {rendered['priority']}")
print(f"Body length: {len(rendered['body'])} characters")
```

### 4. Test SMTP Connection

```python
from src.email import get_email_service

email_service = get_email_service()

success, message = email_service.test_connection()

if success:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
```

### 5. Retry Failed Emails

```python
from src.email import get_email_service

email_service = get_email_service()

# Retry up to 10 failed emails
results = email_service.retry_queued_emails(limit=10)

print(f"Retry complete: {results['success']} sent, {results['failed']} failed")
```

## Testing

### Run Test Suite

```bash
# Activate environment
conda activate finnovate-hackathon

# Run email system tests
python scripts/test_email_system.py
```

### Test Results

```
✅ Template Engine: PASSED
   - 6 templates available
   - Rendering successful
   - Custom filters working

✅ Email Logging: PASSED
   - MongoDB collections created
   - Logging functional

⚠️  SMTP Connection: Not configured (expected)
   - Set SMTP credentials to enable
```

### Manual Testing

1. **Access Email Management UI**
   ```bash
   streamlit run src/app.py
   ```
   Navigate to: 📧 Email Management

2. **Preview Templates**
   - Go to "Template Preview" tab
   - Select template
   - View rendered HTML

3. **Test Email Sending**
   - Go to "Test Email" tab
   - Enter recipient email
   - Select template
   - Click "Send Test Email"

4. **Monitor Email Log**
   - Go to "Email Log" tab
   - Filter by status/recipient
   - Download CSV report

## Troubleshooting

### Common Issues

#### 1. SMTP Authentication Failed

**Error:** `SMTPAuthenticationError: Username and Password not accepted`

**Solutions:**
- **Gmail:** Use app password, not regular password
- **SendGrid:** Use 'apikey' as username
- **Check credentials:** Verify username and password in .env
- **2FA enabled:** Generate app-specific password

#### 2. Connection Timeout

**Error:** `SMTPServerDisconnected: Connection unexpectedly closed`

**Solutions:**
- Check firewall/network settings
- Verify SMTP host and port
- Try alternative port (465 for SSL, 587 for TLS)
- Check if SMTP server is accessible

#### 3. Emails Going to Spam

**Solutions:**
- Use authenticated SMTP server
- Verify sender domain (SPF, DKIM, DMARC)
- Use professional email service (SendGrid)
- Test with different recipients
- Check email content for spam triggers

#### 4. Template Rendering Errors

**Error:** `UndefinedError: 'variable_name' is undefined`

**Solutions:**
- Check context has all required variables
- Review template variable names
- Use get_template_info() to see required variables
- Verify Jinja2 syntax in template

#### 5. Queue Not Retrying

**Solutions:**
- Check MongoDB connection
- Verify email_queue collection exists
- Run retry_queued_emails() manually
- Check retry_count limits
- Review error messages in queue

### Debug Mode

Enable debug logging:

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test email sending with detailed logs
from src.email import get_email_service

email_service = get_email_service()
email_service.send_email(...)
```

## Template Customization

### Modify Existing Templates

1. Edit HTML template files in `src/email/templates/`
2. Use Jinja2 syntax for dynamic content: `{{ variable_name }}`
3. Use filters: `{{ balance | currency }}`, `{{ date | date }}`
4. Test in "Template Preview" tab
5. Restart application to reload templates

### Add New Template

1. **Create HTML Template**
   ```html
   <!-- src/email/templates/custom_notification.html -->
   <!DOCTYPE html>
   <html>
   <body>
       <h1>{{ title }}</h1>
       <p>{{ message }}</p>
   </body>
   </html>
   ```

2. **Register Template**
   ```python
   # In EmailTemplateEngine._load_template_registry()
   'custom_notification': {
       'name': 'Custom Notification',
       'subject': 'Custom: {{ title }}',
       'category': 'notification',
       'priority': 'medium',
       'variables': ['title', 'message', 'app_name', 'current_year']
   }
   ```

3. **Use Template**
   ```python
   from src.email import EmailTemplateEngine

   engine = EmailTemplateEngine()
   rendered = engine.render_template('custom_notification', {
       'title': 'Test',
       'message': 'Hello!',
       'app_name': 'Project Aura',
       'current_year': 2024
   })
   ```

## MongoDB Collections

### email_log
Stores sent email audit trail.

**Schema:**
```json
{
  "_id": ObjectId,
  "to_email": "john@example.com",
  "subject": "New GL Account Assignment",
  "status": "sent",
  "attempt": 1,
  "timestamp": ISODate,
  "from_email": "noreply@projectaura.com",
  "error": null,
  "metadata": {
    "event": "assignment",
    "account_code": "10010001"
  }
}
```

### email_queue
Stores failed emails for retry.

**Schema:**
```json
{
  "_id": ObjectId,
  "to_email": "john@example.com",
  "subject": "New GL Account Assignment",
  "body_html": "<html>...",
  "body_text": "Plain text...",
  "status": "queued",
  "retry_count": 2,
  "created_at": ISODate,
  "last_retry_at": ISODate,
  "last_error": "Connection timeout"
}
```

### notification_log
Stores notification trigger events.

**Schema:**
```json
{
  "_id": ObjectId,
  "event": "assignment",
  "recipient": "john@example.com",
  "account_code": "10010001",
  "success": true,
  "message": "Email sent successfully",
  "timestamp": ISODate
}
```

## Performance

### Email Sending

- **Average send time:** 1-2 seconds per email
- **Bulk sending:** 10-20 emails/minute
- **Retry delay:** 5s, 10s, 20s (exponential backoff)
- **Queue processing:** 10 emails per batch

### Template Rendering

- **Render time:** <100ms per template
- **Cache:** Templates loaded once at initialization
- **Fallback:** <50ms for simple HTML generation

## Security

### Best Practices

1. **Environment Variables**
   - Never commit `.env` to git
   - Use strong passwords
   - Rotate credentials regularly

2. **SMTP Authentication**
   - Use app passwords (not account password)
   - Enable 2FA on email accounts
   - Use TLS encryption

3. **Email Content**
   - Sanitize user inputs
   - Validate email addresses
   - Avoid exposing sensitive data

4. **Access Control**
   - Restrict Email Management UI access
   - Log all email operations
   - Monitor for suspicious activity

## Production Deployment

### Checklist

- [ ] Configure production SMTP credentials
- [ ] Test email sending with production data
- [ ] Set up email monitoring/alerting
- [ ] Configure weekly summary cron job
- [ ] Enable email queue retry scheduler
- [ ] Set up email logs backup
- [ ] Configure rate limiting
- [ ] Test spam filters
- [ ] Verify sender domain authentication
- [ ] Document runbook for issues

### Cron Jobs

```bash
# Weekly summary (Monday 9 AM)
0 9 * * 1 python scripts/send_weekly_summary.py

# Retry failed emails (every hour)
0 * * * * python scripts/retry_email_queue.py

# Check SLA breaches (every 6 hours)
0 */6 * * * python scripts/check_sla_breaches.py

# Send reminders (daily at 10 AM)
0 10 * * * python scripts/send_reminders.py
```

## Support

### Resources

- **Documentation:** `docs/Email-System.md`
- **Test Script:** `scripts/test_email_system.py`
- **Management UI:** Streamlit → 📧 Email Management
- **Code:** `src/email/`

### Contact

For issues or questions:
- GitHub Issues: [Project Repository]
- Email: support@projectaura.com
- Team: Project Aura Finnovate 2024

---

**Last Updated:** November 8, 2024
**Version:** 1.0.0
**Author:** Project Aura Team
