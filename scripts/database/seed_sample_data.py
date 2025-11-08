"""
Seed sample data into PostgreSQL and MongoDB databases.

This script populates the tri-store architecture with test data matching
the Trial Balance structure across all 12 sheets.
"""

import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.db.mongodb import (
    create_review_session,
    init_mongo_collections,
    log_audit_event,
    save_assignment_details,
    save_gl_metadata,
    save_query_template,
    save_user_feedback,
)
from src.db.postgres import (
    create_account_template,
    create_gl_account,
    create_master_account,
    create_responsibility_assignment,
    create_user,
    get_user_by_email,
    init_db,
)

# ============================================================================
# Sample Data Definitions
# ============================================================================

SAMPLE_USERS = [
    {
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@adani.com",
        "department": "Finance",
        "role": "Senior Accountant",
    },
    {
        "name": "Priya Sharma",
        "email": "priya.sharma@adani.com",
        "department": "Treasury",
        "role": "Treasury Manager",
    },
    {
        "name": "Amit Patel",
        "email": "amit.patel@adani.com",
        "department": "Accounts",
        "role": "Accountant",
    },
    {
        "name": "Sneha Reddy",
        "email": "sneha.reddy@adani.com",
        "department": "Finance",
        "role": "Financial Controller",
    },
    {
        "name": "Vikram Singh",
        "email": "vikram.singh@adani.com",
        "department": "Accounts",
        "role": "Senior Accountant",
    },
]

