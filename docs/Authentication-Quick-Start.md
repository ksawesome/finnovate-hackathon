# Quick Start Guide - Authentication System

## 🚀 Getting Started

### 1. Run the Application
```powershell
streamlit run src/app.py
```

### 2. Demo Credentials

Use any of these accounts to login:

**Reviewer Account:**
- Email: `priya@adani.com`
- Password: `Demo@123`

**Approver Account:**
- Email: `rahul@adani.com`
- Password: `Demo@123`

**Manager Account:**
- Email: `anjali@adani.com`
- Password: `Demo@123`

**Admin Account:**
- Email: `vikram@adani.com`
- Password: `Demo@123`

## 📋 Features Available

### Login Page
- **Login Tab**: Sign in with existing account
- **Sign Up Tab**: Create new account
- **Forgot Password Tab**: Reset password using token

### After Login
- **User Menu**: Sidebar shows your profile (name, email, role, department)
- **Logout Button**: Click to sign out
- **Dashboard Access**: Full access to all Project Aura features

## 🔐 Password Requirements

When creating a new account or resetting password:
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*(),.?":{}|<>)

## 👥 Creating Demo Users

If you need to recreate demo users:

```powershell
python scripts/seed_demo_users.py
```

## 🛠️ For Developers

### Initialize Database with Auth Columns
```python
from src.auth import add_auth_columns_to_user
add_auth_columns_to_user()
```

### Check Authentication Status
```python
from src.auth import AuthService

if AuthService.is_authenticated():
    user = AuthService.get_current_user()
    print(f"Logged in as: {user['name']}")
```

### Programmatic Login
```python
from src.auth import AuthService

result = AuthService.login_user("email@example.com", "password")
if result["success"]:
    print(f"Welcome {result['user']['name']}")
else:
    print(f"Error: {result['message']}")
```

### Register New User
```python
from src.auth import AuthService

result = AuthService.register_user(
    name="John Doe",
    email="john@example.com",
    password="SecurePass@123",
    department="Finance - Treasury",
    role="Reviewer"
)

if result["success"]:
    print("Account created successfully!")
```

## 🎭 User Roles

- **Reviewer**: Review and validate GL accounts
- **Approver**: Approve reviewed accounts
- **Manager**: Manage teams and reports
- **Admin**: Full system access

## 🐛 Troubleshooting

### Can't Login?
1. Check credentials (email/password are case-sensitive)
2. Ensure account is active
3. Try password reset if you forgot password

### Database Connection Error?
1. Check PostgreSQL is running
2. Verify environment variables in `.env`
3. Run database initialization script

### Auth Columns Missing?
Run this once:
```python
from src.auth import add_auth_columns_to_user
add_auth_columns_to_user()
```

## 📞 Support

For issues or questions:
1. Check `docs/Authentication-System-Complete.md` for detailed documentation
2. Review error messages in Streamlit app
3. Check PostgreSQL logs for database issues

---

**Quick Tip**: Use `priya@adani.com` / `Demo@123` for fastest testing!
