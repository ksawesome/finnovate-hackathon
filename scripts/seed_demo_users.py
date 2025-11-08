"""
Seed Demo Users for Authentication Testing

Creates sample users with different roles for testing the authentication system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auth import AuthService


def seed_demo_users():
    """Create demo users with different roles."""
    demo_users = [
        {
            "name": "Priya Sharma",
            "email": "priya@adani.com",
            "password": "Demo@123",
            "department": "Finance - Treasury",
            "role": "Reviewer",
        },
        {
            "name": "Rahul Verma",
            "email": "rahul@adani.com",
            "password": "Demo@123",
            "department": "Finance - Consolidation",
            "role": "Approver",
        },
        {
            "name": "Anjali Patel",
            "email": "anjali@adani.com",
            "password": "Demo@123",
            "department": "Finance - Treasury",
            "role": "Manager",
        },
        {
            "name": "Vikram Singh",
            "email": "vikram@adani.com",
            "password": "Demo@123",
            "department": "Finance - Accounting",
            "role": "Admin",
        },
        {
            "name": "Sneha Gupta",
            "email": "sneha@adani.com",
            "password": "Demo@123",
            "department": "Finance - Accounting",
            "role": "Reviewer",
        },
    ]

    auth_service = AuthService()
    created_count = 0

    for user_data in demo_users:
        try:
            result = auth_service.register_user(
                name=user_data["name"],
                email=user_data["email"],
                password=user_data["password"],
                department=user_data["department"],
                role=user_data["role"],
            )

            if result["success"]:
                created_count += 1
                print(
                    f"Created user: {user_data['name']} ({user_data['email']}) - {user_data['role']}"
                )
            else:
                print(f"Skipped {user_data['email']}: {result.get('message', 'Unknown error')}")

        except Exception as e:
            print(f"Error creating {user_data['email']}: {e!s}")

    print(f"\nTotal users created: {created_count}/{len(demo_users)}")
    print("\nDemo credentials:")
    print("=" * 60)
    print("Email: priya@adani.com | Password: Demo@123 | Role: Reviewer")
    print("Email: rahul@adani.com | Password: Demo@123 | Role: Approver")
    print("Email: anjali@adani.com | Password: Demo@123 | Role: Manager")
    print("Email: vikram@adani.com | Password: Demo@123 | Role: Admin")
    print("Email: sneha@adani.com | Password: Demo@123 | Role: Reviewer")
    print("=" * 60)


if __name__ == "__main__":
    print("Seeding demo users...\n")
    seed_demo_users()