SAMPLE_GL_ACCOUNTS = [
    {
        "account_code": "10010001",
        "account_name": "Cash - Local Bank Account",
        "entity": "AEML",
        "balance": Decimal("15000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("12000000.00"),
        "debit_period": Decimal("50000000.00"),
        "credit_period": Decimal("47000000.00"),
        "bs_pl": "BS",
        "status": "Active",
        "account_category": "Cash and Bank",
        "sub_category": "Current Account",
        "review_flag": "Green",
        "review_checkpoint": "Monthly Reconciliation",
        "criticality": "High",
        "review_frequency": "Monthly",
        "report_type": "Balance Sheet",
        "analysis_required": "Yes",
        "reconciliation_type": "Bank Reconciliation",
        "variance_pct": Decimal("2.5"),
        "department": "Treasury",
    },
    {
        "account_code": "10020002",
        "account_name": "Trade Receivables - Domestic",
        "entity": "AEML",
        "balance": Decimal("85000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("75000000.00"),
        "debit_period": Decimal("120000000.00"),
        "credit_period": Decimal("110000000.00"),
        "bs_pl": "BS",
        "status": "Active",
        "account_category": "Trade Receivables",
        "sub_category": "Domestic Customers",
        "review_flag": "Amber",
        "review_checkpoint": "Aging Analysis Required",
        "criticality": "High",
        "review_frequency": "Monthly",
        "report_type": "Balance Sheet",
        "analysis_required": "Yes",
        "reconciliation_type": "Sub-ledger Reconciliation",
        "variance_pct": Decimal("5.2"),
        "department": "Accounts",
    },
    {
        "account_code": "20030001",
        "account_name": "Trade Payables - Vendors",
        "entity": "AEML",
        "balance": Decimal("-45000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("-40000000.00"),
        "debit_period": Decimal("95000000.00"),
        "credit_period": Decimal("100000000.00"),
        "bs_pl": "BS",
        "status": "Active",
        "account_category": "Trade Payables",
        "sub_category": "Domestic Vendors",
        "review_flag": "Green",
        "review_checkpoint": "Vendor Statement Matching",
        "criticality": "Medium",
        "review_frequency": "Monthly",
        "report_type": "Balance Sheet",
        "analysis_required": "Yes",
        "reconciliation_type": "Vendor Reconciliation",
        "variance_pct": Decimal("3.8"),
        "department": "Accounts",
    },
    {
        "account_code": "40010001",
        "account_name": "Revenue - Sale of Goods",
        "entity": "AEML",
        "balance": Decimal("250000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("5000000.00"),
        "credit_period": Decimal("255000000.00"),
        "bs_pl": "PL",
        "status": "Active",
        "account_category": "Revenue",
        "sub_category": "Operating Revenue",
        "review_flag": "Green",
        "review_checkpoint": "Revenue Recognition Review",
        "criticality": "High",
        "review_frequency": "Monthly",
        "report_type": "P&L",
        "analysis_required": "Yes",
        "reconciliation_type": "Revenue Reconciliation",
        "variance_pct": Decimal("8.5"),
        "department": "Finance",
    },
    {
        "account_code": "50020001",
        "account_name": "Employee Costs - Salaries",
        "entity": "AEML",
        "balance": Decimal("-35000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("35000000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "PL",
        "status": "Active",
        "account_category": "Operating Expenses",
        "sub_category": "Employee Costs",
        "review_flag": "Green",
        "review_checkpoint": "Payroll Reconciliation",
        "criticality": "Medium",
        "review_frequency": "Monthly",
        "report_type": "P&L",
        "analysis_required": "No",
        "reconciliation_type": "Payroll Reconciliation",
        "variance_pct": Decimal("1.2"),
        "department": "Finance",
    },
]

SAMPLE_MASTER_ACCOUNTS = [
    {
        "account_code": "10010001",
        "account_description": "Cash - Local Bank Account",
        "group_gl_account": "100100",
        "schedule_number": "SCH-01",
        "tb_5500": Decimal("15000000.00"),
        "reclassification_mar_18": Decimal("0.00"),
        "derived_tb_5500": Decimal("15000000.00"),
    },
    {
        "account_code": "10020002",
        "account_description": "Trade Receivables - Domestic",
        "group_gl_account": "100200",
        "schedule_number": "SCH-02",
        "tb_5500": Decimal("85000000.00"),
        "reclassification_mar_18": Decimal("-2000000.00"),
        "derived_tb_5500": Decimal("83000000.00"),
    },
]

SAMPLE_QUERY_TEMPLATES = [
    {
        "query_type": "Balance Confirmation",
        "account_code": "10010001",
        "account_name": "Cash - Local Bank Account",
        "nature": "BS - Current Assets - Cash and Bank",
        "query_text": "Please provide bank statements and reconciliation for all bank accounts as of period end.",
        "standard_response": "Bank statements attached. Reconciliation completed with minor timing differences.",
        "required_fields": ["bank_statement", "reconciliation_workpaper", "outstanding_items_list"],
        "validation_rules": ["bank_balance_matches_gl", "all_reconciling_items_explained"],
        "department": "Treasury",
    },
    {
        "query_type": "Aging Analysis",
        "account_code": "10020002",
        "account_name": "Trade Receivables - Domestic",
        "nature": "BS - Current Assets - Trade Receivables",
        "query_text": "Provide detailed aging analysis with customer-wise breakup and provision calculation.",
        "standard_response": "Aging analysis attached. ECL provision calculated as per Ind AS 109.",
        "required_fields": ["aging_report", "provision_calculation", "doubtful_debts_list"],
        "validation_rules": ["aging_total_matches_gl", "provision_adequacy_check"],
        "department": "Accounts",
    },
]

OBSERVATION_DATA = [
    {
        "gl_code": "10020002",
        "observation_type": "query",
        "feedback_text": "Customer XYZ Ltd has outstanding balance of 5Cr for >180 days. Need to verify status.",
        "submitted_by": "rajesh.kumar@adani.com",
        "priority": "high",
        "category": "collection_risk",
    },
    {
        "gl_code": None,
        "observation_type": "suggestion",
        "feedback_text": "Recommend automating bank reconciliation process to reduce manual effort.",
        "submitted_by": "priya.sharma@adani.com",
        "priority": "medium",
        "category": "process_improvement",
    },
]


# ============================================================================
# Seeding Functions
# ============================================================================


def seed_users():
    """Seed sample users."""
    print("\n📊 Seeding users...")
    created_users = []

    for user_data in SAMPLE_USERS:
        try:
            # Check if user exists
            existing = get_user_by_email(user_data["email"])
            if existing:
                print(f"   ⏭️  User already exists: {user_data['email']}")
                created_users.append(existing)
            else:
                user = create_user(**user_data)
                print(f"   ✅ Created user: {user.name} ({user.email})")
                created_users.append(user)
        except Exception as e:
            print(f"   ❌ Error creating user {user_data['email']}: {e}")

    return created_users


def seed_gl_accounts(users):
    """Seed sample GL accounts."""
    print("\n📊 Seeding GL accounts...")
    created_accounts = []

    for i, gl_data in enumerate(SAMPLE_GL_ACCOUNTS):
        try:
            # Assign to user in round-robin fashion
            assigned_user = users[i % len(users)]
            gl_data["assigned_user_id"] = assigned_user.id

            gl_account = create_gl_account(**gl_data)
            print(f"   ✅ Created GL: {gl_account.account_code} - {gl_account.account_name}")
            created_accounts.append(gl_account)

            # Log audit event
            log_audit_event(
                gl_code=gl_account.account_code,
                action="account_created",
                actor={"id": assigned_user.id, "email": assigned_user.email},
                details={"balance": float(gl_account.balance), "period": gl_account.period},
            )

            # Create GL metadata in MongoDB
            save_gl_metadata(
                gl_code=gl_account.account_code,
                company_code=gl_account.company_code,
                period=gl_account.period,
                metadata={
                    "description_long": f"Detailed description for {gl_account.account_name}",
                    "account_category": gl_account.account_category,
                    "sub_category": gl_account.sub_category,
                    "criticality": gl_account.criticality,
                    "review_notes": [],
                    "historical_issues": [],
                    "reconciliation_details": {},
                    "supporting_schedule_refs": [f"SCH-{i+1:02d}"],
                    "tags": ["sample", "mar-24", gl_account.department.lower()],
                },
            )

        except Exception as e:
            print(f"   ❌ Error creating GL account {gl_data['account_code']}: {e}")

    return created_accounts


def seed_responsibility_assignments(gl_accounts, users):
    """Seed responsibility matrix assignments."""
    print("\n📊 Seeding responsibility assignments...")

    for i, gl_account in enumerate(gl_accounts):
        try:
            assigned_user = users[i % len(users)]

            # Create basic assignment
            assignment = create_responsibility_assignment(
                gl_code=gl_account.account_code,
                company_code=gl_account.company_code,
                assigned_user_id=assigned_user.id,
                assignment_id=f"ASSGN-{gl_account.period}-{gl_account.account_code}",
                person_name=assigned_user.name,
                prepare_status="Completed",
                review_status="In Progress",
                final_status="Pending",
                form_filled="Yes",
                approved="No",
                severity="Medium" if gl_account.criticality == "Medium" else "High",
                amount_lc=gl_account.balance,
                query_type="Balance Confirmation",
                working_needed="Yes" if gl_account.analysis_required == "Yes" else "No",
                assignment_date=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            )

            print(f"   ✅ Created assignment: {assignment.assignment_id} for {assigned_user.name}")

            # Add detailed metadata in MongoDB
            save_assignment_details(
                assignment_id=assignment.assignment_id,
                gl_code=gl_account.account_code,
                company_code=gl_account.company_code,
                details={
                    "person_name": assigned_user.name,
                    "assigned_user_email": assigned_user.email,
                    "severity": assignment.severity,
                    "query_type": assignment.query_type,
                    "working_needed": assignment.working_needed,
                    "preparer_comment": f"Initial review completed for {gl_account.account_name}",
                    "reviewer_comment": "Pending final review",
                    "communication_log": [
                        {
                            "message": "Assignment created",
                            "from_user": "system",
                            "to_user": assigned_user.email,
                            "timestamp": datetime.utcnow() - timedelta(days=5),
                        }
                    ],
                    "status_history": [
                        {
                            "status": "assigned",
                            "timestamp": datetime.utcnow() - timedelta(days=5),
                            "changed_by": "system",
                        },
                        {
                            "status": "in_progress",
                            "timestamp": datetime.utcnow() - timedelta(days=3),
                            "changed_by": assigned_user.email,
                        },
                    ],
                    "attachments": [],
                    "escalations": [],
                },
            )

        except Exception as e:
            print(f"   ❌ Error creating assignment for {gl_account.account_code}: {e}")


def seed_master_accounts():
    """Seed master chart of accounts."""
    print("\n📊 Seeding master chart of accounts...")

    for master_data in SAMPLE_MASTER_ACCOUNTS:
        try:
            master = create_master_account(**master_data)
            print(f"   ✅ Created master account: {master.account_code}")
        except Exception as e:
            print(f"   ❌ Error creating master account {master_data['account_code']}: {e}")


def seed_query_templates():
    """Seed query library templates."""
    print("\n📊 Seeding query templates...")

    for template in SAMPLE_QUERY_TEMPLATES:
        try:
            result = save_query_template(
                query_type=template["query_type"],
                account_code=template["account_code"],
                template_data=template,
            )
            print(
                f"   ✅ Created query template: {template['query_type']} for {template['account_code']}"
            )
        except Exception as e:
            print(f"   ❌ Error creating query template: {e}")


def seed_review_session():
    """Seed a sample review session."""
    print("\n📊 Seeding review session...")

    try:
        session_id = "SESSION-MAR24-001"
        result = create_review_session(
            session_id=session_id,
            period="Mar-24",
            created_by="sneha.reddy@adani.com",
            session_data={
                "start_date": datetime.utcnow() - timedelta(days=10),
                "target_completion_date": datetime.utcnow() + timedelta(days=5),
                "status": "in_progress",
                "accounts_in_scope": [acc["account_code"] for acc in SAMPLE_GL_ACCOUNTS],
                "checkpoints": [
                    {
                        "name": "Data Collection",
                        "completed_at": datetime.utcnow() - timedelta(days=8),
                    },
                    {
                        "name": "Initial Review",
                        "completed_at": datetime.utcnow() - timedelta(days=5),
                    },
                ],
                "milestones": [
                    {"name": "All assignments created", "target": "Day 2", "status": "completed"},
                    {"name": "50% accounts reviewed", "target": "Day 7", "status": "in_progress"},
                    {"name": "Final approval", "target": "Day 15", "status": "pending"},
                ],
                "overall_progress": 45,
                "blockers": [
                    {
                        "issue": "Pending bank statements",
                        "account": "10010001",
                        "raised_on": datetime.utcnow() - timedelta(days=2),
                    }
                ],
            },
        )
        print(f"   ✅ Created review session: {session_id}")
    except Exception as e:
        print(f"   ❌ Error creating review session: {e}")


def seed_user_feedback():
    """Seed user feedback and observations."""
    print("\n📊 Seeding user feedback...")

    for feedback in OBSERVATION_DATA:
        try:
            result = save_user_feedback(
                gl_code=feedback["gl_code"],
                observation_type=feedback["observation_type"],
                feedback_text=feedback["feedback_text"],
                submitted_by=feedback["submitted_by"],
                additional_data={
                    "priority": feedback["priority"],
                    "category": feedback["category"],
                    "tags": ["mar-24", feedback["observation_type"]],
                },
            )
            print(f"   ✅ Created feedback: {feedback['observation_type']}")
        except Exception as e:
            print(f"   ❌ Error creating feedback: {e}")


def seed_account_templates():
    """Seed account master templates."""
    print("\n📊 Seeding account templates...")

    templates = [
        {
            "account_code": "10010001",
            "account_description": "Cash - Local Bank Account",
            "nature": "BS - Current Assets - Cash and Bank",
            "standard_query_type": "Balance Confirmation",
            "department": "Treasury",
            "is_active": True,
        },
        {
            "account_code": "10020002",
            "account_description": "Trade Receivables - Domestic",
            "nature": "BS - Current Assets - Trade Receivables",
            "standard_query_type": "Aging Analysis",
            "department": "Accounts",
            "is_active": True,
        },
    ]

    for template_data in templates:
        try:
            template = create_account_template(**template_data)
            print(f"   ✅ Created account template: {template.account_code}")
        except Exception as e:
            print(f"   ❌ Error creating account template: {e}")


# ============================================================================
# Main Execution
# ============================================================================


def main():
    """Main seeding function."""
    print("\n" + "=" * 70)
    print("🌱 Project Aura - Sample Data Seeding Script")
    print("=" * 70)

    try:
        # Initialize databases
        print("\n🔧 Initializing databases...")
        init_db()
        init_mongo_collections()

        # Seed data in order (maintaining referential integrity)
        users = seed_users()
        gl_accounts = seed_gl_accounts(users)
        seed_responsibility_assignments(gl_accounts, users)
        seed_master_accounts()
        seed_account_templates()
        seed_query_templates()
        seed_review_session()
        seed_user_feedback()

        print("\n" + "=" * 70)
        print("✅ Sample data seeding completed successfully!")
        print("=" * 70)
        print("\n📈 Summary:")
        print(f"   - {len(SAMPLE_USERS)} users created")
        print(f"   - {len(SAMPLE_GL_ACCOUNTS)} GL accounts created")
        print(f"   - {len(SAMPLE_GL_ACCOUNTS)} responsibility assignments created")
        print(f"   - {len(SAMPLE_MASTER_ACCOUNTS)} master accounts created")
        print(f"   - {len(SAMPLE_QUERY_TEMPLATES)} query templates created")
        print("   - 1 review session created")
        print(f"   - {len(OBSERVATION_DATA)} feedback items created")
        print("\n🎯 Ready for testing the data ingestion pipeline!\n")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
