# Database Setup Guide

**Project:** OmniBrain – Enterprise Multi-Modal RAG Platform

**Module:** Database

**Database:** PostgreSQL 17+

---

# Overview

This guide explains how to set up the PostgreSQL database required for the OmniBrain database module.

It covers:

- PostgreSQL installation
- Database creation
- Required extensions
- Schema initialization
- SQL execution order
- Installation verification
- Common troubleshooting steps

Following this guide ensures that every developer creates a consistent local database environment.

---

# Prerequisites

Before starting, ensure the following software is installed.

| Software | Recommended Version |
|----------|----------------------|
| PostgreSQL | 17+ |
| psql | Latest |
| Git | Latest |
| VS Code | Latest |

---

# Required PostgreSQL Extensions

The database uses PostgreSQL extensions to support UUID generation and additional database functionality.

The required extensions are installed automatically by:

```
schema/00_extensions.sql
```

No manual installation is required after PostgreSQL has been installed successfully.

---

# Clone the Repository

Clone the project repository.

```bash
git clone <repository-url>
```

Navigate to the project directory.

```bash
cd OmniBrain
```

---

# Create the Database

Open PostgreSQL.

```bash
psql postgres
```

Create the database.

```sql
CREATE DATABASE omnibrain;
```

Connect to the database.

```sql
\c omnibrain
```

---

# Execute SQL Scripts

The SQL scripts must be executed in the following order.

```text
00_extensions.sql
        ↓
01_schemas.sql
        ↓
02_auth.sql
        ↓
03_knowledge.sql
        ↓
04_common_functions.sql
        ↓
05_structured.sql
```

Execute each script using `psql`.

Example:

```bash
psql -d omnibrain -f backend/database/schema/00_extensions.sql
```

Repeat for each SQL file following the execution order above.

---

# Verify Installation

After all scripts have been executed successfully, verify that the schemas have been created.

```sql
SELECT schema_name
FROM information_schema.schemata
ORDER BY schema_name;
```

Expected schemas include:

- auth
- knowledge
- structured

---

Verify the tables.

Example:

```sql
\dt knowledge.*
```

```sql
\dt structured.*
```

```sql
\dt auth.*
```

All expected tables should be listed without errors.

---

# Verify Database Functions

Ensure the common database functions have been created.

```sql
\df
```

Verify that functions defined in:

```
04_common_functions.sql
```

are available.

---

# Run Database Tests

Execute the SQL validation scripts.

```
backend/database/tests/
```

Available tests include:

- Authentication tests
- Knowledge schema tests
- Structured schema tests
- Common function tests

Each test should complete without constraint or integrity violations.

---

# Verify Documentation

Confirm that the following documentation is available.

```
backend/database/docs/
```

- Database Design Specification
- Database Standards
- Authentication Schema Specification
- Knowledge Schema Specification
- Structured Schema Specification

These documents should always remain synchronized with the SQL implementation.

---

# Troubleshooting

## Extension Creation Failed

Ensure PostgreSQL is installed correctly and the connected user has sufficient privileges to create extensions.

---

## Database Already Exists

If the database already exists, reconnect instead of creating it again.

```sql
\c omnibrain
```

---

## Relation Already Exists

This usually indicates that the SQL scripts have already been executed.

Recreate the database or execute the scripts only on a clean database.

---

## Missing Tables

Verify that every SQL script was executed in the correct order.

Refer to:

```
SCHEMA_EXECUTION_ORDER.md
```

---

## Foreign Key Errors

Foreign key errors generally occur when scripts are executed out of sequence.

Always execute schema files in numerical order.

---

## Permission Errors

Ensure the PostgreSQL user has privileges to:

- Create schemas
- Create tables
- Create extensions
- Create functions

---

# Development Workflow

When modifying the database module:

1. Update the relevant SQL script.
2. Update the corresponding schema documentation.
3. Update or add SQL tests.
4. Validate the implementation locally.
5. Commit the SQL, documentation, and tests together.

Documentation and SQL should always remain synchronized.

---

# Related Documentation

| Document | Purpose |
|----------|---------|
| `DATABASE_DESIGN_SPEC.md` | Overall database architecture |
| `DATABASE_STANDARDS.md` | Development standards |
| `SCHEMA_EXECUTION_ORDER.md` | SQL execution sequence |
| `DATABASE_NAMING_GUIDE.md` | Naming conventions |
| `AUTH_SCHEMA_SPEC.md` | Authentication schema |
| `KNOWLEDGE_SCHEMA_SPEC.md` | Knowledge schema |
| `STRUCTURED_SCHEMA_SPEC.md` | Structured schema |

---

# Setup Checklist

Before starting development, confirm the following:

- PostgreSQL installed
- Database created
- Required extensions installed
- All SQL scripts executed successfully
- Schemas verified
- Functions verified
- Tests executed successfully
- Documentation reviewed

Once all items are complete, the OmniBrain database environment is ready for development.