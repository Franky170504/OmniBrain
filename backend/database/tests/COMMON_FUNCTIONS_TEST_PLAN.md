# Common Functions Test Plan

**Project:** OmniBrain – Enterprise Multi-Modal RAG Platform

**Module:** Database

**Schema:** `common`

**SQL File:** `04_common_functions.sql`

---

# Overview

This document defines the testing strategy for the reusable PostgreSQL functions implemented in the `common` schema.

These functions provide shared functionality used across multiple database schemas and ensure consistent behaviour throughout the OmniBrain database module.

Testing verifies that every function behaves correctly under normal and exceptional conditions while maintaining database integrity.

SQL validation is performed using:

```
backend/database/tests/common_functions_test.sql
```

---

# Test Objectives

The objectives of this test plan are to verify that:

- Database functions are created successfully.
- Functions return the expected results.
- Trigger functions behave correctly.
- Invalid inputs are rejected.
- Error messages are meaningful.
- Referential integrity is preserved.
- Functions remain reusable across database schemas.

---

# Test Environment

| Component | Value |
|----------|-------|
| Database | PostgreSQL 17+ |
| Schema | common |
| SQL Script | 04_common_functions.sql |
| Test Script | common_functions_test.sql |

---

# Functions Covered

| Function | Type | Purpose |
|----------|------|---------|
| `common.set_updated_at()` | Trigger Function | Automatically updates the `updated_at` timestamp before row modification. |
| `common.validate_resource_tag()` | Trigger Function | Validates that a tagged structured resource exists before allowing tag assignment. |

---

# Function Testing

---

# 1. common.set_updated_at()

## Purpose

Automatically updates the `updated_at` column whenever an existing row is modified.

This function provides consistent timestamp management across database tables using trigger-based automation.

---

## Test Objectives

Verify that:

- Function is created successfully.
- Trigger executes before `UPDATE`.
- `updated_at` is automatically refreshed.
- Other column values remain unchanged.
- Function can be attached to supported tables.

---

## Validation

The following scenarios should be tested.

| Test | Expected Result |
|------|-----------------|
| Function exists | Success |
| Trigger executes | Success |
| UPDATE changes timestamp | Success |
| INSERT unaffected | Success |
| Multiple updates refresh timestamp | Success |

---

## Edge Cases

Validate:

- Updating multiple rows.
- Updating the same row repeatedly.
- Updating rows without changing business values.
- Updating rows containing NULL values.

Expected Result:

The `updated_at` column always reflects the latest modification time.

---

# 2. common.validate_resource_tag()

## Purpose

Validates polymorphic references stored in `structured.resource_tags`.

Because PostgreSQL cannot enforce foreign keys across multiple target tables, this trigger ensures that the referenced resource exists before allowing the tag assignment.

Supported resource types:

- DATASET
- TABLE
- COLUMN
- RELATIONSHIP

---

## Test Objectives

Verify that:

- Existing resources are accepted.
- Invalid resources are rejected.
- Unsupported resource types generate an exception.
- Appropriate PostgreSQL error codes are returned.
- Referential integrity is preserved.

---

## Validation

### DATASET

| Test | Expected Result |
|------|-----------------|
| Existing dataset | Accepted |
| Missing dataset | Rejected |

---

### TABLE

| Test | Expected Result |
|------|-----------------|
| Existing table | Accepted |
| Missing table | Rejected |

---

### COLUMN

| Test | Expected Result |
|------|-----------------|
| Existing column | Accepted |
| Missing column | Rejected |

---

### RELATIONSHIP

| Test | Expected Result |
|------|-----------------|
| Existing relationship | Accepted |
| Missing relationship | Rejected |

---

### Invalid Resource Type

| Test | Expected Result |
|------|-----------------|
| Unsupported resource_type | Exception raised |

---

## Error Validation

Verify that the function raises exceptions when:

- Dataset does not exist.
- Table does not exist.
- Column does not exist.
- Relationship does not exist.
- Unsupported resource type is supplied.

Expected Result:

Appropriate PostgreSQL exceptions are generated and invalid metadata is rejected.

---

# Trigger Validation

The trigger functions should be validated to ensure that:

- They execute automatically.
- They do not require manual invocation.
- They preserve data consistency.
- They do not modify unrelated data.

---

# Performance Validation

Verify that:

- Trigger execution introduces minimal overhead.
- Metadata validation completes successfully.
- Trigger behaviour remains consistent during repeated operations.

---

# Success Criteria

Testing is considered successful when:

- All functions are created successfully.
- Trigger functions execute automatically.
- Valid operations complete successfully.
- Invalid operations are rejected.
- Referential integrity is preserved.
- No unexpected exceptions occur.

---

# Related Files

| File | Purpose |
|------|---------|
| `04_common_functions.sql` | Common database functions |
| `common_functions_test.sql` | SQL validation script |
| `DATABASE_STANDARDS.md` | Database development standards |

---

# Summary

The reusable functions implemented in the `common` schema provide shared database functionality used throughout the OmniBrain database module.

Successful completion of the test cases confirms that timestamp automation and polymorphic resource validation operate correctly while preserving metadata integrity across the implemented schemas.