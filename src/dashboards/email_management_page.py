"""
Email Management Dashboard

Streamlit page for email system administration:
- View sent emails log
- Preview email templates
- Test email sending
- Configure SMTP settings
- Manage email queue

Author: Project Aura Team
Date: November 2024
"""

import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from ..email_system import EmailTemplateEngine, get_email_service


def render_email_management_page():
    """Render the email management dashboard."""
    st.title("📧 Email Management")
    st.markdown("---")

    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📨 Email Log",
            "📝 Template Preview",
            "🧪 Test Email",
            "⚙️ SMTP Settings",
            "📥 Email Queue",
        ]
    )

    with tab1:
        render_email_log()

    with tab2:
        render_template_preview()

    with tab3:
        render_test_email()

    with tab4:
        render_smtp_settings()

    with tab5:
        render_email_queue()


def render_email_log():
    """Render email log viewer."""
    st.subheader("📨 Email Log")
    st.markdown("View history of sent emails and their status.")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox("Status", ["All", "sent", "failed"], key="email_log_status")

    with col2:
        recipient_filter = st.text_input(
            "Recipient Email", placeholder="Filter by email...", key="email_log_recipient"
        )

    with col3:
        limit = st.number_input(
            "Limit", min_value=10, max_value=500, value=50, step=10, key="email_log_limit"
        )

    # Get email service
    try:
        email_service = get_email_service()

        # Build query
        query_status = None if status_filter == "All" else status_filter
        query_recipient = recipient_filter if recipient_filter else None

        # Get emails
        emails = email_service.get_email_log(
            status=query_status, to_email=query_recipient, limit=limit
        )

        if emails:
            # Convert to DataFrame
            df = pd.DataFrame(emails)

            # Format timestamp
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

            # Select columns to display
            display_cols = ["timestamp", "to_email", "subject", "status", "attempt"]
            if "error" in df.columns:
                display_cols.append("error")

            df_display = df[display_cols].copy()

            # Display stats
            st.markdown("### 📊 Statistics")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Emails", len(df))

            with col2:
                sent_count = len(df[df["status"] == "sent"])
                st.metric("Sent Successfully", sent_count)

            with col3:
                failed_count = len(df[df["status"] == "failed"])
                st.metric("Failed", failed_count)

            st.markdown("---")

            # Display table
            st.markdown("### 📋 Email History")
            st.dataframe(
                df_display,
                use_container_width=True,
                height=400,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Time"),
                    "to_email": "Recipient",
                    "subject": "Subject",
                    "status": st.column_config.TextColumn(
                        "Status",
                    ),
                    "attempt": "Attempts",
                    "error": "Error Message",
                },
            )

            # Download button
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"email_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

        else:
            st.info("📭 No emails found. Try adjusting filters or send some test emails.")

    except Exception as e:
        st.error(f"❌ Error loading email log: {e!s}")


def render_template_preview():
    """Render template preview interface."""
    st.subheader("📝 Template Preview")
    st.markdown("Preview email templates with sample data.")

    # Get template engine
    try:
        engine = EmailTemplateEngine()
        templates = engine.list_templates()

        # Template selector
        template_options = {t["id"]: f"{t['name']} ({t['category']})" for t in templates}
        selected_template = st.selectbox(
            "Select Template",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x],
            key="template_preview_select",
        )

        if selected_template:
            # Get template info
            template_info = engine.get_template_info(selected_template)

            # Display template details
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Category", template_info["category"].upper())

            with col2:
                st.metric("Priority", template_info["priority"].upper())

            with col3:
                st.metric("Variables", len(template_info["variables"]))

            st.markdown("---")

            # Sample context data
            sample_contexts = {
                "assignment_notification": {
                    "account_code": "10010001",
                    "account_name": "Cash and Cash Equivalents",
                    "reviewer_name": "John Doe",
                    "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "balance": 1234567.89,
                    "entity": "AEML",
                    "app_name": "Project Aura",
                    "current_year": datetime.now().year,
                },
                "upload_reminder": {
                    "account_code": "10010001",
                    "reviewer_name": "John Doe",
                    "deadline": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                    "days_remaining": 2,
                    "docs_required": ["Bank statement", "Reconciliation", "Supporting documents"],
                    "app_name": "Project Aura",
                    "current_year": datetime.now().year,
                },
                "review_completion": {
                    "account_code": "10010001",
                    "account_name": "Cash and Cash Equivalents",
                    "reviewer_name": "John Doe",
                    "completion_date": datetime.now().strftime("%Y-%m-%d"),
                    "comments": "All documents verified and reconciled successfully.",
                    "hygiene_score": 85,
                    "app_name": "Project Aura",
                    "current_year": datetime.now().year,
                },
                "approval_notification": {
                    "account_code": "10010001",
                    "account_name": "Cash and Cash Equivalents",
                    "reviewer_name": "John Doe",
                    "approver_name": "Jane Smith",
                    "approval_date": datetime.now().strftime("%Y-%m-%d"),
                    "app_name": "Project Aura",
                    "current_year": datetime.now().year,
                },
                "sla_breach_alert": {
                    "account_code": "10010001",
                    "reviewer_name": "John Doe",
                    "deadline": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                    "days_overdue": 3,
                    "escalation_level": "high",
                    "entity": "AEML",
                    "app_name": "Project Aura",
                    "current_year": datetime.now().year,
                },
                "weekly_summary": {
                    "week_ending": datetime.now().strftime("%Y-%m-%d"),
                    "total_accounts": 100,
                    "reviewed": 75,
                    "pending": 25,
                    "hygiene_score": 82,
                    "top_accounts": [
                        {
                            "code": "10010001",
                            "name": "Cash",
                            "status": "pending",
                            "balance": 1234567.89,
                        },
                        {
                            "code": "20010001",
                            "name": "Receivables",
                            "status": "overdue",
                            "balance": 987654.32,
                        },
                    ],
                    "app_name": "Project Aura",
                    "current_year": datetime.now().year,
                },
            }

            # Get sample context
            context = sample_contexts.get(selected_template, {})

            # Render template
            try:
                rendered = engine.render_template(selected_template, context)

                # Display subject
                st.markdown("### 📬 Email Subject")
                st.info(rendered["subject"])

                # Display HTML preview
                st.markdown("### 📄 Email Body Preview")

                # Preview options
                col1, col2 = st.columns([3, 1])

                with col1:
                    preview_mode = st.radio(
                        "Preview Mode",
                        ["Rendered HTML", "HTML Source"],
                        horizontal=True,
                        key="preview_mode",
                    )

                with col2:
                    if st.button("📋 Copy HTML", use_container_width=True):
                        st.code(rendered["body"], language="html")

                if preview_mode == "Rendered HTML":
                    # Display rendered HTML in iframe
                    st.components.v1.html(rendered["body"], height=600, scrolling=True)
                else:
                    # Display HTML source
                    st.code(rendered["body"], language="html", line_numbers=True)

            except Exception as e:
                st.error(f"❌ Error rendering template: {e!s}")

    except Exception as e:
        st.error(f"❌ Error loading templates: {e!s}")


