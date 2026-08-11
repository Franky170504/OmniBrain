"""
===============================================================================
OmniBrain Database Session Management

File        : session.py
Module      : Database Infrastructure
Description :
    Centralized SQLAlchemy engine and session management.

Responsibilities
----------------
- Create SQLAlchemy Engine
- Configure Connection Pool
- Provide Session Factory
- FastAPI Dependency Injection
- Graceful Engine Disposal

Author      : OmniBrain Database Team
===============================================================================
"""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.app_config import app_settings

# =============================================================================
# SQLAlchemy Engine
# =============================================================================

engine: Engine = create_engine(
    app_settings.SQLALCHEMY_DATABASE_URI,

    echo=app_settings.SQL_ECHO,

    pool_size=app_settings.POOL_SIZE,
    max_overflow=app_settings.MAX_OVERFLOW,
    pool_timeout=app_settings.POOL_TIMEOUT,
    pool_recycle=app_settings.POOL_RECYCLE,
    pool_pre_ping=app_settings.POOL_PRE_PING,

    future=True,
)

# =============================================================================
# Session Factory
# =============================================================================

SessionLocal = sessionmaker(
    bind=engine,

    autocommit=False,
    autoflush=False,

    expire_on_commit=False,

    class_=Session,

    future=True,
)

# =============================================================================
# Dependency
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session.

    Example
    -------
    @router.get("/documents")
    def get_documents(db: Session = Depends(get_db)):
        ...
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =============================================================================
# Database Health Check
# =============================================================================

def check_database_connection() -> bool:
    """
    Verify PostgreSQL connectivity.

    Returns
    -------
    bool
        True if the database connection is healthy.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    except Exception:
        return False


# =============================================================================
# Engine Shutdown
# =============================================================================

def dispose_engine() -> None:
    """
    Close all pooled PostgreSQL connections.
    """

    engine.dispose()