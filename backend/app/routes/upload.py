from fastapi import APIRouter, File, UploadFile, status
from app.models.schemas import UploadResponse, ErrorResponse
from app.services.document_service import document_service

router = APIRouter(tags=["Document Management"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Asynchronous Document Upload",
    description="Upload a PDF document asynchronously. The file is validated and saved to local storage with a unique document ID.",
    responses={
        201: {"model": UploadResponse, "description": "Document successfully uploaded and saved."},
        400: {"model": ErrorResponse, "description": "Invalid file format, MIME type, or file size limit exceeded."},
        500: {"model": ErrorResponse, "description": "Internal server error during document saving."}
    }
)
async def upload_document(
    file: UploadFile = File(..., description="PDF file to be uploaded")
) -> UploadResponse:
    """
    Asynchronous endpoint to upload PDF documents.
    Generates a unique document_id and stores the file in backend/uploads/{document_id}.pdf.
    """
    result = await document_service.save_pdf(file)
    return UploadResponse(**result)
