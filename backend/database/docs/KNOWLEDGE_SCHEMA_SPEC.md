# Knowledge Schema Specification

**Project:** OmniBrain – Enterprise Multi-Modal RAG Platform

**Schema:** `knowledge`

**Database:** PostgreSQL 17+

**Version:** 1.0

---

# Overview

The `knowledge` schema is the central metadata repository for OmniBrain's knowledge base.

It manages the metadata, structure, and relationships of all knowledge assets ingested into the platform while keeping binary files, vector embeddings, authentication, and runtime services separated into their respective components.

This schema serves as the relational foundation of the Retrieval-Augmented Generation (RAG) pipeline by organizing documents and their extracted content into a structured, searchable, and scalable hierarchy.

The schema is designed to support enterprise-scale document management while maintaining high data integrity, efficient querying, and clear ownership of every knowledge asset.

---

# Purpose

The purpose of the `knowledge` schema is to:

- Organize enterprise knowledge into logical domains and collections.
- Store metadata for every ingested knowledge asset.
- Maintain relationships between documents and extracted content.
- Support efficient metadata filtering before semantic retrieval.
- Enable citation and provenance tracking for generated responses.
- Provide a consistent metadata layer for the ingestion and retrieval pipelines.

The schema stores only relational metadata and does not manage binary content or vector embeddings.

---

# Scope

The `knowledge` schema manages metadata for the following entities:

- Domains
- Collections
- Documents
- Pages
- Chunks
- Images
- Tables
- Tags
- Document–Tag Mapping

The schema intentionally excludes the following:

| Component | Managed By |
|-----------|------------|
| Original files | MinIO |
| Extracted images | MinIO |
| OCR outputs | MinIO |
| Vector embeddings | Qdrant |
| Similarity search | Qdrant |
| Authentication | `auth` schema |
| Structured datasets | `structured` schema |
| Query history | `query_engine` schema |
| Audit logs | `audit` schema |

This separation allows each component of OmniBrain to use the storage technology best suited to its workload.

---

# Architecture

The `knowledge` schema follows a metadata-first architecture.

```
                User Upload
                     │
                     ▼
            Document Ingestion
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
    PostgreSQL                 MinIO
 (Metadata Layer)          (Binary Storage)
        │
        ▼
     Qdrant
(Vector Embeddings)
        │
        ▼
 Retrieval Pipeline
        │
        ▼
 Generated Response
```

Within PostgreSQL, the metadata hierarchy is organized as follows:

```
Domain
│
└── Collection
      │
      └── Document
            │
            ├── Page
            │     ├── Chunk
            │     ├── Image
            │     └── Table
            │
            └── Document Tag Mapping
                    │
                    └── Tag
```

Each entity has a clearly defined responsibility and is connected through foreign key relationships.

---

# Design Principles

The `knowledge` schema is designed around the following principles.

## Metadata First

Only structured metadata is stored inside PostgreSQL.

Binary files, extracted assets, and embeddings are stored in specialized storage systems.

---

## Separation of Concerns

Each system is responsible only for the data it is optimized to manage.

| System | Responsibility |
|---------|----------------|
| PostgreSQL | Metadata and relationships |
| MinIO | File storage |
| Qdrant | Vector storage and semantic search |

---

## Normalized Relational Design

The schema follows Third Normal Form (3NF) to reduce redundancy, simplify maintenance, and maintain data consistency.

Each table has a single responsibility within the overall metadata model.

---

## UUID-Based Identity

Every primary entity uses UUIDs as primary keys.

UUIDs provide globally unique identifiers that remain stable across distributed systems and future integrations.

---

## Referential Integrity

Relationships between entities are enforced through foreign key constraints.

This prevents orphan records and ensures consistency throughout the metadata hierarchy.

---

## Scalability

The schema is designed to efficiently manage:

- Large document collections
- Millions of pages
- Millions of chunks
- Large numbers of extracted images and tables
- Enterprise-scale metadata queries

Performance is supported through indexing and normalized relationships.

---

## Extensibility

The schema is designed to support future enhancements without major structural changes, including:

- Additional document formats
- Advanced metadata
- AI-generated annotations
- Knowledge graph integration
- Enhanced retrieval capabilities

