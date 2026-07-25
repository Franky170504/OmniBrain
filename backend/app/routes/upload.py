from __future__ import annotations
from fastapi import APIRouter, File, UploadFile, status,HTTPException,Form,Depends
from backend.app.dependencies import get_document_service
from backend.app.models.schemas import UploadResponse
from backend.app.services.document_service import DocumentService

router = APIRouter(tags=["Document Management"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(default="local-user"),
    document_service: DocumentService = Depends(
        get_document_service
    ),
) -> UploadResponse:
    try:
        result = await document_service.process_upload(
            file=file,
            user_id=user_id,
        )

        return UploadResponse(**result)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {exc}",
        ) from exc