from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies import get_authenticated_user_id, get_auth_service, get_document_service
from app.models.schemas import OwnerAssignmentRequest, UploadResponse
from app.services.document_service import DocumentAuthorizationError, DocumentService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/upload",tags=["Documents"])

@router.post("",operation_id="upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), user_id: str = Depends(get_authenticated_user_id), document_service: DocumentService = Depends(get_document_service)) -> UploadResponse:
    try:
        result = await document_service.process_upload(file=file,user_id=user_id,)
        return UploadResponse(**result)

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(exc)) from exc

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Document processing failed: {exc}") from exc


@router.delete("/{document_id}", operation_id="delete_document")
def delete_document(
    document_id: str,
    user_id: str = Depends(get_authenticated_user_id),
    document_service: DocumentService = Depends(get_document_service),
) -> dict[str, object]:
    try:
        deleted = document_service.delete_document(
            document_id=document_id,
            user_id=user_id,
        )
        return {
            "deleted": deleted,
            "document_id": document_id,
        }
    except DocumentAuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document deletion failed: {exc}",
        ) from exc


@router.put("/{document_id}/owner", operation_id="assign_document_owner")
def assign_document_owner(
    document_id: str,
    payload: OwnerAssignmentRequest,
    user_id: str = Depends(get_authenticated_user_id),
    document_service: DocumentService = Depends(get_document_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, object]:
    try:
        assigned = document_service.assign_document_owner(
            document_id=document_id,
            owner_user_id=payload.owner_user_id,
            assigning_user_id=user_id,
            auth_service=auth_service,
        )
        if not assigned:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
        return {"assigned": True, "document_id": document_id, "owner_user_id": payload.owner_user_id}
    except DocumentAuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
