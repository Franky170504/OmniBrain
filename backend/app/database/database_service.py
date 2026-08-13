"""
===============================================================================
OmniBrain Database Service

File        : database_service.py
Module      : Database Infrastructure

Description
-----------
High-level database service responsible for managing PostgreSQL connectivity.

Responsibilities
----------------
- Validate database connectivity
- Provide SQLAlchemy sessions
- Execute health checks
- Manage startup and shutdown
- Provide transaction context managers

This class intentionally contains no business logic.

Author      : OmniBrain Database Team
===============================================================================
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.custom_exception import CustomException
from app.database.session import (
    SessionLocal,
    check_database_connection,
    dispose_engine,
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    High-level PostgreSQL service.

    This class wraps SQLAlchemy session management and exposes
    a clean interface to the rest of the application.
    """

    def __init__(self) -> None:
        self._connected = True

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def connect(self) -> None:
        logger.info("Initializing PostgreSQL database service...")

        try:
            self._connected = True

        except Exception as exc:
            raise CustomException("Unable to establish PostgreSQL connection. {exc}")


        logger.info("PostgreSQL database connected successfully.")

    def close(self) -> None:
        """
        Gracefully dispose SQLAlchemy resources.
        """

        logger.info("Closing PostgreSQL database service...")

        dispose_engine()

        self._connected = False

        logger.info("PostgreSQL database service stopped.")

    # =========================================================================
    # Health
    # =========================================================================

    def is_healthy(self) -> bool:
        """
        Check database availability.
        """

        return check_database_connection()

    @property
    def connected(self) -> bool:
        """
        Returns current connection status.
        """

        return self._connected

    # =========================================================================
    # Session Management
    # =========================================================================

    def get_session(self) -> Session:
        """
        Create a new SQLAlchemy session.

        Returns
        -------
        Session
            SQLAlchemy database session.
        """

        return SessionLocal()

    def session_generator(self) -> Generator[Session, None, None]:
        """
        FastAPI dependency generator.
        """

        db = SessionLocal()

        try:
            yield db

        finally:
            db.close()

    @contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """
        Transaction context manager.

        Example
        -------
        with database_service.transaction() as db:
            ...
        """

        session = SessionLocal()

        try:
            yield session

            session.commit()

        except Exception:

            session.rollback()

            raise

        finally:

            session.close()

    # =========================================================================
    # Diagnostics
    # =========================================================================

    def execute_health_check(self) -> dict:
        """
        Execute a lightweight PostgreSQL health check.

        Returns
        -------
        dict
            Database health information.
        """

        try:

            with SessionLocal() as session:

                session.execute(text("SELECT 1"))

            return {
                "status": "healthy",
                "database": "PostgreSQL",
                "connected": True,
            }

        except SQLAlchemyError as exc:

            logger.exception(exc)

            return {
                "status": "unhealthy",
                "database": "PostgreSQL",
                "connected": False,
                "error": str(exc),
            }