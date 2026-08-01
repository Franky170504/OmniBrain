# Knowledge Schema Test Plan

**Project:** OmniBrain – Enterprise Multi-Modal RAG Platform

**Module:** Database

**Schema:** `knowledge`

**SQL File:** `03_knowledge.sql`

---

# Overview

This document defines the testing strategy for the **knowledge** schema.

The objective is to verify that the schema is created correctly, maintains referential integrity, enforces database constraints, and supports reliable metadata management for unstructured knowledge assets.

Testing is performed using SQL validation scripts located in:

```
backend/database/tests/knowledge_test.sql
```

---

# Test Objectives

The knowledge schema should be validated to ensure:

- Schema objects are created successfully.
- Tables are created correctly.
- Primary keys are enforced.
- Foreign key relationships are maintained.
- Unique constraints prevent duplicate metadata.
- Check constraints validate allowed values.
- Triggers execute correctly.
- Default values are assigned properly.
- Indexes are created successfully.
- Metadata hierarchy remains consistent.

---

# Test Environment

| Component | Value |
|----------|-------|
| Database | PostgreSQL 17+ |
| Schema | knowledge |
| SQL Script | 03_knowledge.sql |
| Test Script | knowledge_test.sql |

---

# Scope

The following database objects are covered.

| Component | Tested |
|-----------|--------|
| Domains | ✅ |
| Collections | ✅ |
| Documents | ✅ |
| Pages | ✅ |
| Chunks | ✅ |
| Images | ✅ |
| Tables | ✅ |
| Tags | ✅ |
| Document Tag Mapping | ✅ |

---

# Test Categories

## 1. Schema Validation

Verify:

- Schema exists.
- Tables exist.
- Required columns exist.
- Primary keys exist.

Expected Result:

All schema objects are created successfully.

---

## 2. Primary Key Validation

Verify:

- UUID primary keys are generated correctly.
- Duplicate primary keys are rejected.

Expected Result:

Every record has a unique primary key.

---

## 3. Foreign Key Validation

Verify relationships between:

- Domains → Collections
- Collections → Documents
- Documents → Pages
- Pages → Chunks
- Pages → Images
- Pages → Tables
- Documents → Document Tag Mapping
- Tags → Document Tag Mapping

Expected Result:

Invalid references are rejected.

---

## 4. Constraint Validation

Validate:

- NOT NULL constraints
- UNIQUE constraints
- CHECK constraints
- Foreign key constraints

Expected Result:

Only valid metadata can be inserted.

---

## 5. Metadata Hierarchy Validation

Verify the hierarchy:

```
Domain
    ↓
Collection
    ↓
Document
    ↓
Page
    ├── Chunk
    ├── Image
    └── Table
```

Expected Result:

The hierarchy remains consistent with no orphan records.

---

## 6. Document Metadata Validation

Verify insertion and retrieval of:

- Domain metadata
- Collection metadata
- Document metadata

Expected Result:

Metadata is stored and retrieved successfully.

---

## 7. Page Metadata Validation

Verify:

- Page creation
- Page ordering
- Parent document references

Expected Result:

Pages remain correctly associated with their parent document.

---

## 8. Chunk Validation

Verify:

- Chunk insertion
- Chunk ordering
- Parent page references

Expected Result:

Chunks remain linked to valid pages.

---

## 9. Image Metadata Validation

Verify:

- Image metadata insertion
- Parent page references
- Metadata retrieval

Expected Result:

Image metadata remains consistent.

---

## 10. Table Metadata Validation

Verify:

- Table metadata insertion
- Parent page references
- Metadata retrieval

Expected Result:

Extracted table metadata is stored correctly.

---

## 11. Tag Validation

Verify:

- Tag creation
- Document-tag mapping
- Duplicate prevention

Expected Result:

Tags remain normalized and reusable.

---

## 12. Trigger Validation

Verify that automatic timestamp triggers execute correctly.

Expected Result:

`updated_at` is refreshed automatically during record updates.

---

## 13. Index Validation

Verify indexes exist for:

- Primary keys
- Foreign keys
- Frequently queried metadata columns

Expected Result:

Indexes support efficient metadata retrieval.

---

## 14. Data Integrity Validation

Verify:

- Duplicate metadata is rejected.
- Invalid foreign keys are rejected.
- Orphan records cannot exist.
- Metadata relationships remain consistent.

Expected Result:

Database integrity is preserved.

---

# Edge Case Testing

The following scenarios should be validated.

| Scenario | Expected Result |
|----------|-----------------|
| Duplicate UUID | Rejected |
| Duplicate tag | Rejected |
| Invalid foreign key | Rejected |
| Missing required field | Rejected |
| Invalid hierarchy | Rejected |
| Parent deletion | Cascade or Restrict according to schema |

---

# Performance Validation

Validate the performance of:

- Document lookup
- Page lookup
- Chunk retrieval
- Image retrieval
- Table retrieval
- Tag filtering
- Metadata traversal

Performance should remain efficient through proper indexing.

---

# Success Criteria

Testing is considered successful when:

- All tables are created successfully.
- All constraints behave correctly.
- Referential integrity is maintained.
- Valid metadata is accepted.
- Invalid metadata is rejected.
- Trigger execution is successful.
- Indexes exist and function correctly.
- No orphan records are produced.

---

# Related Files

| File | Purpose |
|------|---------|
| `03_knowledge.sql` | Knowledge schema implementation |
| `knowledge_test.sql` | SQL validation script |
| `KNOWLEDGE_SCHEMA_SPEC.md` | Knowledge schema documentation |
| `DATABASE_STANDARDS.md` | Database development standards |

---

# Summary

This test plan validates the correctness, integrity, and reliability of the **knowledge** schema.

Successful completion of all tests confirms that the schema correctly supports metadata management for unstructured knowledge assets while maintaining referential integrity, consistency, and scalability within the OmniBrain platform.