---

## PostgreSQL as the Source of Truth

PostgreSQL is the authoritative source for all knowledge metadata.

Other services reference PostgreSQL records rather than maintaining independent metadata copies, ensuring consistency across the OmniBrain platform.

---

# Responsibilities

The `knowledge` schema is responsible for managing the complete metadata lifecycle of knowledge assets within OmniBrain.

It acts as the central metadata layer between the document ingestion pipeline, storage systems, and retrieval engine.

## Core Responsibilities

### Knowledge Organization

- Organize knowledge into domains.
- Group related documents into collections.
- Maintain a structured knowledge hierarchy.

### Document Management

- Register every ingested document.
- Store document metadata.
- Track document ownership and status.
- Maintain document lifecycle information.

### Content Organization

- Store page-level metadata.
- Maintain extracted text chunks.
- Track extracted images.
- Track extracted tables.
- Preserve relationships between documents and extracted content.

### Metadata Management

- Store file metadata.
- Maintain storage references.
- Record document properties.
- Support metadata-based filtering.

### Retrieval Support

Provide metadata required by the RAG pipeline, including:

- Document provenance
- Page references
- Chunk hierarchy
- Domain classification
- Collection membership
- Tag-based filtering

### Data Integrity

Maintain data consistency through:

- Foreign key relationships
- Primary key constraints
- Unique constraints
- Check constraints
- Controlled cascading operations

---

# Responsibilities Outside the Knowledge Schema

The `knowledge` schema intentionally stores only metadata. Other responsibilities are handled by dedicated system components.

| Component | Responsibility |
|----------|----------------|
| MinIO | Original documents and extracted binary assets |
| Qdrant | Vector embeddings and semantic search |
| `auth` schema | Authentication and authorization |
| `structured` schema | Structured datasets |
| `query_engine` schema | Query execution and conversation history |
| `audit` schema | Audit logs and activity tracking |

This separation keeps the schema lightweight, scalable, and focused on metadata management.

---

# Core Entity Model

The `knowledge` schema consists of nine relational tables that collectively represent OmniBrain's enterprise knowledge repository.

Each table has a clearly defined responsibility and participates in a normalized relational model.

| Entity | Purpose |
|---------|---------|
| Domains | High-level knowledge categories |
| Collections | Logical grouping of related documents |
| Documents | Metadata for uploaded knowledge assets |
| Pages | Logical pages extracted from documents |
| Chunks | Smallest retrievable text units |
| Images | Metadata of extracted images |
| Tables | Metadata of extracted tables |
| Tags | Reusable classification labels |
| Document Tag Mapping | Many-to-many relationship between documents and tags |

---

# Entity Hierarchy

The metadata hierarchy implemented in the database is shown below.

```
Domain
│
└── Collection
      │
      └── Document
            │
            ├── Page
            │     ├── Chunk
            │     ├── Image
            │     └── Table
            │
            └── Document Tag Mapping
                    │
                    └── Tag
```

This hierarchy represents ownership between entities.

Each child entity depends on its parent and is linked through foreign key constraints.

---

# Entity Overview

## Domain

Represents the highest level of knowledge organization.

Examples:

- Mechanical Engineering
- Artificial Intelligence
- Law
- Medicine
- Finance

A domain can contain multiple collections.

---

## Collection

Represents a logical grouping of related documents within a domain.

Examples:

- Textbooks
- Research Papers
- Technical Manuals
- Lecture Notes

Each collection belongs to one domain.

A collection can contain multiple documents.

---

## Document

Represents a single uploaded knowledge asset.

Supported document types include:

- PDF
- DOCX
- PPTX
- XLSX
- HTML
- Markdown
- Images

Each document belongs to one collection.

---

## Page

Represents a logical page extracted from a document.

Pages preserve document structure and act as the parent for extracted content.

Each page belongs to one document.

---

## Chunk

Represents the smallest retrievable text segment used during semantic retrieval.

Chunks are generated during document processing.

Each chunk belongs to one page.

---

## Image

Represents an image extracted from a document page.

Only metadata is stored within PostgreSQL.

The image itself is stored in MinIO.

---

## Table

Represents a structured table extracted from a document page.

