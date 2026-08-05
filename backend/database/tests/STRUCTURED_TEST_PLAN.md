# Structured Schema Test Plan

**Project:** OmniBrain – Enterprise Multi-Modal RAG Platform

**Module:** Database

**Schema:** `structured`

**SQL File:** `05_structured.sql`

---

# Overview

This document defines the testing strategy for the **structured** schema.

The objective is to verify that the schema has been created correctly, maintains referential integrity, enforces database constraints, and behaves as expected during metadata management operations.

Testing is performed using SQL validation scripts located in:

```
backend/database/tests/structured_test.sql
```

---

# Test Objectives

The structured schema should be validated to ensure:

- Tables are created successfully.
- Relationships are established correctly.
- Primary keys are enforced.
- Foreign key constraints maintain integrity.
- Unique constraints prevent duplicate metadata.
- Check constraints validate allowed values.
- Default values are applied correctly.
- Indexes support efficient metadata retrieval.
- Metadata hierarchy remains consistent.

---

# Test Environment

| Component | Value |
|----------|-------|
| Database | PostgreSQL 17+ |
| Schema | structured |
| SQL Script | 05_structured.sql |
| Test Script | structured_test.sql |

---

# Scope

The following database objects are covered.

| Component | Tested |
|-----------|--------|
| Data Sources | ✅ |
| Datasets | ✅ |
| Dataset Tables | ✅ |
| Dataset Columns | ✅ |
| Dataset Relationships | ✅ |
| Dataset Relationship Columns | ✅ |
| Dataset Statistics | ✅ |
| Table Statistics | ✅ |
| Column Statistics | ✅ |
| Tags | ✅ |
| Resource Tags | ✅ |
| Dataset Refresh History | ✅ |

---

# Test Categories

## 1. Schema Validation

Verify:

- Schema exists.
- Tables exist.
- Required columns exist.
- Primary keys exist.

Expected Result:

All database objects are created successfully.

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

- Data Sources → Datasets
- Datasets → Dataset Tables
- Dataset Tables → Dataset Columns
- Dataset Relationships → Relationship Columns
- Datasets → Dataset Statistics
- Dataset Tables → Table Statistics
- Dataset Columns → Column Statistics
- Datasets → Dataset Refresh History
- Tags → Resource Tags

Expected Result:

Invalid references must be rejected.

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

## 5. Relationship Validation

Verify:

- Parent-child hierarchy
- Relationship traversal
- Junction table mappings
- Metadata consistency

Expected Result:

No orphan metadata records exist.

---

## 6. Metadata Validation

Verify insertion and retrieval of:

- Data source metadata
- Dataset metadata
- Table metadata
- Column metadata
- Statistical metadata
- Refresh history
- Resource tags

Expected Result:

Metadata is stored and retrieved correctly.

---

## 7. Statistics Validation

Verify:

- Dataset statistics
- Table statistics
- Column statistics

Expected Result:

Statistics reference valid parent entities.

---

## 8. Tag Validation

Verify:

- Tag creation
- Resource-tag mapping
- Duplicate prevention

Expected Result:

Tags remain reusable and normalized.

---

## 9. Refresh History Validation

Verify:

- Refresh records
- Parent dataset references
- Refresh status metadata

Expected Result:

Refresh history remains linked to valid datasets.

---

## 10. Cascade Behaviour

Verify cascading operations for dependent entities.

Expected Result:

Dependent metadata is removed only where cascading relationships are defined.

---

## 11. Index Validation

Verify indexes exist on:

- Primary keys
- Foreign keys
- Frequently queried metadata columns

Expected Result:

Metadata retrieval remains efficient.

---

## 12. Data Integrity Validation

Verify that:

- Duplicate metadata cannot be inserted.
- Invalid relationships are rejected.
- Metadata hierarchy remains consistent.

Expected Result:

Database integrity is preserved.

---

# Edge Case Testing

The following scenarios should be validated.

| Scenario | Expected Result |
|----------|-----------------|
| Duplicate UUID | Rejected |
| Invalid foreign key | Rejected |
| Duplicate tag mapping | Rejected |
| Missing required field | Rejected |
| Invalid status value | Rejected |
| Invalid relationship | Rejected |
| Parent deletion | Cascade or Restrict according to schema |

---

# Performance Validation

The following operations should complete successfully on large metadata repositories.

- Dataset lookup
- Table lookup
- Column lookup
- Relationship traversal
- Tag filtering
- Statistics retrieval
- Refresh history retrieval

Performance should remain acceptable through indexing and normalized relationships.

---

# Success Criteria

Testing is considered successful when:

- All schema objects are created successfully.
- All constraints behave as expected.
- Referential integrity is maintained.
- Invalid metadata is rejected.
- Valid metadata is stored successfully.
- Indexes support efficient retrieval.
- No orphan records are produced.
- All SQL validation scripts complete without unexpected errors.

---

# Related Files

| File | Purpose |
|------|---------|
| `05_structured.sql` | Structured schema implementation |
| `structured_test.sql` | SQL validation script |
| `STRUCTURED_SCHEMA_SPEC.md` | Schema documentation |
| `DATABASE_STANDARDS.md` | Database development standards |

---

# Summary

This test plan validates the correctness, integrity, and reliability of the **structured** schema.

Successful completion of all tests confirms that the schema correctly supports structured metadata management within the OmniBrain platform and provides a stable foundation for future database development.