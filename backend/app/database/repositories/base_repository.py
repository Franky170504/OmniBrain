"""
===============================================================================
OmniBrain Generic Base Repository

File        : base_repository.py
Module      : Database Repositories

Description
-----------
Generic repository providing reusable CRUD operations for all SQLAlchemy ORM
models.

Responsibilities
----------------
- Generic CRUD
- Pagination
- Counting
- Existence checks
- Transaction helpers

Business logic MUST NOT be placed here.

Author      : OmniBrain Database Team
===============================================================================
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic SQLAlchemy repository.
    """

    def __init__(
        self,
        session: Session,
        model: type[ModelType],
    ) -> None:

        self.session = session
        self.model = model

    # =======================================================================
    # CREATE
    # =======================================================================

    def create(self, entity: ModelType) -> ModelType:
        """
        Persist a single entity.
        """

        self.session.add(entity)

        return entity

    def create_many(
        self,
        entities: list[ModelType],
    ) -> list[ModelType]:
        """
        Persist multiple entities.
        """

        self.session.add_all(entities)

        return entities

    # =======================================================================
    # READ
    # =======================================================================

    def get_by_id(
        self,
        primary_key: Any,
    ) -> ModelType | None:
        """
        Retrieve entity by primary key.
        """

        return self.session.get(
            self.model,
            primary_key,
        )

    def get_all(self) -> list[ModelType]:
        """
        Retrieve all records.
        """

        statement = select(self.model)

        return list(
            self.session.scalars(statement).all()
        )

    def exists(
        self,
        primary_key: Any,
    ) -> bool:

        return (
            self.get_by_id(primary_key)
            is not None
        )

    def count(self) -> int:

        statement = select(
            func.count()
        ).select_from(
            self.model
        )

        return self.session.scalar(statement) or 0

    # =======================================================================
    # UPDATE
    # =======================================================================

    def update(
        self,
        entity: ModelType,
    ) -> ModelType:
        """
        Merge detached entity.
        """

        return self.session.merge(entity)

    # =======================================================================
    # DELETE
    # =======================================================================

    def delete(
        self,
        entity: ModelType,
    ) -> None:
        """
        Delete entity.
        """

        self.session.delete(entity)

    # =======================================================================
    # PAGINATION
    # =======================================================================

    def paginate(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> list[ModelType]:

        offset = (page - 1) * page_size

        statement = (
            select(self.model)
            .offset(offset)
            .limit(page_size)
        )

        return list(
            self.session.scalars(statement).all()
        )

    # =======================================================================
    # SESSION HELPERS
    # =======================================================================

    def flush(self) -> None:

        self.session.flush()

    def refresh(
        self,
        entity: ModelType,
    ) -> None:

        self.session.refresh(entity)

    def commit(self) -> None:

        self.session.commit()

    def rollback(self) -> None:

        self.session.rollback()