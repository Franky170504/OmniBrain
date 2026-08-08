# Schema Execution Order

Defines the order in which database schema scripts should be applied.

## Execution order

1. `00_extensions.sql`
2. `01_schemas.sql`
3. `02_auth.sql`
4. `03_knowledge.sql`
5. `04_common_functions.sql`
6. `05_structured.sql`
7. `06_query_engine/` scripts
