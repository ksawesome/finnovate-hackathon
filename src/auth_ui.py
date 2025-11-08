"""
Authentication UI Components

Streamlit components for login, signup, and password reset.

Author: Project Aura Team
Date: November 2024
"""

import streamlit as st

from .auth import AuthService


def render_login_page():
    """Render the login/signup page."""
    # Custom CSS for auth pages
    st.markdown(
        """
        <style>
            .auth-container {
                max-width: 500px;
                margin: 50px auto;
                padding: 30px;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .auth-header {
                text-align: center;
                color: #1f77b4;
                margin-bottom: 30px;
            }
            .auth-logo {
                text-align: center;
                font-size: 48px;
                margin-bottom: 10px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Center container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Logo and title
        st.markdown('<div class="auth-logo">💼</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="auth-header">Project Aura</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align: center; color: #666; margin-bottom: 30px;">AI-Powered Financial Review Agent</p>',
            unsafe_allow_html=True,
        )

        # Tabs for Login and Signup
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "✍️ Sign Up", "🔑 Forgot Password"])

        with tab1:
            render_login_form()

        with tab2:
            render_signup_form()

        with tab3:
            render_forgot_password_form()


def render_login_form():
    """Render the login form."""
    st.markdown("### Welcome Back!")
    st.markdown("Login to access your account")

    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="your.email@example.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

        st.markdown("")  # Spacing

        col1, col2 = st.columns([1, 1])
        with col1:
            remember_me = st.checkbox("Remember me")

        submit_button = st.form_submit_button("🚀 Login", use_container_width=True)

        if submit_button:
            if not email or not password:
                st.error("❌ Please enter both email and password")
            else:
                with st.spinner("Authenticating..."):
                    result = AuthService.login_user(email, password)

                    if result["success"]:
                        # Store user data in session
                        user_data = result["user"]
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_data["id"]
                        st.session_state.user_name = user_data["name"]
                        st.session_state.user_email = user_data["email"]
                        st.session_state.user_role = user_data["role"]
                        st.session_state.user_department = user_data["department"]

                        st.success(f"✅ {result['message']}")
                        st.balloons()

                        # Wait a moment then rerun
                        import time

                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")


def render_signup_form():
    """Render the signup form."""
    st.markdown("### Create Your Account")
    st.markdown("Join Project Aura to start reviewing GL accounts")

    with st.form("signup_form"):
        name = st.text_input("👤 Full Name", placeholder="John Doe")
        email = st.text_input("📧 Email", placeholder="john.doe@example.com")

        col1, col2 = st.columns(2)
        with col1:
            department = st.selectbox(
                "🏢 Department", ["Finance", "Accounting", "Audit", "Treasury", "Tax", "Other"]
            )
        with col2:
            role = st.selectbox("👔 Role", ["Reviewer", "Approver", "Manager", "Admin"])

        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Min 8 chars, with upper, lower, digit, special",
        )
        confirm_password = st.text_input(
            "🔒 Confirm Password", type="password", placeholder="Re-enter your password"
        )

        st.markdown("")  # Spacing

        agree_terms = st.checkbox("I agree to the Terms & Conditions and Privacy Policy")

        submit_button = st.form_submit_button("📝 Sign Up", use_container_width=True)

        if submit_button:
            # Validation
            if not all([name, email, password, confirm_password]):
                st.error("❌ Please fill in all fields")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            elif not agree_terms:
                st.error("❌ Please agree to the Terms & Conditions")
            else:
                with st.spinner("Creating your account..."):
                    result = AuthService.register_user(
                        name=name, email=email, password=password, department=department, role=role
                    )

                    if result["success"]:
                        st.success(f"✅ {result['message']}")
                        st.info("👉 Please go to the Login tab to sign in")
                        st.balloons()
                    else:
                        st.error(f"❌ {result['message']}")


def render_forgot_password_form():
    """Render the forgot password form."""
    st.markdown("### Reset Your Password")
    st.markdown("Enter your email to receive a password reset link")

    # Step 1: Request reset
    if "reset_token_requested" not in st.session_state:
        st.session_state.reset_token_requested = False

    if not st.session_state.reset_token_requested:
        with st.form("forgot_password_form"):
            email = st.text_input("📧 Email", placeholder="your.email@example.com")

            submit_button = st.form_submit_button("📨 Send Reset Link", use_container_width=True)

            if submit_button:
                if not email:
                    st.error("❌ Please enter your email address")
                else:
                    with st.spinner("Processing request..."):
                        success, token, message = AuthService.generate_reset_token(email)

                        if success:
                            st.success("✅ Password reset instructions sent to your email")
                            st.info(
                                "💡 In a real environment, you would receive an email. For demo purposes, we'll show the reset form below."
                            )

                            # For demo, store token in session
                            st.session_state.reset_token = token
                            st.session_state.reset_token_requested = True
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

    # Step 2: Reset password (demo - normally via email link)
    else:
        st.info("✉️ Reset link sent! Enter your new password below:")

        with st.form("reset_password_form"):
            # In production, token would come from email link
            # For demo, we'll use a text input
            token = st.text_input(
                "🔑 Reset Token",
                value=st.session_state.get("reset_token", ""),
                help="In production, this comes from email link",
            )
            new_password = st.text_input(
                "🔒 New Password",
                type="password",
                placeholder="Min 8 chars, with upper, lower, digit, special",
            )
            confirm_password = st.text_input(
                "🔒 Confirm New Password", type="password", placeholder="Re-enter your new password"
            )

            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("🔄 Reset Password", use_container_width=True)
            with col2:
                cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)

            if cancel_button:
                st.session_state.reset_token_requested = False
                st.session_state.reset_token = None
                st.rerun()

            if submit_button:
                if not all([token, new_password, confirm_password]):
                    st.error("❌ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    with st.spinner("Resetting password..."):
                        success, message = AuthService.reset_password(token, new_password)

                        if success:
                            st.success(f"✅ {message}")
                            st.info(
                                "👉 Please go to the Login tab to sign in with your new password"
                            )

                            # Clear reset state
                            st.session_state.reset_token_requested = False
                            st.session_state.reset_token = None
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")


def render_user_menu():
    """Render user menu in sidebar (when logged in)."""
    if not AuthService.is_authenticated():
        return

    user = AuthService.get_current_user()

    # Get first initial for avatar
    initial = user["name"][0].upper() if user["name"] else "?"

    # Format last login time
    from datetime import datetime

    last_login = user.get("last_login")
    if last_login:
        if isinstance(last_login, str):
            try:
                last_login = datetime.fromisoformat(last_login.replace("Z", "+00:00"))
            except:
                last_login = None
        login_time_str = last_login.strftime("%b %d, %I:%M %p") if last_login else "Just now"
    else:
        login_time_str = "Just now"

    role_class = f"role-{user['role'].lower()}" if user["role"] else "role-reviewer"

    with st.sidebar:
        st.markdown("---")

        # Professional user card
        st.markdown(
            f"""
            <div class="user-card">
                <div class="avatar">{initial}</div>
                <div class="info">
                    <div class="name">{user['name']}</div>
                    <div class="role-badge {role_class}">{user['role']}</div>
                    <div class="dept">{user['department']}</div>
                    <div class="email">{user['email']}</div>
                    <div class="login-time">Last Login: {login_time_str}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Logout button
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            AuthService.logout_user()
            st.rerun()