Table metadata is maintained within PostgreSQL.

Structured content may be processed separately by downstream services.

---

## Tag

Represents a reusable label for document classification.

Examples:

- Thermodynamics
- Machine Learning
- FEM
- NLP

Tags improve metadata filtering and retrieval.

---

## Document Tag Mapping

Implements the many-to-many relationship between documents and tags.

This table allows a document to have multiple tags while allowing each tag to be reused across multiple documents.

---

# Relationship Model

The relationships implemented in the schema are summarized below.

| Parent | Child | Relationship |
|---------|-------|--------------|
| Domain | Collection | One-to-Many |
| Collection | Document | One-to-Many |
| Document | Page | One-to-Many |
| Page | Chunk | One-to-Many |
| Page | Image | One-to-Many |
| Page | Table | One-to-Many |
| Document | Tag | Many-to-Many |

---

# Referential Integrity

The schema enforces the following rules:

- Every child record must reference a valid parent.
- Orphan records are not permitted.
- Primary keys are immutable.
- Relationships are maintained using foreign keys.
- Many-to-many relationships are implemented through junction tables.
- Cascading deletes are applied only where ownership exists.

---

# Naming Conventions

The schema follows a consistent naming convention throughout the project.

## Schemas

- Lowercase
- Singular business meaning

Example:

```
knowledge
```

---

## Tables

- Lowercase
- Snake case
- Plural nouns

Examples:

```
domains
collections
documents
pages
chunks
images
tables
tags
document_tag_mapping
```

---

## Columns

- Snake case
- Descriptive names
- Singular identifiers

Examples:

```
domain_id
collection_id
document_id
page_number
chunk_index
created_at
updated_at
```

---

## Keys

| Type | Convention |
|------|------------|
| Primary Key | `<entity>_id` |
| Foreign Key | Parent entity primary key |
| Junction Table | Composite foreign keys |

---

## Timestamp Columns

Timestamp columns follow a consistent naming pattern across the schema.

```
created_at
updated_at
```

These fields support auditing, synchronization, and lifecycle management.

---

## General Conventions

- UUID primary keys
- Snake case naming
- Explicit foreign keys
- Normalized relationships
- Consistent timestamp fields
- PostgreSQL standard data types
- Metadata-first design


---

# Schema Overview

The `knowledge` schema is composed of nine normalized relational tables that collectively manage the metadata of OmniBrain's enterprise knowledge repository.

Each table has a single responsibility and is connected through foreign key relationships to maintain data integrity and support efficient retrieval.

## Schema Structure

| Table | Description |
|--------|-------------|
| `domains` | Defines high-level knowledge categories |
| `collections` | Groups related documents within a domain |
| `documents` | Stores metadata of uploaded knowledge assets |
| `pages` | Stores page-level metadata extracted from documents |
| `chunks` | Stores retrievable text segments |
| `images` | Stores metadata of extracted images |
| `tables` | Stores metadata of extracted tables |
| `tags` | Stores reusable document labels |
| `document_tag_mapping` | Maps documents to tags |

---

## Schema Hierarchy

```
domains
    │
    └── collections
            │
            └── documents
                    │
                    ├── pages
                    │      ├── chunks
                    │      ├── images
                    │      └── tables
                    │
                    └── document_tag_mapping
                              │
                              └── tags
```

The hierarchy reflects the ownership of metadata within the knowledge repository. Parent-child relationships are enforced through foreign keys to maintain referential integrity.

---

# Table Specifications

---

# 1. domains

## Purpose

The `domains` table represents the highest level of organization within the knowledge repository.

A domain groups collections belonging to a common subject area, enabling logical organization and metadata filtering during retrieval.

Examples include:

- Artificial Intelligence
- Mechanical Engineering
- Law
- Finance
- Medicine

---

## Responsibilities

- Organize enterprise knowledge.
- Group related collections.
- Enable domain-based filtering.
- Maintain top-level classification.

---

## Primary Key

| Column | Type |
|---------|------|
| `domain_id` | UUID |

---

## Key Columns

| Column | Description |
|---------|-------------|
| `domain_name` | Unique name of the knowledge domain |
| `description` | Brief description of the domain |
| `created_at` | Record creation timestamp |
| `updated_at` | Last modification timestamp |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Domain → Collections | One-to-Many |