def render_test_email():
    """Render test email sending interface."""
    st.subheader("🧪 Test Email Sending")
    st.markdown("Send test emails to verify SMTP configuration.")

    # Warning about SMTP configuration
    smtp_configured = bool(os.getenv("SMTP_USERNAME") and os.getenv("SMTP_PASSWORD"))

    if not smtp_configured:
        st.warning(
            "⚠️ SMTP credentials not configured. "
            "Set SMTP_USERNAME and SMTP_PASSWORD in .env file to send emails."
        )

    # Test email form
    with st.form("test_email_form"):
        st.markdown("### 📝 Email Details")

        col1, col2 = st.columns(2)

        with col1:
            recipient_email = st.text_input(
                "Recipient Email *",
                placeholder="test@example.com",
                help="Email address to send test email to",
            )

        with col2:
            # Get templates
            engine = EmailTemplateEngine()
            templates = engine.list_templates()
            template_options = {t["id"]: t["name"] for t in templates}

            selected_template = st.selectbox(
                "Template *",
                options=list(template_options.keys()),
                format_func=lambda x: template_options[x],
            )

        # Submit button
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            send_button = st.form_submit_button("📤 Send Test Email", use_container_width=True)

        with col2:
            preview_button = st.form_submit_button("👁️ Preview", use_container_width=True)

    # Handle form submission
    if send_button:
        if not recipient_email:
            st.error("❌ Please enter a recipient email address.")
        elif not smtp_configured:
            st.error("❌ SMTP credentials not configured. Please set up SMTP in .env file.")
        else:
            with st.spinner("Sending email..."):
                try:
                    # Get services
                    email_service = get_email_service()

                    # Sample context (using same as preview)
                    context = {
                        "account_code": "TEST-001",
                        "account_name": "Test Account",
                        "reviewer_name": "Test User",
                        "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                        "balance": 12345.67,
                        "entity": "TEST",
                        "app_name": "Project Aura",
                        "current_year": datetime.now().year,
                        "completion_date": datetime.now().strftime("%Y-%m-%d"),
                        "comments": "This is a test email.",
                        "hygiene_score": 85,
                        "approver_name": "Test Approver",
                        "approval_date": datetime.now().strftime("%Y-%m-%d"),
                        "days_remaining": 2,
                        "days_overdue": 0,
                        "escalation_level": "medium",
                        "week_ending": datetime.now().strftime("%Y-%m-%d"),
                        "total_accounts": 100,
                        "reviewed": 75,
                        "pending": 25,
                        "top_accounts": [],
                    }

                    # Render template
                    rendered = engine.render_template(selected_template, context)

                    # Send email
                    success, message = email_service.send_email(
                        to_email=recipient_email,
                        subject=f"[TEST] {rendered['subject']}",
                        body_html=rendered["body"],
                        metadata={"test": True, "template": selected_template},
                    )

                    if success:
                        st.success(f"✅ Test email sent successfully to {recipient_email}!")
                        st.info(f"📨 Subject: {rendered['subject']}")
                    else:
                        st.error(f"❌ Failed to send email: {message}")

                except Exception as e:
                    st.error(f"❌ Error sending test email: {e!s}")

    if preview_button:
        if selected_template:
            st.info(f"👁️ Preview for: {template_options[selected_template]}")


