"""
Seed comprehensive demo data into all 3 databases (PostgreSQL, MongoDB, File System).

Creates realistic, demo-ready data with:
- 30+ GL accounts with varied statuses
- 5 users with different roles
- Audit trail and review sessions
- Supporting documentation metadata
- Realistic balances and review workflows
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
    log_audit_event,
    save_gl_metadata,
    save_user_feedback,
    save_validation_results,
)
from src.db.postgres import (
    create_gl_account,
    create_responsibility_assignment,
    create_user,
    create_version_snapshot,
    get_user_by_email,
    init_db,
)

# ============================================================================
# SAMPLE DATA DEFINITIONS
# ============================================================================

USERS = [
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
        "department": "Operations",
        "role": "Operations Manager",
    },
]

# Realistic GL Accounts covering various categories and statuses
GL_ACCOUNTS = [
    # Cash & Bank Accounts (High criticality, monthly review)
    {
        "account_code": "10010001",
        "account_name": "Cash - Local Bank HDFC",
        "entity": "AEML",
        "balance": Decimal("15500000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("12000000.00"),
        "debit_period": Decimal("50000000.00"),
        "credit_period": Decimal("46500000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Cash and Bank",
        "sub_category": "Current Account",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Treasury",
        "analysis_required": "Yes",
        "reconciliation_type": "Bank Reconciliation",
    },
    {
        "account_code": "10010002",
        "account_name": "Cash - ICICI Bank Current Account",
        "entity": "AEML",
        "balance": Decimal("8200000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("7500000.00"),
        "debit_period": Decimal("25000000.00"),
        "credit_period": Decimal("24300000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Cash and Bank",
        "sub_category": "Current Account",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Treasury",
        "analysis_required": "Yes",
        "reconciliation_type": "Bank Reconciliation",
    },
    {
        "account_code": "10010003",
        "account_name": "Petty Cash",
        "entity": "AEML",
        "balance": Decimal("50000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("45000.00"),
        "debit_period": Decimal("200000.00"),
        "credit_period": Decimal("195000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Cash and Bank",
        "sub_category": "Petty Cash",
        "review_status": "pending",
        "review_flag": "Not Considered",
        "criticality": "Low",
        "review_frequency": "Quarterly",
        "department": "Finance",
        "analysis_required": "No",
        "reconciliation_type": "Non Reconciliation GL",
    },
    # Accounts Receivable (Medium-High criticality)
    {
        "account_code": "12010001",
        "account_name": "Trade Receivables - Domestic",
        "entity": "AEML",
        "balance": Decimal("45000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("42000000.00"),
        "debit_period": Decimal("150000000.00"),
        "credit_period": Decimal("147000000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Current Assets",
        "sub_category": "Trade Receivables",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Reconciliation GL",
    },
    {
        "account_code": "12010002",
        "account_name": "Trade Receivables - Export",
        "entity": "AEML",
        "balance": Decimal("28000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("25000000.00"),
        "debit_period": Decimal("85000000.00"),
        "credit_period": Decimal("82000000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Current Assets",
        "sub_category": "Trade Receivables",
        "review_status": "flagged",
        "review_flag": "Red",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Reconciliation GL",
    },
    {
        "account_code": "12010003",
        "account_name": "Provision for Doubtful Debts",
        "entity": "AEML",
        "balance": Decimal("-2500000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("-2000000.00"),
        "debit_period": Decimal("0.00"),
        "credit_period": Decimal("500000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Current Assets",
        "sub_category": "Provisions",
        "review_status": "pending",
        "review_flag": "Not Considered",
        "criticality": "Medium",
        "review_frequency": "Quarterly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Non Reconciliation GL",
    },
    # Inventory (Medium criticality)
    {
        "account_code": "13010001",
        "account_name": "Raw Materials - Coal",
        "entity": "AEML",
        "balance": Decimal("65000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("60000000.00"),
        "debit_period": Decimal("200000000.00"),
        "credit_period": Decimal("195000000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Current Assets",
        "sub_category": "Inventory",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "Medium",
        "review_frequency": "Monthly",
        "department": "Operations",
        "analysis_required": "Yes",
        "reconciliation_type": "Inventory Reconciliation",
    },
    {
        "account_code": "13010002",
        "account_name": "Work in Progress",
        "entity": "AEML",
        "balance": Decimal("12000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("10000000.00"),
        "debit_period": Decimal("45000000.00"),
        "credit_period": Decimal("43000000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Current Assets",
        "sub_category": "Inventory",
        "review_status": "pending",
        "review_flag": "Not Considered",
        "criticality": "Medium",
        "review_frequency": "Monthly",
        "department": "Operations",
        "analysis_required": "Yes",
        "reconciliation_type": "Inventory Reconciliation",
    },
    # Fixed Assets (High criticality, less frequent review)
    {
        "account_code": "15010001",
        "account_name": "Land and Buildings",
        "entity": "AEML",
        "balance": Decimal("250000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("250000000.00"),
        "debit_period": Decimal("0.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Fixed Assets",
        "sub_category": "Property",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Half Yearly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Fixed Asset Register",
    },
    {
        "account_code": "15010002",
        "account_name": "Plant and Machinery",
        "entity": "AEML",
        "balance": Decimal("450000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("455000000.00"),
        "debit_period": Decimal("5000000.00"),
        "credit_period": Decimal("10000000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Fixed Assets",
        "sub_category": "Plant & Equipment",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Half Yearly",
        "department": "Operations",
        "analysis_required": "Yes",
        "reconciliation_type": "Fixed Asset Register",
    },
    {
        "account_code": "15020001",
        "account_name": "Accumulated Depreciation - Plant",
        "entity": "AEML",
        "balance": Decimal("-85000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("-80000000.00"),
        "debit_period": Decimal("0.00"),
        "credit_period": Decimal("5000000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Fixed Assets",
        "sub_category": "Depreciation",
        "review_status": "pending",
        "review_flag": "Not Considered",
        "criticality": "Medium",
        "review_frequency": "Quarterly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Non Reconciliation GL",
    },
    # Current Liabilities (High criticality)
    {
        "account_code": "20010001",
        "account_name": "Trade Payables - Suppliers",
        "entity": "AEML",
        "balance": Decimal("38000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("35000000.00"),
        "debit_period": Decimal("120000000.00"),
        "credit_period": Decimal("123000000.00"),
        "bs_pl": "BS",
        "status": "Liabilities",
        "account_category": "Current Liabilities",
        "sub_category": "Trade Payables",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Accounts",
        "analysis_required": "Yes",
        "reconciliation_type": "Reconciliation GL",
    },
    {
        "account_code": "20010002",
        "account_name": "Accrued Expenses",
        "entity": "AEML",
        "balance": Decimal("7500000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("6800000.00"),
        "debit_period": Decimal("25000000.00"),
        "credit_period": Decimal("25700000.00"),
        "bs_pl": "BS",
        "status": "Liabilities",
        "account_category": "Current Liabilities",
        "sub_category": "Accruals",
        "review_status": "flagged",
        "review_flag": "Red",
        "criticality": "Medium",
        "review_frequency": "Monthly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Non Reconciliation GL",
    },
    {
        "account_code": "20020001",
        "account_name": "Short Term Loans",
        "entity": "AEML",
        "balance": Decimal("50000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("45000000.00"),
        "debit_period": Decimal("10000000.00"),
        "credit_period": Decimal("15000000.00"),
        "bs_pl": "BS",
        "status": "Liabilities",
        "account_category": "Current Liabilities",
        "sub_category": "Borrowings",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Treasury",
        "analysis_required": "Yes",
        "reconciliation_type": "Loan Reconciliation",
    },
    # Long Term Liabilities
    {
        "account_code": "21010001",
        "account_name": "Long Term Borrowings - Banks",
        "entity": "AEML",
        "balance": Decimal("350000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("360000000.00"),
        "debit_period": Decimal("10000000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "BS",
        "status": "Liabilities",
        "account_category": "Non-Current Liabilities",
        "sub_category": "Term Loans",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Quarterly",
        "department": "Treasury",
        "analysis_required": "Yes",
        "reconciliation_type": "Loan Reconciliation",
    },
    {
        "account_code": "21010002",
        "account_name": "Deferred Tax Liability",
        "entity": "AEML",
        "balance": Decimal("15000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("14500000.00"),
        "debit_period": Decimal("0.00"),
        "credit_period": Decimal("500000.00"),
        "bs_pl": "BS",
        "status": "Liabilities",
        "account_category": "Non-Current Liabilities",
        "sub_category": "Deferred Tax",
        "review_status": "pending",
        "review_flag": "Not Considered",
        "criticality": "Medium",
        "review_frequency": "Half Yearly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Non Reconciliation GL",
    },
    # Equity
    {
        "account_code": "30010001",
        "account_name": "Share Capital",
        "entity": "AEML",
        "balance": Decimal("500000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("500000000.00"),
        "debit_period": Decimal("0.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "BS",
        "status": "Equity",
        "account_category": "Equity",
        "sub_category": "Share Capital",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Half Yearly",
        "department": "Finance",
        "analysis_required": "No",
        "reconciliation_type": "Non Reconciliation GL",
    },
    {
        "account_code": "30020001",
        "account_name": "Retained Earnings",
        "entity": "AEML",
        "balance": Decimal("125000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("110000000.00"),
        "debit_period": Decimal("0.00"),
        "credit_period": Decimal("15000000.00"),
        "bs_pl": "BS",
        "status": "Equity",
        "account_category": "Equity",
        "sub_category": "Reserves",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Quarterly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Non Reconciliation GL",
    },
    # Income (P&L)
    {
        "account_code": "40010001",
        "account_name": "Revenue from Operations",
        "entity": "AEML",
        "balance": Decimal("185000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("5000000.00"),
        "credit_period": Decimal("190000000.00"),
        "bs_pl": "PL",
        "status": "Income",
        "account_category": "Revenue",
        "sub_category": "Operating Revenue",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Revenue Reconciliation",
    },
    {
        "account_code": "40020001",
        "account_name": "Other Income",
        "entity": "AEML",
        "balance": Decimal("3500000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("0.00"),
        "credit_period": Decimal("3500000.00"),
        "bs_pl": "PL",
        "status": "Income",
        "account_category": "Revenue",
        "sub_category": "Other Income",
        "review_status": "pending",
        "review_flag": "Not Considered",
        "criticality": "Low",
        "review_frequency": "Quarterly",
        "department": "Finance",
        "analysis_required": "No",
        "reconciliation_type": "Non Reconciliation GL",
    },
    # Expenses (P&L)
    {
        "account_code": "50010001",
        "account_name": "Cost of Goods Sold",
        "entity": "AEML",
        "balance": Decimal("95000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("95000000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "PL",
        "status": "Expense",
        "account_category": "Direct Expenses",
        "sub_category": "COGS",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Operations",
        "analysis_required": "Yes",
        "reconciliation_type": "Non Reconciliation GL",
    },
    {
        "account_code": "50020001",
        "account_name": "Employee Salaries",
        "entity": "AEML",
        "balance": Decimal("28000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("28000000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "PL",
        "status": "Expense",
        "account_category": "Operating Expenses",
        "sub_category": "Personnel Costs",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Payroll Reconciliation",
    },
    {
        "account_code": "50020002",
        "account_name": "Employee Benefits",
        "entity": "AEML",
        "balance": Decimal("5500000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("5500000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "PL",
        "status": "Expense",
        "account_category": "Operating Expenses",
        "sub_category": "Personnel Costs",
        "review_status": "flagged",
        "review_flag": "Red",
        "criticality": "Medium",
        "review_frequency": "Monthly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Non Reconciliation GL",
    },
    {
        "account_code": "50030001",
        "account_name": "Depreciation Expense",
        "entity": "AEML",
        "balance": Decimal("12000000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("12000000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "PL",
        "status": "Expense",
        "account_category": "Operating Expenses",
        "sub_category": "Depreciation",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "Medium",
        "review_frequency": "Quarterly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Non Reconciliation GL",
    },
    {
        "account_code": "50030002",
        "account_name": "Repairs and Maintenance",
        "entity": "AEML",
        "balance": Decimal("8500000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("8500000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "PL",
        "status": "Expense",
        "account_category": "Operating Expenses",
        "sub_category": "Maintenance",
        "review_status": "pending",
        "review_flag": "Not Considered",
        "criticality": "Low",
        "review_frequency": "Quarterly",
        "department": "Operations",
        "analysis_required": "No",
        "reconciliation_type": "Non Reconciliation GL",
    },
    {
        "account_code": "50040001",
        "account_name": "Interest Expense",
        "entity": "AEML",
        "balance": Decimal("9500000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("9500000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "PL",
        "status": "Expense",
        "account_category": "Finance Costs",
        "sub_category": "Interest",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Treasury",
        "analysis_required": "Yes",
        "reconciliation_type": "Interest Reconciliation",
    },
    {
        "account_code": "50050001",
        "account_name": "Office Expenses",
        "entity": "AEML",
        "balance": Decimal("2800000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("2800000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "PL",
        "status": "Expense",
        "account_category": "Administrative Expenses",
        "sub_category": "Office Costs",
        "review_status": "pending",
        "review_flag": "Not Considered",
        "criticality": "Low",
        "review_frequency": "Quarterly",
        "department": "Finance",
        "analysis_required": "No",
        "reconciliation_type": "Non Reconciliation GL",
    },
    {
        "account_code": "50050002",
        "account_name": "Travel and Conveyance",
        "entity": "AEML",
        "balance": Decimal("1200000.00"),
        "period": "Mar-24",
        "company_code": "5500",
        "balance_carryforward": Decimal("0.00"),
        "debit_period": Decimal("1200000.00"),
        "credit_period": Decimal("0.00"),
        "bs_pl": "PL",
        "status": "Expense",
        "account_category": "Administrative Expenses",
        "sub_category": "Travel",
        "review_status": "pending",
        "review_flag": "Not Considered",
        "criticality": "Low",
        "review_frequency": "Quarterly",
        "department": "Finance",
        "analysis_required": "No",
        "reconciliation_type": "Non Reconciliation GL",
    },
]

# Additional accounts for ABEX entity
ABEX_ACCOUNTS = [
    {
        "account_code": "10010001",
        "account_name": "Cash - Bank Account",
        "entity": "ABEX",
        "balance": Decimal("8500000.00"),
        "period": "2022-06",
        "company_code": "5501",
        "balance_carryforward": Decimal("7000000.00"),
        "debit_period": Decimal("30000000.00"),
        "credit_period": Decimal("28500000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Cash and Bank",
        "sub_category": "Current Account",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Treasury",
        "analysis_required": "Yes",
        "reconciliation_type": "Bank Reconciliation",
    },
    {
        "account_code": "12010001",
        "account_name": "Trade Receivables",
        "entity": "ABEX",
        "balance": Decimal("25000000.00"),
        "period": "2022-06",
        "company_code": "5501",
        "balance_carryforward": Decimal("22000000.00"),
        "debit_period": Decimal("80000000.00"),
        "credit_period": Decimal("77000000.00"),
        "bs_pl": "BS",
        "status": "Assets",
        "account_category": "Current Assets",
        "sub_category": "Trade Receivables",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Finance",
        "analysis_required": "Yes",
        "reconciliation_type": "Reconciliation GL",
    },
    {
        "account_code": "20010001",
        "account_name": "Trade Payables",
        "entity": "ABEX",
        "balance": Decimal("18000000.00"),
        "period": "2022-06",
        "company_code": "5501",
        "balance_carryforward": Decimal("16000000.00"),
        "debit_period": Decimal("50000000.00"),
        "credit_period": Decimal("52000000.00"),
        "bs_pl": "BS",
        "status": "Liabilities",
        "account_category": "Current Liabilities",
        "sub_category": "Trade Payables",
        "review_status": "reviewed",
        "review_flag": "Green",
        "criticality": "High",
        "review_frequency": "Monthly",
        "department": "Accounts",
        "analysis_required": "Yes",
        "reconciliation_type": "Reconciliation GL",
    },
]

# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================


def seed_users():
    """Create sample users."""
    print("\n📥 Seeding Users...")
    created_users = []

    for user_data in USERS:
        try:
            # Check if user exists
            existing_user = get_user_by_email(user_data["email"])
            if existing_user:
                print(f"  ✓ User already exists: {user_data['name']}")
                created_users.append(existing_user)
                continue

            # Create new user
            user = create_user(
                name=user_data["name"],
                email=user_data["email"],
                department=user_data["department"],
                role=user_data["role"],
            )
            created_users.append(user)
            print(f"  ✓ Created user: {user_data['name']}")

            # Log to MongoDB
            log_audit_event(
                entity_type="user",
                entity_id=user.email,
                action="created",
                user_email=user.email,
                changes={"status": "User account created"},
            )
        except Exception as e:
            print(f"  ✗ Error creating user {user_data['name']}: {e}")

    print(f"✅ Created/found {len(created_users)} users")
    return created_users


def seed_gl_accounts(users):
    """Create sample GL accounts."""
    print("\n📥 Seeding GL Accounts...")
    created_accounts = []
    all_accounts = GL_ACCOUNTS + ABEX_ACCOUNTS

    for idx, acc_data in enumerate(all_accounts):
        try:
            # Create GL account
            account = create_gl_account(**acc_data)
            created_accounts.append(account)
            print(
                f"  ✓ Created account: {acc_data['account_code']} - {acc_data['account_name'][:40]}"
            )

            # Assign to user (round-robin)
            user = users[idx % len(users)]
            try:
                create_responsibility_assignment(
                    account_code=acc_data["account_code"],
                    company_code=acc_data["company_code"],
                    period=acc_data["period"],
                    assigned_user_id=user.id,
                    department=acc_data["department"],
                    assignment_date=datetime.utcnow(),
                    priority="High" if acc_data["criticality"] == "High" else "Medium",
                    notes=f"Assigned to {user.name} for {acc_data['period']} review",
                )
            except Exception as e:
                # Assignment might already exist
                pass

            # Add metadata to MongoDB
            save_gl_metadata(
                gl_code=acc_data["account_code"],
                company_code=acc_data["company_code"],
                period=acc_data["period"],
                metadata={
                    "description_long": f"Extended information for {acc_data['account_name']}",
                    "account_category": acc_data["account_category"],
                    "sub_category": acc_data["sub_category"],
                    "criticality": acc_data["criticality"],
                    "review_notes": [
                        f"Reviewed by {user.name}",
                        f"Status: {acc_data['review_status']}",
                    ],
                    "historical_issues": [],
                    "reconciliation_details": {
                        "type": acc_data["reconciliation_type"],
                        "frequency": acc_data["review_frequency"],
                    },
                    "supporting_schedule_refs": [],
                    "tags": [acc_data["department"], acc_data["bs_pl"], acc_data["status"]],
                },
            )

            # Log creation
            log_audit_event(
                entity_type="gl_account",
                entity_id=acc_data["account_code"],
                action="created",
                user_email=user.email,
                changes={
                    "balance": float(acc_data["balance"]),
                    "status": acc_data["review_status"],
                    "period": acc_data["period"],
                },
            )

            # For reviewed accounts, create version snapshot
            if acc_data["review_status"] in ["reviewed", "flagged"]:
                try:
                    create_version_snapshot(
                        account_id=account.id,
                        snapshot_data={
                            "balance": float(acc_data["balance"]),
                            "review_status": acc_data["review_status"],
                            "review_flag": acc_data["review_flag"],
                            "reviewed_by": user.email,
                            "reviewed_at": datetime.utcnow().isoformat(),
                        },
                        created_by=user.email,
                        change_reason=f"Review completed for {acc_data['period']}",
                    )

                    # Log review action
                    log_audit_event(
                        entity_type="gl_account",
                        entity_id=acc_data["account_code"],
                        action="reviewed",
                        user_email=user.email,
                        changes={
                            "review_status": acc_data["review_status"],
                            "review_flag": acc_data["review_flag"],
                        },
                    )
                except Exception as e:
                    pass

        except Exception as e:
            # Account might already exist (duplicate key)
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print(f"  ℹ Account already exists: {acc_data['account_code']}")
            else:
                print(f"  ✗ Error creating account {acc_data['account_code']}: {e}")

    print(f"✅ Created/found {len(created_accounts)} GL accounts")
    return created_accounts


def seed_review_sessions():
    """Create review sessions in MongoDB."""
    print("\n📥 Seeding Review Sessions...")

    sessions_created = 0
    for i in range(3):
        try:
            session_id = f"RS-MAR24-{i+1:03d}"
            create_review_session(
                session_id=session_id,
                period="Mar-24",
                created_by=USERS[i % len(USERS)]["email"],
                session_data={
                    "start_date": datetime.utcnow() - timedelta(days=random.randint(5, 15)),
                    "target_completion_date": datetime.utcnow()
                    + timedelta(days=random.randint(10, 20)),
                    "status": random.choice(["in_progress", "completed", "not_started"]),
                    "accounts_in_scope": random.randint(5, 15),
                    "checkpoints": ["Initial review", "Reconciliation", "Final approval"],
                    "milestones": ["Q4 close", "Year-end audit prep"],
                    "overall_progress": random.randint(40, 95),
                    "blockers": [],
                },
            )
            sessions_created += 1
            print(f"  ✓ Created review session: {session_id}")
        except Exception as e:
            print(f"  ✗ Error creating session: {e}")

    print(f"✅ Created {sessions_created} review sessions")


def seed_user_feedback():
    """Create sample user feedback."""
    print("\n📥 Seeding User Feedback...")

    feedback_items = [
        {
            "gl_code": "12010002",
            "observation_type": "query",
            "feedback_text": "Need clarification on export receivables aging - some invoices > 90 days",
            "submitted_by": USERS[0]["email"],
            "additional_data": {
                "priority": "high",
                "category": "aging_analysis",
                "tags": ["receivables", "export"],
            },
        },
        {
            "gl_code": "20010002",
            "observation_type": "observation",
            "feedback_text": "Accrued expenses seem high compared to last month - please verify",
            "submitted_by": USERS[1]["email"],
            "additional_data": {
                "priority": "medium",
                "category": "variance",
                "tags": ["accruals", "monthly_review"],
            },
        },
        {
            "gl_code": None,
            "observation_type": "suggestion",
            "feedback_text": "Dashboard is excellent! Would be great to add YoY comparison charts.",
            "submitted_by": USERS[2]["email"],
            "additional_data": {
                "priority": "low",
                "category": "enhancement",
                "tags": ["ui", "charts"],
            },
        },
        {
            "gl_code": "50020002",
            "observation_type": "reclassification",
            "feedback_text": "Some employee benefits should be reclassified to different cost centers",
            "submitted_by": USERS[3]["email"],
            "additional_data": {
                "priority": "high",
                "category": "reclassification",
                "tags": ["payroll", "cost_allocation"],
            },
        },
    ]

    feedback_created = 0
    for feedback in feedback_items:
        try:
            save_user_feedback(**feedback)
            feedback_created += 1
            print(f"  ✓ Saved feedback from {feedback['submitted_by']}")
        except Exception as e:
            print(f"  ✗ Error saving feedback: {e}")

    print(f"✅ Created {feedback_created} feedback items")


def seed_validation_results():
    """Create sample validation results."""
    print("\n📥 Seeding Validation Results...")

    validations_created = 0
    for account in GL_ACCOUNTS[:10]:  # First 10 accounts
        try:
            passed = account["review_flag"] == "Green"
            checks_passed = random.randint(10, 12) if passed else random.randint(6, 9)

            save_validation_results(
                gl_code=account["account_code"],
                period=account["period"],
                validation_suite="great_expectations_trial_balance",
                results={
                    "validation_date": datetime.utcnow().isoformat(),
                    "checks_passed": checks_passed,
                    "checks_total": 12,
                    "issues_found": 0 if passed else random.randint(1, 3),
                    "status": "passed" if passed else "warning",
                    "details": {
                        "balance_check": "passed",
                        "debit_credit_balance": "passed",
                        "reconciliation_check": (
                            "passed"
                            if account["reconciliation_type"] != "Non Reconciliation GL"
                            else "not_applicable"
                        ),
                        "sla_check": (
                            "passed" if account["review_status"] == "reviewed" else "pending"
                        ),
                        "variance_threshold": "passed" if passed else "warning",
                        "nil_balance_check": "passed",
                        "duplicate_check": "passed",
                        "data_completeness": "passed",
                    },
                    "expectations": {
                        "expect_column_values_to_not_be_null": {"passed": True},
                        "expect_column_values_to_be_in_set": {"passed": True},
                        "expect_table_row_count_to_be_between": {"passed": True},
                    },
                },
                passed=passed,
            )
            validations_created += 1
            print(f"  ✓ Saved validation for {account['account_code']}")
        except Exception as e:
            print(f"  ✗ Error saving validation: {e}")

    print(f"✅ Created {validations_created} validation results")


def print_summary():
    """Print seeding summary."""
    print("\n" + "=" * 60)
    print("🎉 DEMO DATA SEEDING COMPLETE!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"  • Users: {len(USERS)}")
    print(f"  • GL Accounts (AEML): {len(GL_ACCOUNTS)}")
    print(f"  • GL Accounts (ABEX): {len(ABEX_ACCOUNTS)}")
    print(f"  • Total Accounts: {len(GL_ACCOUNTS) + len(ABEX_ACCOUNTS)}")
    print(f"\n✅ Status Distribution:")
    reviewed = sum(1 for acc in GL_ACCOUNTS + ABEX_ACCOUNTS if acc["review_status"] == "reviewed")
    pending = sum(1 for acc in GL_ACCOUNTS + ABEX_ACCOUNTS if acc["review_status"] == "pending")
    flagged = sum(1 for acc in GL_ACCOUNTS + ABEX_ACCOUNTS if acc["review_status"] == "flagged")
    print(f"  • Reviewed: {reviewed} ({reviewed/(len(GL_ACCOUNTS)+len(ABEX_ACCOUNTS))*100:.1f}%)")
    print(f"  • Pending: {pending} ({pending/(len(GL_ACCOUNTS)+len(ABEX_ACCOUNTS))*100:.1f}%)")
    print(f"  • Flagged: {flagged} ({flagged/(len(GL_ACCOUNTS)+len(ABEX_ACCOUNTS))*100:.1f}%)")
    print(f"\n💰 Financial Summary (AEML - Mar-24):")
    total_assets = sum(acc["balance"] for acc in GL_ACCOUNTS if acc["status"] == "Assets")
    total_liabilities = sum(acc["balance"] for acc in GL_ACCOUNTS if acc["status"] == "Liabilities")
    total_equity = sum(acc["balance"] for acc in GL_ACCOUNTS if acc["status"] == "Equity")
    total_income = sum(acc["balance"] for acc in GL_ACCOUNTS if acc["status"] == "Income")
    total_expense = sum(acc["balance"] for acc in GL_ACCOUNTS if acc["status"] == "Expense")
    print(f"  • Total Assets: ₹{total_assets:,.2f}")
    print(f"  • Total Liabilities: ₹{total_liabilities:,.2f}")
    print(f"  • Total Equity: ₹{total_equity:,.2f}")
    print(f"  • Total Income: ₹{total_income:,.2f}")
    print(f"  • Total Expense: ₹{total_expense:,.2f}")
    print(f"  • Net Profit: ₹{total_income - total_expense:,.2f}")
    print("\n🚀 Ready to demo!")
    print("   Run: streamlit run src/app.py")
    print("=" * 60 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main seeding function."""
    print("\n" + "=" * 60)
    print("🌱 SEEDING DEMO DATA FOR PROJECT AURA")
    print("=" * 60)

    # Initialize databases
    print("\n🔧 Initializing databases...")
    init_db()
    print("✅ Databases initialized")

    # Seed in order
    users = seed_users()
    accounts = seed_gl_accounts(users)
    seed_review_sessions()
    seed_user_feedback()
    seed_validation_results()

    # Print summary
    print_summary()


if __name__ == "__main__":
    main()