A domain can contain multiple collections, while each collection belongs to exactly one domain.

---

## Constraints

- UUID primary key
- Unique domain name
- Mandatory domain name
- Automatic timestamp tracking

---

## Indexing

Indexes are maintained to support:

- Fast domain lookup
- Efficient joins with collections
- Metadata filtering

---

## Example

```
Mechanical Engineering
    ├── Textbooks
    ├── Research Papers
    └── Laboratory Manuals
```

---

# 2. collections

## Purpose

The `collections` table groups related documents within a specific domain.

Collections provide an intermediate organizational layer that simplifies document management and retrieval.

Examples include:

- Textbooks
- Lecture Notes
- Research Papers
- Technical Manuals
- Company Policies

---

## Responsibilities

- Organize documents within a domain.
- Support collection-level categorization.
- Improve metadata filtering.
- Maintain logical grouping of knowledge assets.

---

## Primary Key

| Column | Type |
|---------|------|
| `collection_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `domain_id` | `domains.domain_id` |

---

## Key Columns

| Column | Description |
|---------|-------------|
| `collection_name` | Name of the collection |
| `description` | Collection description |
| `domain_id` | Parent domain |
| `created_at` | Record creation timestamp |
| `updated_at` | Last modification timestamp |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Domain → Collection | One-to-Many |
| Collection → Documents | One-to-Many |

---

## Constraints

- UUID primary key
- Mandatory parent domain
- Foreign key enforcement
- Automatic timestamp tracking

---

## Indexing

Indexes support:

- Domain-based filtering
- Collection lookup
- Join performance

---

## Example

```
Domain:
Mechanical Engineering

Collections:
• Textbooks
• Research Papers
• Lecture Notes
```

---

# 3. documents

## Purpose

The `documents` table stores the primary metadata for every knowledge asset ingested into OmniBrain.

Each uploaded document is represented by a single record containing its identity, storage metadata, processing information, and current status.

This table acts as the central entity of the `knowledge` schema.

---

## Responsibilities

- Register uploaded documents.
- Store document metadata.
- Maintain storage references.
- Track ingestion and processing status.
- Preserve document properties.
- Link documents to collections.
- Act as the parent entity for extracted content.

---

## Primary Key

| Column | Type |
|---------|------|
| `document_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `collection_id` | `collections.collection_id` |

---

## Metadata Categories

The table stores metadata related to:

### Identification

- Document ID
- Document title
- Original filename

### File Information

- File type
- MIME type
- File extension
- File size
- File checksum

### Storage

- Storage location
- Object path
- Storage reference

### Processing

- Processing status
- Ingestion status
- Extraction status
- Language information

### Ownership

- Parent collection
- Created timestamp
- Updated timestamp

---

## Relationships

| Relationship | Type |
|--------------|------|
| Collection → Document | One-to-Many |
| Document → Pages | One-to-Many |
| Document → Tags | Many-to-Many |

The document serves as the parent entity for all extracted page-level metadata.

---

## Constraints

- UUID primary key
- Mandatory parent collection
- Foreign key enforcement
- Metadata validation through SQL constraints
- Automatic timestamp tracking

---

## Indexing

Indexes are maintained to optimize:

- Document lookup
- Collection filtering
- Processing status queries
- File metadata search
- Join performance

---

## Example

```
Document
│
├── Title:
│   Theory of Machines
│
├── Collection:
│   Mechanical Engineering → Textbooks
│
├── File Type:
│   PDF
│
├── Status:
│   Processed
│
└── Storage:
    MinIO
```

---

## Notes

- Binary document contents are **not stored** in PostgreSQL.
- The document record stores only metadata required by the ingestion and retrieval pipelines.
- Extracted pages, chunks, images, and tables reference the document through foreign key relationships, enabling efficient traversal across the knowledge hierarchy.


---

# 4. pages

## Purpose

The `pages` table stores metadata for each logical page extracted from a document.

It preserves the document structure and acts as the parent entity for all page-level content, including text chunks, images, and tables.

---

## Responsibilities

- Maintain page order.
- Store page metadata.
- Support page-level citations.
- Link extracted content to its source page.
- Preserve document hierarchy.

