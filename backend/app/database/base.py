"""
===============================================================================
OmniBrain SQLAlchemy Base

File        : base.py
Module      : Database Infrastructure

Description
-----------
Defines the SQLAlchemy Declarative Base shared by all ORM models.

Responsibilities
----------------
- SQLAlchemy Declarative Base
- Shared metadata for all database schemas

NOTE
----
This file intentionally contains NO mixins.

Reusable mixins are defined in:

    app.database.mixins

Author      : OmniBrain Database Team
===============================================================================
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# =============================================================================
# Naming Convention
# =============================================================================

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(
    naming_convention=NAMING_CONVENTION
)

# =============================================================================
# Declarative Base
# =============================================================================

class Base(DeclarativeBase):
    """
    Base class inherited by every SQLAlchemy ORM model.

    This class intentionally contains no business logic,
    columns or mixins.
    """

    metadata = metadata