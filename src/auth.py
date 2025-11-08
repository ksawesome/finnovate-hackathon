"""
Authentication Module for Project Aura

Handles user registration, login, password reset, and session management.
Uses bcrypt for password hashing and Streamlit session state for authentication.

Author: Project Aura Team
Date: November 2024
"""

import re
import secrets
from datetime import datetime, timedelta
from typing import Any

import bcrypt
import streamlit as st
from sqlalchemy.exc import IntegrityError

from .db import get_postgres_session
from .db.postgres import User


# Extend User model with authentication fields (if not already present)
def add_auth_columns_to_user():
    """Add authentication columns to User model if they don't exist."""
    from sqlalchemy import inspect, text

    session = get_postgres_session()
    try:
        inspector = inspect(session.bind)
        columns = [col["name"] for col in inspector.get_columns("users")]

        # Add password_hash column if not exists
        if "password_hash" not in columns:
            session.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
            session.commit()

        # Add is_active column if not exists
        if "is_active" not in columns:
            session.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
            session.commit()

        # Add last_login column if not exists
        if "last_login" not in columns:
            session.execute(text("ALTER TABLE users ADD COLUMN last_login TIMESTAMP"))
            session.commit()

        # Add reset_token column if not exists
        if "reset_token" not in columns:
            session.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(255)"))
            session.commit()

        # Add reset_token_expiry column if not exists
        if "reset_token_expiry" not in columns:
            session.execute(text("ALTER TABLE users ADD COLUMN reset_token_expiry TIMESTAMP"))
            session.commit()

    except Exception as e:
        session.rollback()
        print(f"Note: Authentication columns may already exist: {e}")
    finally:
        session.close()


