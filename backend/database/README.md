# OmniBrain Database Module

The **Database Module** provides PostgreSQL schemas, shared functions, documentation, and SQL validation for OmniBrain.

## What’s included

- Schema scripts for `auth`, `knowledge`, `structured`, `common`, and `query_engine`
- Documentation and schema execution guidance
- SQL-based test scripts for schema validation

## Core schema folders

- `backend/database/schema/`
- `backend/database/schema/06_query_engine/`
- `backend/database/tests/`
- `backend/database/docs/`

## Execution order

Run schema scripts by numeric prefix.

## Validation

Use SQL test scripts in `backend/database/tests/` to verify schema objects, constraints, and relationships.

- Query engine tests and plan: `backend/database/tests/QUERY_ENGINE_TEST_PLAN.md`
