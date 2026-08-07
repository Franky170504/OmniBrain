from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import ChatRepository, KnowledgeRepository, UserRepository
from app.dependencies import get_db


router = APIRouter(tags=["History"])


@router.get("/sessions")
async def list_sessions(
    user_id: str = Query(default="local-user"),
    session: AsyncSession = Depends(get_db),
):
    users = UserRepository(session)
    chats = ChatRepository(session)
    db_user_id = await users.resolve_user(user_id)
    await session.commit()
    return await chats.list_sessions(user_id=db_user_id)


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: UUID,
    user_id: str = Query(default="local-user"),
    session: AsyncSession = Depends(get_db),
):
    users = UserRepository(session)
    chats = ChatRepository(session)
    db_user_id = await users.resolve_user(user_id)
    await session.commit()
    if not await chats.validate_session_owner(session_id=session_id, user_id=db_user_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return await chats.get_messages(session_id=session_id, user_id=db_user_id)


@router.get("/documents")
async def list_documents(
    user_id: str = Query(default="local-user"),
    session: AsyncSession = Depends(get_db),
):
    users = UserRepository(session)
    knowledge = KnowledgeRepository(session)
    db_user_id = await users.resolve_user(user_id)
    await session.commit()
    return await knowledge.list_documents_for_user(db_user_id)
