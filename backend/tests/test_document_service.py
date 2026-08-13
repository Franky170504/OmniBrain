import asyncio
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.document_service import DocumentService


def test_document_service_accepts_injected_document_repository() -> None:
    repository = MagicMock()
    service = DocumentService(
        qdrant_service=MagicMock(),
        document_repository=repository,
        database_service=MagicMock(),
        minio_service=MagicMock(),
    )

    assert service.document_repository is repository


def test_build_document_record_includes_storage_and_processing_metadata() -> None:
    service = DocumentService(qdrant_service=None)  # type: ignore[arg-type]

    parsed_document = {
        "document_id": "doc-123",
        "filename": "sample.pdf",
        "page_count": 3,
        "chunk_count": 5,
        "image_occurrence_count": 2,
        "unique_image_count": 1,
        "sha256": "a" * 64,
        "metadata": {"title": "Example"},
    }

    saved_path = Path("/tmp/sample.pdf")
    collection_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

    record = service._build_document_record(
        parsed_document=parsed_document,
        saved_path=saved_path,
        original_filename="sample.pdf",
        bucket_name="omnibrain-docs",
        object_path="uploads/doc-123/sample.pdf",
        user_id="user-1",
        collection_id=collection_id,
    )

    assert record["document_id"] == "doc-123"
    assert record["document_title"] == "Example"
    assert record["original_filename"] == "sample.pdf"
    assert record["bucket_name"] == "omnibrain-docs"
    assert record["object_path"] == "uploads/doc-123/sample.pdf"
    assert record["processing_status"] == "UPLOADED"
    assert record["page_count"] == 3
    assert record["chunk_count"] == 5
    assert record["image_count"] == 2
    assert record["file_extension"] == "pdf"
    assert record["owner_user_id"] == uuid.uuid5(uuid.NAMESPACE_URL, "user-1")


def test_process_upload_uses_document_id_in_object_path() -> None:
    service = DocumentService(
        qdrant_service=MagicMock(),
        document_repository=MagicMock(),
        database_service=MagicMock(),
        minio_service=MagicMock(),
    )

    file = MagicMock()
    service.save_upload = AsyncMock(return_value=(Path("/tmp/sample file.pdf"), "sample file.pdf"))

    parsed_document = {
        "document_id": "doc-123",
        "page_count": 2,
        "chunk_count": 3,
        "image_occurrence_count": 1,
        "sha256": "b" * 64,
        "metadata": {"title": "Sample"},
    }

    with patch("app.services.document_service.parse_pdf", return_value=(parsed_document, [], [])), \
         patch.object(service, "_ensure_default_collection", return_value=uuid.uuid4()), \
         patch.object(service, "_mark_processing_status"), \
         patch.object(service, "_persist_document_ingestion", return_value=(True, MagicMock(document_id="doc-123"))) as mock_persist, \
            patch.object(service, "_verify_document_ready_for_index", return_value=True), \
         patch.object(service.qdrant_service, "ingest_chunks", return_value=0):
        asyncio.run(service.process_upload(file=file, user_id="user-1"))

    persisted_record = mock_persist.call_args.kwargs["record"]
    assert persisted_record["object_path"] == "uploads/doc-123/sample file.pdf"
    assert "doc-123" in persisted_record["object_path"]


def test_duplicate_filename_with_different_document_ids_generates_different_paths() -> None:
    path_a = "uploads/doc-1/sample file.pdf"
    path_b = "uploads/doc-2/sample file.pdf"

    assert path_a != path_b
    assert path_a.startswith("uploads/doc-1/")
    assert path_b.startswith("uploads/doc-2/")


def test_create_chunks_uses_one_based_indexes_and_keeps_page_numbers() -> None:
    from app.pipeline.parsing_pipeline import PageText, create_chunks

    pages = [
        PageText(page_number=1, text="alpha beta gamma delta"),
        PageText(page_number=2, text="epsilon zeta eta theta iota"),
    ]

    chunks = create_chunks(
        pages=pages,
        document_id="doc-one",
        source_file="sample.pdf",
        document_metadata={},
        chunk_size=18,
        overlap=0,
    )

    assert [chunk.chunk_index for chunk in chunks] == [1, 2, 3, 4]
    assert [chunk.page_start for chunk in chunks] == [1, 1, 2, 2]
    assert [chunk.page_end for chunk in chunks] == [1, 1, 2, 2]
    assert [chunk.text for chunk in chunks] == [
        "alpha beta gamma",
        "delta",
        "epsilon zeta eta",
        "theta iota",
    ]
