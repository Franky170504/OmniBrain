"""
===============================================================================
OmniBrain ORM Mixins

File        : mixins.py
Module      : Database Infrastructure

Description
-----------
Reusable ORM mixins shared across multiple models.

Responsibilities
----------------
- Audit timestamps
- Future soft delete support
- Future ownership support
- Future version tracking

Author      : OmniBrain Database Team
===============================================================================
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

# =============================================================================
# Timestamp Mixin
# =============================================================================

class TimestampMixin:
    """
    Adds audit timestamps.

    These columns mirror the PostgreSQL schema.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


# =============================================================================
# Soft Delete Mixin (Future)
# =============================================================================

class SoftDeleteMixin:
    """
    Optional soft delete support.

    This mixin is intentionally NOT used until a table
    explicitly supports logical deletion.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


# =============================================================================
# Ownership Mixin (Future)
# =============================================================================

class OwnershipMixin:
    """
    Placeholder for future ownership tracking.

    Example
    -------
    created_by
    updated_by
    """

    pass


# =============================================================================
# Version Mixin (Future)
# =============================================================================

class VersionMixin:
    """
    Placeholder for optimistic locking/version control.

    Can later expose:

        version_number

    for ORM-managed optimistic concurrency.
    """

    pass