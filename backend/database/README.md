# OmniBrain Database Module

The **Database Module** is the core data management layer of the **OmniBrain** platform. It provides the PostgreSQL schemas, database standards, architecture documentation, migration framework, and testing utilities required to support the platform's enterprise-scale Retrieval-Augmented Generation (RAG) system.

The module is designed with a modular architecture where each schema is responsible for a specific business domain while maintaining clear separation of concerns, data integrity, and scalability.

---

# Module Objectives

The database module is responsible for:

- Designing and maintaining the PostgreSQL database architecture.
- Defining relational schemas and constraints.
- Managing metadata for knowledge and structured data.
- Providing reusable database functions.
- Maintaining database documentation.
- Supporting database migrations.
- Validating database objects through SQL-based tests.

---

# Directory Structure

```
backend/database/
│
├── README.md
│
├── docs/
│   ├── architecture/
│   ├── AUTH_SCHEMA_SPEC.md
│   ├── DATABASE_DESIGN_SPEC.md
│   ├── DATABASE_STANDARDS.md
│   ├── DATABASE_SETUP.md
│   ├── DATABASE_CHANGELOG.md
│   ├── DATABASE_NAMING_GUIDE.md
│   ├── SCHEMA_EXECUTION_ORDER.md
│   ├── KNOWLEDGE_SCHEMA_SPEC.md
│   └── STRUCTURED_SCHEMA_SPEC.md
│
├── schema/
│   ├── 00_extensions.sql
│   ├── 01_schemas.sql
│   ├── 02_auth.sql
│   ├── 03_knowledge.sql
│   ├── 04_common_functions.sql
│   └── 05_structured.sql
│
├── migrations/
│
└── tests/
    ├── AUTH_TEST_PLAN.md
    ├── KNOWLEDGE_TEST_PLAN.md
    ├── STRUCTURED_TEST_PLAN.md
    ├── COMMON_FUNCTIONS_TEST_PLAN.md
    ├── auth_test.sql
    ├── knowledge_test.sql
    ├── structured_test.sql
    └── common_functions_test.sql
```

---

# Database Architecture

The database follows a modular schema-based architecture.

Each schema manages a specific functional area of OmniBrain while sharing a common PostgreSQL database.

Current schemas include:

| Schema | Purpose |
|---------|---------|
| `auth` | User authentication and authorization |
| `knowledge` | Metadata for unstructured knowledge assets |
| `structured` | Metadata for structured datasets |
| `common` | Shared database utilities and reusable functions |

Additional schemas may be introduced as the platform evolves.

---

# Database Workflow

```
Document / Dataset Ingestion
            │
            ▼
      Metadata Extraction
            │
            ▼
      PostgreSQL Database
            │
   ┌────────┼────────┐
   │        │        │
 auth   knowledge structured
   │        │        │
   └────────┼────────┘
            │
            ▼
    Retrieval & AI Services
```

---

# SQL Schema

The SQL implementation is organized into incremental scripts.

| File | Purpose |
|------|---------|
| `00_extensions.sql` | Installs required PostgreSQL extensions |
| `01_schemas.sql` | Creates application schemas |
| `02_auth.sql` | Authentication schema |
| `03_knowledge.sql` | Knowledge metadata schema |
| `04_common_functions.sql` | Shared database functions |
| `05_structured.sql` | Structured metadata schema |

The scripts should always be executed in numerical order.

---

# Documentation

The `docs/` directory contains the complete technical documentation for the database module.

Available documentation includes:

- Database Design Specification
- Database Standards
- Database Setup Guide
- Database Naming Guide
- Schema Execution Order
- Knowledge Schema Specification
- Structured Schema Specification
- Authentication Schema Specification
- Architecture Diagrams

---

# Architecture Diagrams

The `docs/architecture/` directory contains diagrams describing the database architecture, including:

- Conceptual ER Diagram
- Logical Database Schema
- Overall Database Architecture
- Internal Storage Architecture
- PostgreSQL Architecture
- Query Processing Pipeline

These diagrams provide a visual representation of the database design and data flow.

---

# Testing

The `tests/` directory contains SQL validation scripts and testing documentation for the implemented schemas.

Testing includes:

- Schema validation
- Constraint verification
- Foreign key validation
- Function testing
- Data integrity checks
- Metadata validation

Each schema has its own dedicated test plan and SQL test script.

---

# Migrations

The `migrations/` directory is reserved for future schema evolution.

Database migrations will be version-controlled to ensure safe and repeatable updates across development, testing, and production environments.

---

# Development Guidelines

When modifying the database module:

- Follow the established database standards.
- Maintain naming consistency.
- Preserve referential integrity.
- Keep documentation synchronized with SQL changes.
- Add or update tests for every schema modification.
- Ensure SQL scripts remain idempotent where applicable.

---

# Related Documentation

| Document | Description |
|----------|-------------|
| `DATABASE_DESIGN_SPEC.md` | Overall database architecture and design decisions |
| `DATABASE_STANDARDS.md` | Database development standards |
| `DATABASE_SETUP.md` | Environment setup and installation |
| `DATABASE_NAMING_GUIDE.md` | Naming conventions used throughout the database |
| `SCHEMA_EXECUTION_ORDER.md` | SQL execution sequence |
| `AUTH_SCHEMA_SPEC.md` | Authentication schema documentation |
| `KNOWLEDGE_SCHEMA_SPEC.md` | Knowledge schema documentation |
| `STRUCTURED_SCHEMA_SPEC.md` | Structured schema documentation |

---

# Current Status

| Component | Status |
|-----------|--------|
| Database Standards | ✅ Implemented |
| Database Design | ✅ Documented |
| Authentication Schema | ✅ Implemented |
| Knowledge Schema | ✅ Implemented |
| Structured Schema | ✅ Implemented |
| Common Functions | ✅ Implemented |
| Architecture Documentation | ✅ Available |
| Database Testing | ✅ In Progress |
| Database Migrations | 🚧 Planned |

---

# Version

**Project:** OmniBrain

**Module:** Database

**Database:** PostgreSQL 17+

**Current Development Branch:** `feature/database`

**Status:** Active Development