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

### Local development

The backend can automatically apply the SQL schema files during startup when the `DATABASE_AUTO_INIT` environment variable is enabled.

Set this in `.env` for development only:

```env
DATABASE_AUTO_INIT=true
```

### Production

Do not enable automatic schema initialization in production. Instead, apply the schema scripts in numeric order before starting the backend.

Example:

```bash
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USERNAME -d $POSTGRES_DATABASE -f backend/database/schema/00_extensions.sql
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USERNAME -d $POSTGRES_DATABASE -f backend/database/schema/01_schemas.sql
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USERNAME -d $POSTGRES_DATABASE -f backend/database/schema/02_auth.sql
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USERNAME -d $POSTGRES_DATABASE -f backend/database/schema/03_knowledge.sql
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USERNAME -d $POSTGRES_DATABASE -f backend/database/schema/04_common_functions.sql
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USERNAME -d $POSTGRES_DATABASE -f backend/database/schema/05_structured.sql
for f in backend/database/schema/06_query_engine/*.sql; do
  psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USERNAME -d $POSTGRES_DATABASE -f "$f"
 done
```

## Validation

Use SQL test scripts in `backend/database/tests/` to verify schema objects, constraints, and relationships.

- Query engine tests and plan: `backend/database/tests/QUERY_ENGINE_TEST_PLAN.md`
