"""PostgreSQL database models and operations using SQLAlchemy."""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Boolean,
    UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

from . import get_postgres_engine, get_postgres_session

Base = declarative_base()


class User(Base):
    """User model for stakeholders."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    department = Column(String(100))
    role = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_accounts = relationship("GLAccount", back_populates="assigned_user")
    reviews = relationship("ReviewLog", back_populates="reviewer")
    assignments = relationship("ResponsibilityMatrix", back_populates="assigned_user")


class GLAccount(Base):
    """GL Account model for trial balance data (Extended from Final Data sheet)."""
    
    __tablename__ = "gl_accounts"
    
    # Core identification
    id = Column(Integer, primary_key=True)
    account_code = Column(String(50), nullable=False)
    account_name = Column(String(255), nullable=False)
    entity = Column(String(255), nullable=False, default='ABEX')
    company_code = Column(String(20), nullable=False, default='5500')
    
    # Financial data
    balance = Column(Numeric(18, 2), nullable=False)
    balance_carryforward = Column(Numeric(18, 2))
    debit_period = Column(Numeric(18, 2))
    credit_period = Column(Numeric(18, 2))
    period = Column(String(20), nullable=False)
    
    # Classification
    bs_pl = Column(String(10))  # 'BS' or 'PL'
    status = Column(String(50))  # Assets, Liabilities, Income, Expense, Equity
    account_category = Column(String(100))  # Main Head
    sub_category = Column(String(100))  # Sub head
    
    # Review metadata
    review_status = Column(String(50), default='pending')  # pending, reviewed, flagged, skipped
    review_flag = Column(String(20))  # Green, Red, Not Considered
    review_checkpoint = Column(Text)
    criticality = Column(String(20))  # Critical, Medium, Low
    review_frequency = Column(String(20))  # Monthly, Quarterly, Half Yearly
    
    # Supporting documentation
    report_type = Column(String(100))  # Inventory report, Fixed asset report, etc.
    analysis_required = Column(String(10))  # 'Yes' or 'No' - matches Excel data format
    reconciliation_type = Column(String(50))  # Reconciliation GL, Non Reconciliation GL
    variance_pct = Column(String(50))
    
    # Assignment
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String(50))  # R2R, TRM, O2C, B2P, IDT
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('account_code', 'company_code', 'period', name='uq_gl_account_company_period'),
        Index('idx_gl_accounts_period', 'period'),
        Index('idx_gl_accounts_entity', 'entity'),
        Index('idx_gl_accounts_company', 'company_code'),
        Index('idx_gl_accounts_status', 'review_status'),
        Index('idx_gl_accounts_criticality', 'criticality'),
        Index('idx_gl_accounts_department', 'department'),
        Index('idx_gl_accounts_composite', 'company_code', 'period', 'review_status'),
    )
    
    # Relationships
    assigned_user = relationship("User", back_populates="assigned_accounts")
    reviews = relationship("ReviewLog", back_populates="gl_account")
    versions = relationship("GLAccountVersion", back_populates="gl_account")


class ResponsibilityMatrix(Base):
    """Responsibility matrix for GL account assignments (Extended from Sheet3)."""
    
    __tablename__ = "responsibility_matrix"
    
    id = Column(Integer, primary_key=True)
    
    # Assignment identification
    assignment_id = Column(String(50), unique=True)  # ID from Sheet3
    gl_code = Column(String(50), nullable=False)
    company_code = Column(String(20), nullable=False, default='5500')
    
    # User assignment
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String(50))  # R Department
    person_name = Column(String(255))  # R Person Name (email)
    
    # Multi-stage workflow status
    prepare_status = Column(String(20))  # P.S: Pending, Complete
    review_status = Column(String(20))  # R.S: Pending, Complete
    final_status = Column(String(20))  # F.S: Pending, Complete
    form_filled = Column(String(10))  # FF: 'Yes' or 'No' - matches Excel format
    approved = Column(String(10))  # Ok: 'Yes' or 'No' - matches Excel format
    
    # Severity & Priority
    severity = Column(String(20))  # Critical, Medium, Low
    
    # Financial reconciliation data
    amount_lc = Column(Numeric(18, 2))  # Amt Lc
    reconciled_amount_lc = Column(Numeric(18, 2))
    bs_reclassification_lc = Column(Numeric(18, 2))  # BS Reclassification LC
    pl_impact_amt_lc = Column(Numeric(18, 2))  # P&L Impact Amt LC
    overall_reconciliation_status = Column(String(50))
    
    # Query tracking
    query_type = Column(Text)  # Long text field
    working_needed = Column(Text)  # Long text field
    
    # Comments
    preparer_comment = Column(Text)  # P Comment
    reviewer_comment = Column(Text)  # R Comment
    
    # Metadata
    assignment_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('gl_code', 'company_code', 'assignment_id', name='uq_assignment_gl_company'),
        Index('idx_responsibility_assignment', 'assignment_id'),
        Index('idx_responsibility_gl', 'gl_code'),
        Index('idx_responsibility_user', 'assigned_user_id'),
        Index('idx_responsibility_status', 'prepare_status', 'review_status', 'final_status'),
        Index('idx_responsibility_severity', 'severity'),
    )
    
    # Relationships
    assigned_user = relationship("User", back_populates="assignments")


class MasterChartOfAccounts(Base):
    """Master chart of accounts from Base File sheet (2736 accounts)."""
    
    __tablename__ = "master_chart_of_accounts"
    
    id = Column(Integer, primary_key=True)
    
    # Account identification
    account_code = Column(String(50), nullable=False, unique=True)
    account_description = Column(String(255))
    
    # Hierarchy
    group_gl_account = Column(String(50))  # Parent account
    main_group = Column(String(100))
    sub_group = Column(String(100))
    
    # Classification
    bs_pl = Column(String(10))  # BS or PL
    schedule_number = Column(String(20))  # Financial statement schedule (SCH-01, SCH-02, etc.)
    
    # Trial balance data (entity 5500)
    tb_5500 = Column(Numeric(18, 2))  # Original trial balance
    reclassification_mar_18 = Column(Numeric(18, 2))  # Historical adjustment
    derived_tb_5500 = Column(Numeric(18, 2))  # Calculated: TB + Reclassification
    
    # Reporting amounts
    bs_amount = Column(Numeric(18, 2))
    amt_v1 = Column(Numeric(18, 2))
    
    # Status
    is_active = Column(Boolean, default=True)  # In current review set (Final Data)
    last_reviewed_period = Column(String(20))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_master_coa_code', 'account_code'),
        Index('idx_master_coa_group', 'group_gl_account'),
        Index('idx_master_coa_schedule', 'schedule_number'),
        Index('idx_master_coa_active', 'is_active'),
    )


class GLAccountVersion(Base):
    """Version control for GL accounts (from Final Data Backup pattern)."""
    
    __tablename__ = "gl_account_versions"
    
    version_id = Column(Integer, primary_key=True)
    
    # Link to current account
    gl_account_id = Column(Integer, ForeignKey("gl_accounts.id"))
    account_code = Column(String(50), nullable=False)
    
    # Version tracking
    version_number = Column(Integer, nullable=False)
    snapshot_date = Column(DateTime, default=datetime.utcnow)
    
    # User tracking
    created_by = Column(Integer, ForeignKey("users.id"))
    change_reason = Column(String(255))
    
    # Full snapshot as JSON
    snapshot_data = Column(JSONB, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('gl_account_id', 'version_number', name='uq_version_account_number'),
        Index('idx_versions_account', 'gl_account_id'),
        Index('idx_versions_date', 'snapshot_date'),
        Index('idx_versions_user', 'created_by'),
    )
    
    # Relationships
    gl_account = relationship("GLAccount", back_populates="versions")


class AccountMasterTemplate(Base):
    """Historical account template from Final Data - Old sheet (2718 accounts)."""
    
    __tablename__ = "account_master_template"
    
    id = Column(Integer, primary_key=True)
    
    # Account identification
    account_code = Column(String(50), nullable=False, unique=True)
    account_description = Column(String(255))
    
    # Classification
    bs_pl = Column(String(10))
    nature = Column(String(100))  # "Inventory - Not Consider", "TRM - Not Consider", etc.
    
    # Ownership
    department = Column(String(50))  # R2R, TRM, IDT, O2C, B2P
    main_head = Column(String(100))
    sub_head = Column(String(100))
    
    # Review requirements
    reconciliation_report_type = Column(String(100))  # Working, Confirmation, BU Score card
    is_automated = Column(Boolean)  # Automated vs Manual
    standard_query_type = Column(Text)  # Pre-defined query for this account type
    
    # Status
    is_active = Column(Boolean, default=True)  # Currently in review cycle
    filter_reason = Column(String(100))  # Why filtered: "Not Consider", "Zero Balance", etc.
    last_reviewed_period = Column(String(20))
    
    # Historical balance
    balance_historical = Column(Numeric(18, 2))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_template_nature', 'nature'),
        Index('idx_template_dept', 'department'),
        Index('idx_template_active', 'is_active'),
    )


class ReviewLog(Base):
    """Review log for audit trail."""
    
    __tablename__ = "review_log"
    
    id = Column(Integer, primary_key=True)
    gl_account_id = Column(Integer, ForeignKey("gl_accounts.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), nullable=False)
    comments = Column(Text)
    reviewed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    gl_account = relationship("GLAccount", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")


# ============================================================================
# Database Initialization
# ============================================================================

def init_db():
    """Initialize database tables."""
    engine = get_postgres_engine()
    Base.metadata.create_all(engine)
    print("✅ PostgreSQL tables created successfully")
    print(f"   - {len(Base.metadata.tables)} tables initialized")
    for table_name in Base.metadata.tables.keys():
        print(f"     • {table_name}")


# ============================================================================
# User Operations
# ============================================================================

def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    session = get_postgres_session()
    try:
        return session.query(User).filter(User.email == email).first()
    finally:
        session.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID."""
    session = get_postgres_session()
    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()


