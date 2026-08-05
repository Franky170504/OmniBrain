# OmniBrain Database Standards
**Project:** OmniBrain – Enterprise Agentic Multi-Modal RAG System

**Version:** 1.0

**Owner:** Database Engineering Team

**Status:** Approved for Initial Development

---

# 1. Purpose

This document defines the database engineering standards for OmniBrain.

Every SQL script, migration, table, view, function, trigger, and index must follow these standards.

These conventions ensure:

- Consistency
- Maintainability
- Scalability
- Production readiness
- Easy onboarding for future developers

---

# 2. Database Technology

Database Engine

- PostgreSQL 16+

Extensions

- pgcrypto
- pg_trgm
- unaccent

Future Integrations

- Qdrant
- MinIO
- Redis
- Neo4j

---

# 3. Database Architecture

The PostgreSQL database stores only relational metadata.

PostgreSQL DOES NOT store

- vector embeddings
- PDFs
- images
- videos
- audio

Responsibilities

✓ Metadata

✓ Authentication

✓ Knowledge hierarchy

✓ Structured data metadata

✓ Query history

✓ Audit

✓ Feedback

---

# 4. Schema Organization

The database is divided into five logical schemas.

## auth

Stores

- users
- roles

Responsible for authentication and authorization.

---

## knowledge

Stores

- documents
- versions
- pages
- chunks
- images
- tables
- collections
- tags
- storage metadata

Responsible for the complete knowledge base.

---

## structured

Stores metadata describing structured business data.

Examples

- registered databases

- tables

- columns

Used by the Text-to-SQL system.

---

## query_engine

Stores

- queries

- retrieved context

- context items

- feedback

- traces

Responsible for retrieval history and observability.

---

## audit

Stores immutable audit logs.

---

# 5. Naming Convention

Everything uses snake_case.

Correct

users

document_versions

storage_objects

retrieved_context

created_at

updated_at

Incorrect

Users

DocumentVersion

storageObject

CreatedAt

---

# 6. Table Naming

Plural nouns.

Examples

users

documents

pages

chunks

images

collections

queries

feedback

---

# 7. Column Naming

Primary Key

<table>_id

Examples

user_id

document_id

page_id

chunk_id

Foreign Keys follow the same rule.

---

# 8. UUID Policy

Every primary key is UUID.

Default

gen_random_uuid()

Integer primary keys are prohibited unless justified.

---

# 9. Required Columns

Every major table should contain

created_at TIMESTAMP

updated_at TIMESTAMP

Optional

deleted_at TIMESTAMP

---

# 10. Soft Delete Policy

Use deleted_at only when records may require recovery.

Recommended

documents

collections

users

Do NOT use soft delete for

audit logs

query traces

context items

These are immutable.

---

# 11. Timestamp Policy

All timestamps stored in UTC.

Never store local time.

---

# 12. Constraints

Every table must define

PRIMARY KEY

NOT NULL where applicable

FOREIGN KEY constraints

CHECK constraints

UNIQUE constraints where required

Examples

rating BETWEEN 1 AND 5

version_number > 0

token_count >= 0

---

# 13. Foreign Key Policy

Always explicitly define

ON DELETE

ON UPDATE

Preferred

ON UPDATE CASCADE

Deletion policy depends on entity lifecycle.

---

# 14. Index Policy

Every foreign key receives an index.

Additional indexes

B-tree

GIN

BRIN

Composite

Only create indexes for actual query patterns.

---

# 15. Trigger Naming

Format

trg_<purpose>

Examples

trg_update_timestamp

trg_log_query

---

# 16. Function Naming

Format

fn_<action>

Examples

fn_create_document

fn_archive_document

fn_record_feedback

---

# 17. View Naming

Format

vw_<name>

Examples

vw_document_summary

vw_recent_queries

vw_active_users

---

# 18. Migration Rules

Never edit an executed migration.

Create a new migration instead.

Migration filenames must be ordered.

Example

0001_extensions.sql

0002_schemas.sql

0003_auth.sql

---

# 19. SQL Formatting

Keywords uppercase

Identifiers lowercase

One column per line

One constraint per line

Indentation

4 spaces

Maximum line length

100 characters

---

# 20. Comments

Every SQL file begins with

Purpose

Author

Date

Dependencies

Every complex query must include comments.

---

# 21. Documentation

Every table must have

Purpose

Relationships

Indexes

Constraints

Referenced by

---

# 22. Security Standards

Passwords are never stored.

Only password hashes.

No sensitive secrets stored in PostgreSQL.

Prepared statements must always be used by backend services.

---

# 23. Performance Standards

Avoid SELECT *

Return only required columns.

Batch inserts where possible.

Avoid unnecessary joins.

Always analyze execution plans before adding indexes.

---

# 24. Backup Strategy

Daily backups

Point-in-time recovery enabled

Weekly integrity verification

---

# 25. Production Principles

The database is the single source of truth for metadata.

Qdrant stores vectors.

MinIO stores files.

Redis stores cache.

Neo4j stores graph relationships.

Responsibilities must never overlap.

---

# 26. Change Management

Every database change must include

Updated documentation

Migration

Rollback strategy

Testing

Code review

---

# Approval

This document is the official database engineering standard for OmniBrain.

All future database work must comply with these standards.