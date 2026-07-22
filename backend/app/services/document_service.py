import uuid
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings


class DocumentService:
    """Service handling document validation, storage, and retrieval."""

    def __init__(self, upload_dir: Path = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir
        # Ensure uploads directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_pdf(self, file: UploadFile) -> dict:
        """
        Asynchronously validates and saves an uploaded PDF document.
        Stores the PDF in backend/uploads/ using document_id as filename.
        """
        filename = file.filename or "document.pdf"
        
        # 1. Extension validation
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file extension. Only PDF files (.pdf) are allowed."
            )

        # 2. Content-type validation
        if file.content_type and "pdf" not in file.content_type.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content-type '{file.content_type}'. Expected PDF file."
            )

        # 3. Read content asynchronously
        try:
            content = await file.read()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read uploaded file stream: {str(e)}"
            )

        # 4. File size check
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed limit of {settings.MAX_FILE_SIZE_MB}MB."
            )

        # 5. Generate unique document ID and save
        document_id = str(uuid.uuid4())
        destination_path = self.upload_dir / f"{document_id}.pdf"

        try:
            async with aiofiles.open(destination_path, "wb") as out_file:
                await out_file.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save document to storage: {str(e)}"
            )
        finally:
            await file.close()

        return {
            "document_id": document_id,
            "filename": filename,
            "file_size": len(content),
            "message": "Document uploaded and stored successfully."
        }

    def document_exists(self, document_id: str) -> bool:
        """Checks if a document with the specified ID exists in storage."""
        path = self.upload_dir / f"{document_id}.pdf"
        return path.is_file()


document_service = DocumentService()
