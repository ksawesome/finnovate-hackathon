"""Database connection managers and configuration."""

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pymongo import MongoClient
from pymongo.database import Database

# PostgreSQL configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "finnovate")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hackathon2025")

POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# MongoDB configuration
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("MONGO_DB", "finnovate")

MONGO_URL = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

# Global instances
_postgres_engine = None
_postgres_session_factory = None
_mongo_client = None


def get_postgres_engine():
    """Get or create PostgreSQL engine."""
    global _postgres_engine
    if _postgres_engine is None:
        _postgres_engine = create_engine(
            POSTGRES_URL,
            pool_size=10,
            max_overflow=20,
            echo=False
        )
    return _postgres_engine


def get_postgres_session() -> Session:
    """Get a PostgreSQL database session."""
    global _postgres_session_factory
    if _postgres_session_factory is None:
        engine = get_postgres_engine()
        _postgres_session_factory = sessionmaker(bind=engine)
    return _postgres_session_factory()


def get_mongo_client() -> MongoClient:
    """Get or create MongoDB client."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URL)
    return _mongo_client


def get_mongo_database(db_name: Optional[str] = None) -> Database:
    """Get MongoDB database."""
    client = get_mongo_client()
    return client[db_name or MONGO_DB]


def close_connections():
    """Close all database connections."""
    global _postgres_engine, _mongo_client
    if _postgres_engine:
        _postgres_engine.dispose()
        _postgres_engine = None
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