def render_smtp_settings():
    """Render SMTP settings interface."""
    st.subheader("⚙️ SMTP Settings")
    st.markdown("Configure email server settings.")

    # Current settings
    st.markdown("### 📋 Current Configuration")

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)
    smtp_from_name = os.getenv("SMTP_FROM_NAME", "Project Aura")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("SMTP Host", value=smtp_host, disabled=True)
        st.text_input("SMTP Port", value=smtp_port, disabled=True)
        st.text_input("Username", value=smtp_username or "(not configured)", disabled=True)

    with col2:
        st.text_input("From Email", value=smtp_from_email or "(not configured)", disabled=True)
        st.text_input("From Name", value=smtp_from_name, disabled=True)
        password_display = "*" * len(smtp_password) if smtp_password else "(not configured)"
        st.text_input("Password", value=password_display, disabled=True, type="password")

    st.markdown("---")

    # Test connection
    st.markdown("### 🔌 Connection Test")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🧪 Test Connection", use_container_width=True):
            if not smtp_username or not smtp_password:
                st.error("❌ SMTP credentials not configured.")
            else:
                with st.spinner("Testing SMTP connection..."):
                    try:
                        email_service = get_email_service()
                        success, message = email_service.test_connection()

                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")

                    except Exception as e:
                        st.error(f"❌ Connection test failed: {e!s}")

    # Configuration guide
    st.markdown("---")
    st.markdown("### 📚 Configuration Guide")

    with st.expander("📖 How to Configure SMTP"):
        st.markdown(
            """
        **Environment Variables (in `.env` file):**

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
        ```

        **Gmail Setup:**
        1. Enable 2-factor authentication
        2. Generate app password: https://myaccount.google.com/apppasswords
        3. Use app password (not your regular password)

        **SendGrid Setup:**
        1. Sign up at https://sendgrid.com
        2. Verify sender identity
        3. Generate API key
        4. Use 'apikey' as username and API key as password

        **After configuration:**
        - Restart the application
        - Test connection using the button above
        - Send test email in the "Test Email" tab
        """
        )


def render_email_queue():
    """Render email queue management interface."""
    st.subheader("📥 Email Queue")
    st.markdown("Manage failed emails and retry queue.")

    try:
        email_service = get_email_service()

        # Get queue status
        queue_status = email_service.get_queue_status()

        # Display stats
        st.markdown("### 📊 Queue Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total in Queue", queue_status["total"])

        with col2:
            st.metric("Pending Retry", queue_status["queued"])

        with col3:
            st.metric("Successfully Sent", queue_status["sent"])

        st.markdown("---")

        # Queue actions
        st.markdown("### ⚡ Queue Actions")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            retry_limit = st.number_input(
                "Retry Limit",
                min_value=1,
                max_value=50,
                value=10,
                help="Maximum number of emails to retry",
            )

        with col2:
            if st.button("🔄 Retry Failed Emails", use_container_width=True):
                if queue_status["queued"] == 0:
                    st.info("📭 No emails in queue to retry.")
                else:
                    with st.spinner(f"Retrying up to {retry_limit} queued emails..."):
                        try:
                            results = email_service.retry_queued_emails(limit=retry_limit)

                            st.success(
                                f"✅ Retry complete: {results['success']} sent, "
                                f"{results['failed']} failed"
                            )

                            # Refresh page
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error retrying emails: {e!s}")

        # Display queue details if there are items
        if queue_status["total"] > 0:
            st.markdown("---")
            st.markdown("### 📋 Queue Details")

            # Get queue items from MongoDB
            db = email_service.db
            queue_collection = db["email_queue"]

            queue_items = list(queue_collection.find().sort("created_at", -1).limit(50))

            if queue_items:
                # Convert to DataFrame
                df = pd.DataFrame(queue_items)

                # Format dates
                if "created_at" in df.columns:
                    df["created_at"] = pd.to_datetime(df["created_at"])
                    df["created_at"] = df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")

                # Select columns
                display_cols = ["created_at", "to_email", "subject", "status", "retry_count"]
                if "last_error" in df.columns:
                    display_cols.append("last_error")

                df_display = df[display_cols].copy()

                # Display table
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    height=300,
                    column_config={
                        "created_at": "Created",
                        "to_email": "Recipient",
                        "subject": "Subject",
                        "status": "Status",
                        "retry_count": "Retries",
                        "last_error": "Error",
                    },
                )
        else:
            st.info("📭 Email queue is empty. All emails sent successfully!")

    except Exception as e:
        st.error(f"❌ Error loading email queue: {e!s}")


# Main entry point
if __name__ == "__main__":
    render_email_management_page()