---

## Primary Key

| Column | Type |
|---------|------|
| `page_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `document_id` | `documents.document_id` |

---

## Metadata Categories

The table stores metadata related to:

### Page Information

- Page number
- Page label
- Page dimensions
- Rotation
- Processing metadata

### OCR Information

- OCR status
- OCR language (if applicable)

### Ownership

- Parent document
- Created timestamp
- Updated timestamp

---

## Relationships

| Relationship | Type |
|--------------|------|
| Document → Pages | One-to-Many |
| Page → Chunks | One-to-Many |
| Page → Images | One-to-Many |
| Page → Tables | One-to-Many |

Each page belongs to exactly one document.

---

## Constraints

- UUID primary key
- Mandatory parent document
- Foreign key enforcement
- Valid page numbering
- Automatic timestamp tracking

---

## Indexing

Indexes support:

- Page lookup
- Citation generation
- Sequential page retrieval
- Join performance

---

## Example

```
Theory_of_Machines.pdf

Page 1
Page 2
Page 3
...
Page 520
```

---

## Notes

- Pages store only metadata.
- Actual page images or rendered previews are stored externally.
- Every extracted object is linked back to its source page.

---

# 5. chunks

## Purpose

The `chunks` table stores the smallest retrievable text units generated during document processing.

Chunks are the primary input for semantic retrieval and Retrieval-Augmented Generation (RAG).

---

## Responsibilities

- Store processed text.
- Preserve chunk order.
- Support semantic retrieval.
- Maintain references to source pages.
- Enable citation generation.

---

## Primary Key

| Column | Type |
|---------|------|
| `chunk_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `page_id` | `pages.page_id` |

---

## Metadata Categories

The table stores metadata related to:

### Chunk Information

- Chunk index
- Chunk text
- Chunk type
- Character boundaries

### Retrieval Metadata

- Parent page
- Processing metadata

### Ownership

- Created timestamp
- Updated timestamp

---

## Relationships

| Relationship | Type |
|--------------|------|
| Page → Chunks | One-to-Many |

Each chunk belongs to exactly one page.

---

## Constraints

- UUID primary key
- Mandatory parent page
- Foreign key enforcement
- Valid chunk ordering
- Automatic timestamp tracking

---

## Indexing

Indexes support:

- Chunk retrieval
- Semantic search mapping
- Citation lookup
- Join performance

---

## Example

```
Page 18

Chunk 1
Chunk 2
Chunk 3
Chunk 4
```

---

## Notes

- Embedding vectors are **not** stored in PostgreSQL.
- Vector embeddings are stored in Qdrant and reference the corresponding chunk metadata.

---

# 6. images

## Purpose

The `images` table stores metadata for images extracted from document pages.

Only descriptive metadata is maintained in PostgreSQL, while image files are stored in MinIO.

---

## Responsibilities

- Track extracted images.
- Store image metadata.
- Maintain storage references.
- Support multimodal retrieval.

---

## Primary Key

| Column | Type |
|---------|------|
| `image_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `page_id` | `pages.page_id` |

---

## Metadata Categories

The table stores metadata related to:

### Image Information

- Image index
- Image format
- Dimensions
- File size

### Storage

- Storage path
- Object reference

### Ownership

- Parent page
- Created timestamp
- Updated timestamp

---

## Relationships

| Relationship | Type |
|--------------|------|
| Page → Images | One-to-Many |

Each image belongs to exactly one page.

---

## Constraints

- UUID primary key
- Mandatory parent page
- Foreign key enforcement
- Automatic timestamp tracking

---

## Indexing

Indexes support:

- Image lookup
- Page-based retrieval
- Metadata filtering
- Join performance

---

## Example

```
Document

Page 12

├── Figure 1
├── Figure 2
└── Figure 3
```

---

## Notes

- Binary image files are stored in MinIO.
- PostgreSQL stores only metadata required for retrieval and management.

---

# 7. tables

## Purpose

The `tables` table stores metadata for structured tables extracted from document pages.

It preserves the relationship between extracted tabular content and its original location within the document.

---

## Responsibilities

- Track extracted tables.
- Store table metadata.
- Maintain storage references.
- Support future structured retrieval.

---

## Primary Key

| Column | Type |
|---------|------|
| `table_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `page_id` | `pages.page_id` |

