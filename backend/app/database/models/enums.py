"""
===============================================================================
OmniBrain Database Enums

File        : enums.py
Module      : SQLAlchemy Models

Description
-----------
Centralized enumerations mirrored from the PostgreSQL schema.

IMPORTANT
---------
These enums MUST stay synchronized with the CHECK constraints defined
inside backend/database/schema/03_knowledge.sql.

Do not rename values unless the SQL schema changes.
===============================================================================
"""

from enum import Enum


# =============================================================================
# Knowledge Schema
# =============================================================================

class DocumentType(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    PPTX = "PPTX"
    XLSX = "XLSX"
    IMAGE = "IMAGE"
    TEXT = "TEXT"
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"
    OTHER = "OTHER"


class ProcessingStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PARSING = "PARSING"
    OCR_RUNNING = "OCR_RUNNING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


class PageType(str, Enum):
    DOCUMENT = "DOCUMENT"
    SLIDE = "SLIDE"
    IMAGE = "IMAGE"
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"
    OCR = "OCR"


class ChunkType(str, Enum):
    TEXT = "TEXT"
    TITLE = "TITLE"
    HEADER = "HEADER"
    FOOTER = "FOOTER"
    LIST = "LIST"
    TABLE = "TABLE"
    IMAGE_CAPTION = "IMAGE_CAPTION"
    CODE = "CODE"


class ChunkStatus(str, Enum):
    CREATED = "CREATED"
    EMBEDDED = "EMBEDDED"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


class ImageStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    OCR_COMPLETED = "OCR_COMPLETED"
    CAPTION_GENERATED = "CAPTION_GENERATED"
    EMBEDDED = "EMBEDDED"
    FAILED = "FAILED"


class StorageFormat(str, Enum):
    CSV = "CSV"
    JSON = "JSON"
    PARQUET = "PARQUET"


class TableType(str, Enum):
    DATA_TABLE = "DATA_TABLE"
    KEY_VALUE = "KEY_VALUE"
    MATRIX = "MATRIX"
    FINANCIAL = "FINANCIAL"
    UNKNOWN = "UNKNOWN"


class TableStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    SUMMARIZED = "SUMMARIZED"
    EMBEDDED = "EMBEDDED"
    FAILED = "FAILED"


class TagType(str, Enum):
    DOMAIN = "DOMAIN"
    TOPIC = "TOPIC"
    TECHNOLOGY = "TECHNOLOGY"
    DOCUMENT_TYPE = "DOCUMENT_TYPE"
    LANGUAGE = "LANGUAGE"
    SECURITY = "SECURITY"
    CUSTOM = "CUSTOM"


class TagSource(str, Enum):
    MANUAL = "MANUAL"
    AUTO = "AUTO"
    LLM = "LLM"
    IMPORT = "IMPORT"