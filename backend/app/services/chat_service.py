from fastapi import HTTPException, status
from app.services.document_service import document_service


class ChatService:
    """Service handling document interaction and mock Q&A responses."""

    async def get_chat_response(self, document_id: str, question: str) -> dict:
        """
        Validates document existence and returns a structured mock answer.
        Ready for future RAG / LLM / Vector DB pipeline integration.
        """
        # Validate that the requested document exists in backend/uploads/
        if not document_service.document_exists(document_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{document_id}' not found. Please upload the PDF first."
            )

        # Mock AI answer response (clean, modular placeholder for future LLM pipeline)
        mock_answer = (
            f"[Mock AI Response]: Based on document ID '{document_id}', "
            f"here is a simulated analysis for your question: '{question}'."
        )

        mock_sources = [
            f"Document {document_id}.pdf - Section 1.2",
            f"Document {document_id}.pdf - Page 3"
        ]

        return {
            "document_id": document_id,
            "question": question,
            "answer": mock_answer,
            "sources": mock_sources
        }


chat_service = ChatService()