---

## Metadata Categories

The table stores metadata related to:

### Table Information

- Table index
- Table title
- Extraction metadata

### Storage

- Storage path
- Object reference

### Ownership

- Parent page
- Created timestamp
- Updated timestamp

---

## Relationships

| Relationship | Type |
|--------------|------|
| Page → Tables | One-to-Many |

Each table belongs to exactly one page.

---

## Constraints

- UUID primary key
- Mandatory parent page
- Foreign key enforcement
- Automatic timestamp tracking

---

## Indexing

Indexes support:

- Table lookup
- Page-based retrieval
- Metadata filtering
- Join performance

---

## Example

```
Page 56

Table 1
Table 2
```

---

## Notes

- PostgreSQL stores only table metadata.
- Structured table data can be processed by downstream services for analytics, retrieval, or future database integration.
- Each extracted table remains linked to its original source page for traceability and citation.




---

# 8. tags

## Purpose

The `tags` table stores reusable labels used to classify and organize documents within the knowledge repository.

Tags improve metadata filtering and enable more targeted document retrieval without duplicating information across multiple records.

---

## Responsibilities

- Store reusable classification labels.
- Support metadata filtering.
- Enable document categorization.
- Improve search and retrieval.

---

## Primary Key

| Column | Type |
|---------|------|
| `tag_id` | UUID |

---

## Key Columns

| Column | Description |
|---------|-------------|
| `tag_name` | Unique tag name |
| `description` | Optional tag description |
| `created_at` | Record creation timestamp |
| `updated_at` | Last modification timestamp |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Tag ↔ Documents | Many-to-Many |

A tag can be associated with multiple documents, and a document can have multiple tags.

---

## Constraints

- UUID primary key
- Unique tag name
- Mandatory tag name
- Automatic timestamp tracking

---

## Indexing

Indexes support:

- Fast tag lookup
- Metadata filtering
- Document-tag joins

---

## Example

```
Tags

• Thermodynamics
• Machine Learning
• FEM
• NLP
• Computer Vision
```

---

## Notes

- Tags are reusable across the entire knowledge repository.
- Tags contain only classification metadata and do not own any document content.

---

# 9. document_tag_mapping

## Purpose

The `document_tag_mapping` table implements the many-to-many relationship between documents and tags.

Instead of storing multiple tags within the `documents` table, this junction table maintains normalized associations between documents and reusable tags.

---

## Responsibilities

- Associate documents with tags.
- Eliminate data duplication.
- Maintain normalized relationships.
- Support efficient metadata filtering.

---

## Primary Key

Composite Primary Key

| Column |
|---------|
| `document_id` |
| `tag_id` |

---

## Foreign Keys

| Column | References |
|---------|------------|
| `document_id` | `documents.document_id` |
| `tag_id` | `tags.tag_id` |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Document → Tag | Many-to-Many |

Each mapping record represents a single association between one document and one tag.

---

## Constraints

- Composite primary key
- Mandatory document reference
- Mandatory tag reference
- Foreign key enforcement
- Duplicate mappings are not permitted

---

## Indexing

Indexes support:

- Tag-based document retrieval
- Document-based tag retrieval
- Join optimization

---

## Example

```
Theory_of_Machines.pdf

↓

Tags

• Mechanical Engineering
• Dynamics
• Kinematics
• Gear Design
```

---

## Notes

- This table stores relationships only.
- No document metadata or tag metadata is duplicated.

---

# Constraints

The `knowledge` schema enforces constraints to maintain data integrity and ensure consistency across all metadata.

## Primary Keys

Every primary entity uses a UUID-based primary key.

| Table | Primary Key |
|--------|-------------|
| domains | `domain_id` |
| collections | `collection_id` |
| documents | `document_id` |
| pages | `page_id` |
| chunks | `chunk_id` |
| images | `image_id` |
| tables | `table_id` |
| tags | `tag_id` |

The `document_tag_mapping` table uses a composite primary key.

---

## Foreign Keys

Foreign key constraints maintain ownership relationships throughout the schema.