def create_user(name: str, email: str, department: str, role: str) -> User:
    """Create a new user."""
    session = get_postgres_session()
    try:
        user = User(name=name, email=email, department=department, role=role)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


# ============================================================================
# GL Account Operations
# ============================================================================

def get_gl_accounts_by_period(period: str, company_code: Optional[str] = None) -> List[GLAccount]:
    """Get all GL accounts for a specific period."""
    session = get_postgres_session()
    try:
        query = session.query(GLAccount).filter(GLAccount.period == period)
        if company_code:
            query = query.filter(GLAccount.company_code == company_code)
        return query.all()
    finally:
        session.close()


def get_gl_account_by_code(account_code: str, company_code: str, period: str) -> Optional[GLAccount]:
    """Get GL account by code, company, and period."""
    session = get_postgres_session()
    try:
        return session.query(GLAccount).filter(
            GLAccount.account_code == account_code,
            GLAccount.company_code == company_code,
            GLAccount.period == period
        ).first()
    finally:
        session.close()


def create_gl_account(
    account_code: str,
    account_name: str,
    entity: str,
    balance: Decimal,
    period: str,
    company_code: str = '5500',
    **kwargs
) -> GLAccount:
    """Create a new GL account with extended fields."""
    session = get_postgres_session()
    try:
        gl_account = GLAccount(
            account_code=account_code,
            account_name=account_name,
            entity=entity,
            balance=balance,
            period=period,
            company_code=company_code,
            **kwargs
        )
        session.add(gl_account)
        session.commit()
        session.refresh(gl_account)
        return gl_account
    finally:
        session.close()


