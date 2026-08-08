# Database Design Specification

Summarizes the OmniBrain database architecture and schema responsibilities.

Key ideas:

- Modular PostgreSQL schemas for separation of concerns
- Shared utilities in `common`
- Domain-specific data in `auth`, `knowledge`, `structured`, and `query_engine`
- SQL-first validation and documentation