| Parent | Child |
|---------|-------|
| domains | collections |
| collections | documents |
| documents | pages |
| pages | chunks |
| pages | images |
| pages | tables |
| documents | document_tag_mapping |
| tags | document_tag_mapping |

---

## Unique Constraints

Unique constraints prevent duplicate metadata where uniqueness is required.

Examples include:

- Domain names
- Tag names
- Composite document-tag mappings

---

## Check Constraints

Check constraints validate data before it is stored.

These constraints ensure that values such as page numbers, ordering fields, status values, and other controlled metadata remain valid.

---

## NOT NULL Constraints

Mandatory fields are enforced using `NOT NULL` constraints to ensure essential metadata is always available.

Examples include:

- Primary keys
- Foreign keys
- Required names
- Required identifiers

---

## Default Values

Common metadata fields use default values where appropriate.

Examples include:

- UUID generation
- Creation timestamps
- Update timestamps
- Default processing states

---

## Referential Integrity

The schema enforces referential integrity through foreign key constraints.

This ensures:

- Child records always reference valid parent records.
- Orphan records cannot exist.
- Metadata remains consistent across the knowledge hierarchy.

---

# Indexing Strategy

Indexes are used to improve query performance while maintaining efficient metadata retrieval.

The indexing strategy focuses on common access patterns used throughout the OmniBrain ingestion and retrieval pipelines.

---

## Primary Indexes

Every table is indexed through its primary key.

These indexes support:

- Fast record lookup
- Foreign key joins
- Relationship traversal

---

## Foreign Key Indexes

Indexes are maintained on foreign key columns to improve join performance.

Examples include:

- `domain_id`
- `collection_id`
- `document_id`
- `page_id`
- `tag_id`

These indexes optimize hierarchical navigation across the schema.

---

## Metadata Indexes

Additional indexes support efficient filtering based on document metadata.

Typical query patterns include:

- Domain filtering
- Collection filtering
- Document lookup
- Page retrieval
- Processing status
- Tag filtering

---

## Composite Indexes

Composite indexes are used where queries frequently involve multiple related columns.

This reduces lookup time and improves join efficiency for common retrieval operations.

---

## Performance Considerations

The indexing strategy is designed to support:

- Fast document ingestion
- Efficient metadata filtering
- Low-latency joins
- Scalable retrieval
- Enterprise-scale knowledge repositories

Indexes are chosen to balance read performance with insertion and update costs.



---

# Referential Integrity

The `knowledge` schema enforces referential integrity using foreign key constraints to ensure that all metadata remains consistent throughout the knowledge hierarchy.

Every child entity must reference a valid parent entity, preventing orphan records and maintaining relationships between knowledge assets.

## Relationship Summary

| Parent Table | Child Table | Relationship |
|--------------|-------------|--------------|
| `domains` | `collections` | One-to-Many |
| `collections` | `documents` | One-to-Many |
| `documents` | `pages` | One-to-Many |
| `pages` | `chunks` | One-to-Many |
| `pages` | `images` | One-to-Many |
| `pages` | `tables` | One-to-Many |
| `documents` | `document_tag_mapping` | One-to-Many |
| `tags` | `document_tag_mapping` | One-to-Many |

---

## Integrity Rules

The schema follows these principles:

- Every child record must reference an existing parent record.
- Parent-child relationships are enforced using foreign keys.
- Orphan records are not permitted.
- Primary keys remain immutable.
- Metadata relationships remain consistent throughout the document lifecycle.

These rules ensure reliable metadata traversal across the OmniBrain knowledge repository.

---

# Cascade Policies

Cascade policies define how related records are handled during deletion.

Ownership relationships use cascading deletes so that dependent metadata is automatically removed when its parent no longer exists.

## Cascading Relationships

| Parent | Child | Delete Policy |
|---------|-------|---------------|
| Documents | Pages | Cascade |
| Pages | Chunks | Cascade |
| Pages | Images | Cascade |
| Pages | Tables | Cascade |
| Documents | Document Tag Mapping | Cascade |
| Tags | Document Tag Mapping | Cascade |

---

## Restricted Relationships

Higher-level organizational entities are protected from accidental deletion.

