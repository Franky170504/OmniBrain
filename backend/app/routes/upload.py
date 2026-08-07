from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_document_service
from app.models.schemas import UploadResponse
from app.services.document_service import DocumentService


router = APIRouter(prefix="/upload", tags=["Documents"])


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(default="local-user"),
    document_service: DocumentService = Depends(get_document_service),
    session: AsyncSession = Depends(get_db),
) -> UploadResponse:
    try:
        result = await document_service.process_upload(
            file=file,
            user_id=user_id,
            session=session,
        )
        return UploadResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {exc}") from exc