class AuthService:
    """Service for user authentication and authorization."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception:
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength.

        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"

        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"

        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"

        return True, "Password is strong"

    @staticmethod
    def register_user(
        name: str, email: str, password: str, department: str | None = None, role: str = "Reviewer"
    ) -> dict[str, Any]:
        """
        Register a new user.

        Args:
            name: User's full name
            email: User's email address
            password: User's password
            department: User's department
            role: User's role (default: Reviewer)

        Returns:
            Dict with success status and message
        """
        # Validate email
        if not AuthService.validate_email(email):
            return {"success": False, "message": "Invalid email format"}

        # Validate password
        is_valid, message = AuthService.validate_password(password)
        if not is_valid:
            return {"success": False, "message": message}

        # Hash password
        password_hash = AuthService.hash_password(password)

        session = get_postgres_session()
        try:
            # Check if email already exists
            existing_user = session.query(User).filter_by(email=email).first()
            if existing_user:
                return {"success": False, "message": "Email already registered"}

            # Create user using raw SQL to include password_hash
            from sqlalchemy import text

            query = text(
                """
                INSERT INTO users (name, email, password_hash, department, role, is_active, created_at, updated_at)
                VALUES (:name, :email, :password_hash, :department, :role, TRUE, NOW(), NOW())
                RETURNING id
            """
            )

            result = session.execute(
                query,
                {
                    "name": name,
                    "email": email,
                    "password_hash": password_hash,
                    "department": department,
                    "role": role,
                },
            )
            session.commit()

            user_id = result.scalar()

            return {"success": True, "message": f"Registration successful! User ID: {user_id}"}

        except IntegrityError:
            session.rollback()
            return {"success": False, "message": "Email already registered"}
        except Exception as e:
            session.rollback()
            return False, f"Registration failed: {e!s}"
        finally:
            session.close()

    @staticmethod
    def login_user(email: str, password: str) -> dict[str, Any]:
        """
        Authenticate user login.

        Args:
            email: User's email
            password: User's password

        Returns:
            Dict with success status, user data, and message
        """
        if not email or not password:
            return {"success": False, "user": None, "message": "Email and password are required"}

        session = get_postgres_session()
        try:
            # Get user with password hash using raw SQL
            from sqlalchemy import text

            query = text(
                """
                SELECT id, name, email, department, role, password_hash, is_active, last_login
                FROM users
                WHERE email = :email
            """
            )

            result = session.execute(query, {"email": email}).fetchone()

            if not result:
                return {"success": False, "user": None, "message": "Invalid email or password"}

            user_id, name, user_email, department, role, password_hash, is_active, last_login = (
                result
            )

            # Check if account is active
            if not is_active:
                return {
                    "success": False,
                    "user": None,
                    "message": "Account is inactive. Please contact administrator.",
                }

            # Verify password
            if not password_hash or not AuthService.verify_password(password, password_hash):
                return {"success": False, "user": None, "message": "Invalid email or password"}

            # Update last login
            update_query = text(
                """
                UPDATE users
                SET last_login = NOW()
                WHERE id = :user_id
            """
            )
            session.execute(update_query, {"user_id": user_id})
            session.commit()

            # Return user data
            user_data = {
                "id": user_id,
                "name": name,
                "email": user_email,
                "department": department,
                "role": role,
                "last_login": last_login,
            }

            return {"success": True, "user": user_data, "message": "Login successful"}

        except Exception as e:
            session.rollback()
            return {"success": False, "user": None, "message": f"Login failed: {e!s}"}
        finally:
            session.close()

    @staticmethod
    def generate_reset_token(email: str) -> tuple[bool, str | None, str]:
        """
        Generate password reset token for user.

        Args:
            email: User's email

        Returns:
            Tuple of (success: bool, token: str, message: str)
        """
        session = get_postgres_session()
        try:
            from sqlalchemy import text

            # Check if user exists
            query = text("SELECT id FROM users WHERE email = :email")
            result = session.execute(query, {"email": email}).fetchone()

            if not result:
                # Don't reveal if email exists for security
                return True, None, "If email exists, reset link will be sent"

            user_id = result[0]

            # Generate token
            token = secrets.token_urlsafe(32)
            expiry = datetime.utcnow() + timedelta(hours=1)

            # Store token
            update_query = text(
                """
                UPDATE users
                SET reset_token = :token, reset_token_expiry = :expiry
                WHERE id = :user_id
            """
            )
            session.execute(update_query, {"token": token, "expiry": expiry, "user_id": user_id})
            session.commit()

            return True, token, "Password reset token generated"

        except Exception as e:
            session.rollback()
            return False, None, f"Token generation failed: {e!s}"
        finally:
            session.close()

    @staticmethod
    def reset_password(token: str, new_password: str) -> tuple[bool, str]:
        """
        Reset user password using token.

        Args:
            token: Reset token
            new_password: New password

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validate password
        is_valid, message = AuthService.validate_password(new_password)
        if not is_valid:
            return False, message

        session = get_postgres_session()
        try:
            from sqlalchemy import text

            # Find user with valid token
            query = text(
                """
                SELECT id, reset_token_expiry
                FROM users
                WHERE reset_token = :token
            """
            )
            result = session.execute(query, {"token": token}).fetchone()

            if not result:
                return False, "Invalid or expired reset token"

            user_id, expiry = result

            # Check if token is expired
            if not expiry or datetime.utcnow() > expiry:
                return False, "Reset token has expired"

            # Hash new password
            password_hash = AuthService.hash_password(new_password)

            # Update password and clear token
            update_query = text(
                """
                UPDATE users
                SET password_hash = :password_hash,
                    reset_token = NULL,
                    reset_token_expiry = NULL,
                    updated_at = NOW()
                WHERE id = :user_id
            """
            )
            session.execute(update_query, {"password_hash": password_hash, "user_id": user_id})
            session.commit()

            return True, "Password reset successful"

        except Exception as e:
            session.rollback()
            return False, f"Password reset failed: {e!s}"
        finally:
            session.close()

    @staticmethod
    def logout_user():
        """Clear user session."""
        for key in [
            "authenticated",
            "user_id",
            "user_name",
            "user_email",
            "user_role",
            "user_department",
        ]:
            if key in st.session_state:
                del st.session_state[key]

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated."""
        return st.session_state.get("authenticated", False)

    @staticmethod
    def get_current_user() -> dict | None:
        """Get current logged-in user data."""
        if not AuthService.is_authenticated():
            return None

        return {
            "id": st.session_state.get("user_id"),
            "name": st.session_state.get("user_name"),
            "email": st.session_state.get("user_email"),
            "role": st.session_state.get("user_role"),
            "department": st.session_state.get("user_department"),
        }


# Initialize authentication columns
try:
    add_auth_columns_to_user()
except Exception as e:
    print(f"Warning: Could not initialize auth columns: {e}")