| Parent | Child | Delete Policy |
|---------|-------|---------------|
| Domains | Collections | Restricted |
| Collections | Documents | Restricted |

A domain or collection cannot be removed while dependent records still exist.

---

## Benefits

This strategy ensures:

- No orphan metadata
- Consistent hierarchy
- Automatic cleanup of dependent records
- Protection against accidental deletion of large knowledge repositories

---

# Storage Integration

The `knowledge` schema stores only metadata.

Actual document content and machine learning artifacts are managed by specialized storage systems.

## Storage Architecture

| Component | Responsibility |
|-----------|----------------|
| PostgreSQL (`knowledge`) | Metadata and relationships |
| MinIO | Original documents and extracted binary assets |
| Qdrant | Vector embeddings and semantic search |

---

## PostgreSQL

Stores:

- Domains
- Collections
- Document metadata
- Page metadata
- Chunk metadata
- Image metadata
- Table metadata
- Tags
- Entity relationships

---

## MinIO

Stores:

- Original uploaded documents
- Extracted images
- Rendered previews
- OCR output files
- Other binary assets

The `knowledge` schema stores only references to these files.

---

## Qdrant

Stores:

- Vector embeddings
- Similarity indexes

Embeddings are generated from document chunks and linked back to PostgreSQL metadata during retrieval.

---

## Retrieval Flow

```
User Query
      │
      ▼
Metadata Filtering (PostgreSQL)
      │
      ▼
Semantic Search (Qdrant)
      │
      ▼
Retrieve Binary Assets (MinIO)
      │
      ▼
LLM Response Generation
```

This architecture keeps each storage system focused on the workload it is designed to handle.

---

# Performance Notes

The `knowledge` schema is designed to efficiently support document ingestion, metadata management, and retrieval operations.

## Design Considerations

- Normalized relational structure
- UUID primary keys
- Indexed foreign keys
- Optimized join relationships
- Metadata-first architecture

---

## Optimized Operations

The schema supports efficient execution of:

- Domain-based filtering
- Collection-based filtering
- Document lookup
- Page traversal
- Chunk retrieval
- Tag-based search
- Metadata joins

---

## Scalability

The schema is designed to support:

- Large knowledge repositories
- Millions of documents
- Millions of pages
- Millions of chunks
- Enterprise-scale retrieval workloads

Performance improvements are achieved through indexing and normalized relationships rather than data duplication.

---

# Future Extensions

The current schema is designed to support future enhancements without requiring major structural changes.

Potential extensions include:

- Additional document formats
- AI-generated metadata
- Automatic document summarization
- Knowledge graph integration
- Advanced metadata enrichment
- Enhanced retrieval analytics
- Multi-language metadata
- Document-level access policies
- Version management
- Cross-document relationships

These features can be introduced while preserving the existing schema design.

---

# Appendix

## Table Summary

| Table | Purpose |
|--------|---------|
| `domains` | Organizes knowledge into high-level categories |
| `collections` | Groups related documents within a domain |
| `documents` | Stores metadata for uploaded knowledge assets |
| `pages` | Stores page-level metadata |
| `chunks` | Stores retrievable text segments |
| `images` | Stores metadata of extracted images |
| `tables` | Stores metadata of extracted tables |
| `tags` | Stores reusable classification labels |
| `document_tag_mapping` | Maps documents to tags |

---

## Complete Entity Hierarchy

```
domains
│
└── collections
      │
      └── documents
            │
            ├── pages
            │     ├── chunks
            │     ├── images
            │     └── tables
            │
            └── document_tag_mapping
                    │
                    └── tags
```

---

## Schema Summary

The `knowledge` schema serves as the authoritative metadata repository for OmniBrain's enterprise knowledge base.

It organizes knowledge assets into a structured hierarchy, maintains relationships between documents and extracted content, and provides the metadata required by the ingestion and Retrieval-Augmented Generation (RAG) pipelines.

Binary files remain in MinIO, vector embeddings remain in Qdrant, and PostgreSQL acts as the single source of truth for all relational metadata.

The schema follows a normalized design with UUID-based identifiers, foreign key constraints, and indexed relationships to ensure scalability, maintainability, and reliable retrieval across the OmniBrain platform.