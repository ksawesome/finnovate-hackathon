"""PostgreSQL database models and operations using SQLAlchemy."""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
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


class GLAccount(Base):
    """GL Account model for trial balance data."""
    
    __tablename__ = "gl_accounts"
    
    id = Column(Integer, primary_key=True)
    account_code = Column(String(50), nullable=False)
    account_name = Column(String(255), nullable=False)
    entity = Column(String(255), nullable=False)
    balance = Column(Numeric(18, 2), nullable=False)
    period = Column(String(20), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    review_status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_user = relationship("User", back_populates="assigned_accounts")
    reviews = relationship("ReviewLog", back_populates="gl_account")


class ResponsibilityMatrix(Base):
    """Responsibility matrix for GL account assignments."""
    
    __tablename__ = "responsibility_matrix"
    
    id = Column(Integer, primary_key=True)
    gl_code = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


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


def init_db():
    """Initialize database tables."""
    engine = get_postgres_engine()
    Base.metadata.create_all(engine)


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    session = get_postgres_session()
    try:
        return session.query(User).filter(User.email == email).first()
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


def get_gl_accounts_by_period(period: str) -> List[GLAccount]:
    """Get all GL accounts for a specific period."""
    session = get_postgres_session()
    try:
        return session.query(GLAccount).filter(GLAccount.period == period).all()
    finally:
        session.close()


def create_gl_account(
    account_code: str,
    account_name: str,
    entity: str,
    balance: Decimal,
    period: str,
    assigned_user_id: Optional[int] = None
) -> GLAccount:
    """Create a new GL account."""
    session = get_postgres_session()
    try:
        gl_account = GLAccount(
            account_code=account_code,
            account_name=account_name,
            entity=entity,
            balance=balance,
            period=period,
            assigned_user_id=assigned_user_id
        )
        session.add(gl_account)
        session.commit()
        session.refresh(gl_account)
        return gl_account
    finally:
        session.close()


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