def update_gl_account(gl_account_id: int, **kwargs) -> Optional[GLAccount]:
    """Update GL account fields."""
    session = get_postgres_session()
    try:
        gl_account = session.query(GLAccount).filter(GLAccount.id == gl_account_id).first()
        if gl_account:
            for key, value in kwargs.items():
                setattr(gl_account, key, value)
            gl_account.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(gl_account)
        return gl_account
    finally:
        session.close()


# ============================================================================
# Responsibility Matrix Operations
# ============================================================================

def create_responsibility_assignment(
    gl_code: str,
    company_code: str,
    assigned_user_id: int,
    **kwargs
) -> ResponsibilityMatrix:
    """Create a new responsibility assignment."""
    session = get_postgres_session()
    try:
        assignment = ResponsibilityMatrix(
            gl_code=gl_code,
            company_code=company_code,
            assigned_user_id=assigned_user_id,
            **kwargs
        )
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment
    finally:
        session.close()


def get_user_assignments(user_id: int, status_filter: Optional[str] = None) -> List[ResponsibilityMatrix]:
    """Get all assignments for a user."""
    session = get_postgres_session()
    try:
        query = session.query(ResponsibilityMatrix).filter(
            ResponsibilityMatrix.assigned_user_id == user_id
        )
        if status_filter:
            query = query.filter(ResponsibilityMatrix.prepare_status == status_filter)
        return query.all()
    finally:
        session.close()


# ============================================================================
# Master Chart of Accounts Operations
# ============================================================================

def create_master_account(account_code: str, account_description: str, **kwargs) -> MasterChartOfAccounts:
    """Create a master chart of accounts entry."""
    session = get_postgres_session()
    try:
        master_account = MasterChartOfAccounts(
            account_code=account_code,
            account_description=account_description,
            **kwargs
        )
        session.add(master_account)
        session.commit()
        session.refresh(master_account)
        return master_account
    finally:
        session.close()


def get_master_account(account_code: str) -> Optional[MasterChartOfAccounts]:
    """Get master account by code."""
    session = get_postgres_session()
    try:
        return session.query(MasterChartOfAccounts).filter(
            MasterChartOfAccounts.account_code == account_code
        ).first()
    finally:
        session.close()


def get_account_hierarchy_children(parent_code: str) -> List[MasterChartOfAccounts]:
    """Get all child accounts for a parent GL account."""
    session = get_postgres_session()
    try:
        return session.query(MasterChartOfAccounts).filter(
            MasterChartOfAccounts.group_gl_account == parent_code
        ).all()
    finally:
        session.close()


# ============================================================================
# Version Control Operations
# ============================================================================

def create_version_snapshot(
    gl_account_id: int,
    account_code: str,
    snapshot_data: dict,
    created_by: int,
    change_reason: str
) -> GLAccountVersion:
    """Create a version snapshot before modifying GL account."""
    session = get_postgres_session()
    try:
        # Get latest version number
        latest = session.query(GLAccountVersion).filter(
            GLAccountVersion.gl_account_id == gl_account_id
        ).order_by(GLAccountVersion.version_number.desc()).first()
        
        new_version_number = (latest.version_number + 1) if latest else 1
        
        version = GLAccountVersion(
            gl_account_id=gl_account_id,
            account_code=account_code,
            version_number=new_version_number,
            snapshot_data=snapshot_data,
            created_by=created_by,
            change_reason=change_reason
        )
        session.add(version)
        session.commit()
        session.refresh(version)
        return version
    finally:
        session.close()


def get_account_version_history(gl_account_id: int) -> List[GLAccountVersion]:
    """Get all versions for a GL account."""
    session = get_postgres_session()
    try:
        return session.query(GLAccountVersion).filter(
            GLAccountVersion.gl_account_id == gl_account_id
        ).order_by(GLAccountVersion.version_number.desc()).all()
    finally:
        session.close()


# ============================================================================
# Account Template Operations
# ============================================================================

def create_account_template(account_code: str, **kwargs) -> AccountMasterTemplate:
    """Create an account master template entry."""
    session = get_postgres_session()
    try:
        template = AccountMasterTemplate(
            account_code=account_code,
            **kwargs
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        return template
    finally:
        session.close()


def get_template_by_nature(nature: str) -> List[AccountMasterTemplate]:
    """Get all template accounts by nature classification."""
    session = get_postgres_session()
    try:
        return session.query(AccountMasterTemplate).filter(
            AccountMasterTemplate.nature.ilike(f"%{nature}%")
        ).all()
    finally:
        session.close()


def get_active_templates(department: Optional[str] = None) -> List[AccountMasterTemplate]:
    """Get all active account templates."""
    session = get_postgres_session()
    try:
        query = session.query(AccountMasterTemplate).filter(
            AccountMasterTemplate.is_active == True
        )
        if department:
            query = query.filter(AccountMasterTemplate.department == department)
        return query.all()
    finally:
        session.close()


# ============================================================================
# Review Log Operations
# ============================================================================

def log_review(gl_account_id: int, reviewer_id: int, status: str, comments: str = "") -> ReviewLog:
    """Log a review action."""
    session = get_postgres_session()
    try:
        review = ReviewLog(
            gl_account_id=gl_account_id,
            reviewer_id=reviewer_id,
            status=status,
            comments=comments
        )
        session.add(review)
        session.commit()
        session.refresh(review)
        return review
    finally:
        session.close()


def get_account_review_history(gl_account_id: int) -> List[ReviewLog]:
    """Get all reviews for a GL account."""
    session = get_postgres_session()
    try:
        return session.query(ReviewLog).filter(
            ReviewLog.gl_account_id == gl_account_id
        ).order_by(ReviewLog.reviewed_at.desc()).all()
    finally:
        session.close()
