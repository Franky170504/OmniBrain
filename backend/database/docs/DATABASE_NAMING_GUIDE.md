# Database Naming Guide

**Project:** OmniBrain – Enterprise Multi-Modal RAG Platform

**Module:** Database

**Database:** PostgreSQL 17+

---

# Overview

This document defines the naming conventions used throughout the OmniBrain PostgreSQL database.

Consistent naming improves readability, maintainability, collaboration, and long-term scalability across all database schemas.

All SQL scripts, schemas, tables, functions, constraints, and indexes should follow the conventions described in this guide.

---

# Design Principles

The database naming conventions are based on the following principles:

- Consistency
- Readability
- Predictability
- Scalability
- Self-descriptive names
- PostgreSQL best practices

---

# Schema Naming

Schema names use:

- Lowercase letters
- Snake case
- Singular nouns representing functional modules

## Examples

```
auth

knowledge

structured
```

---

# Table Naming

Table names use:

- Lowercase letters
- Snake case
- Plural nouns

## Examples

```
users

roles

documents

pages

chunks

images

tables

datasets

dataset_tables

dataset_columns

tags

resource_tags
```

Plural table names indicate that each table stores multiple records of the same entity.

---

# Column Naming

Column names use:

- Lowercase letters
- Snake case
- Descriptive names
- Singular form where appropriate

## Examples

```
user_id

document_id

dataset_id

table_id

column_id

relationship_id

created_at

updated_at
```

Avoid abbreviations unless they are widely recognized.

---

# Primary Keys

Primary keys follow the convention:

```
<entity>_id
```

## Examples

```
user_id

role_id

document_id

page_id

chunk_id

dataset_id

table_id

column_id
```

UUIDs are used as the primary identifier for major entities to ensure globally unique references.

---

# Foreign Keys

Foreign keys use the primary key name of the referenced table.

## Examples

```
user_id

document_id

page_id

dataset_id

table_id

column_id
```

This convention makes relationships immediately recognizable.

---

# Junction Tables

Many-to-many relationships are implemented using dedicated junction tables.

Naming convention:

```
<entity>_<entity>
```

or

```
<resource>_tags
```

## Examples

```
document_tag_mapping

resource_tags
```

Junction tables store only relationship metadata and avoid duplicating entity information.

---

# Boolean Columns

Boolean fields use descriptive names that clearly indicate a true or false state.

Examples include:

```
is_active

is_deleted

is_verified

is_nullable
```

The `is_` prefix improves readability in SQL queries and application code.

---

# Timestamp Columns

Timestamp fields use a consistent naming convention.

## Standard Columns

```
created_at

updated_at
```

Operational timestamps may include descriptive suffixes when required.

Examples:

```
last_refresh_at

processed_at

completed_at
```

---

# Enumeration Columns

Columns representing predefined values should use descriptive names.

Examples include:

```
status

source_type

relationship_type

processing_state
```

Where applicable, valid values are enforced using check constraints.

---

# Function Naming

Reusable database functions follow:

```
verb_noun()
```

Examples:

```
generate_uuid()

update_timestamp()

calculate_statistics()
```

Function names should clearly describe their purpose.

---

# Constraint Naming

Constraints follow a consistent naming pattern.

## Primary Keys

```
pk_<table>
```

Example:

```
pk_documents
```

---

## Foreign Keys

```
fk_<child>_<parent>
```

Example:

```
fk_documents_collections
```

---

## Unique Constraints

```
uq_<table>_<column>
```

Example:

```
uq_tags_name
```

---

## Check Constraints

```
chk_<table>_<rule>
```

Example:

```
chk_documents_status
```

---

# Index Naming

Indexes use descriptive names following the convention:

```
idx_<table>_<column>
```

Examples:

```
idx_documents_name

idx_chunks_page_id

idx_dataset_columns_table_id
```

Composite indexes should include the most significant indexed columns.

---

# SQL File Naming

SQL files are executed sequentially.

Naming convention:

```
NN_description.sql
```

Examples:

```
00_extensions.sql

01_schemas.sql

02_auth.sql

03_knowledge.sql

04_common_functions.sql

05_structured.sql
```

Numeric prefixes ensure deterministic execution order.

---

# Documentation Naming

Documentation files use uppercase descriptive names with underscores.

Examples:

```
DATABASE_SETUP.md

DATABASE_STANDARDS.md

DATABASE_DESIGN_SPEC.md

AUTH_SCHEMA_SPEC.md

KNOWLEDGE_SCHEMA_SPEC.md

STRUCTURED_SCHEMA_SPEC.md
```

This naming convention distinguishes technical documentation from SQL scripts.

---

# Test File Naming

SQL validation scripts use:

```
<component>_test.sql
```

Examples:

```
auth_test.sql

knowledge_test.sql

structured_test.sql

common_functions_test.sql
```

Test plans use:

```
<COMPONENT>_TEST_PLAN.md
```

Examples:

```
AUTH_TEST_PLAN.md

KNOWLEDGE_TEST_PLAN.md

STRUCTURED_TEST_PLAN.md

COMMON_FUNCTIONS_TEST_PLAN.md
```

---

# General Guidelines

When adding new database objects:

- Use lowercase names for SQL objects.
- Use snake case consistently.
- Avoid spaces and special characters.
- Prefer descriptive names over abbreviations.
- Keep naming consistent across all schemas.
- Reuse existing conventions whenever possible.
- Update documentation when introducing new naming patterns.

Following these conventions ensures that the OmniBrain database remains consistent, maintainable, and easy to understand as new schemas and features are added.

---

# Summary

The OmniBrain database follows a standardized naming convention across schemas, tables, columns, functions, constraints, indexes, SQL scripts, documentation, and test files.

These conventions promote consistency, improve collaboration, simplify maintenance, and provide a predictable structure for future database development.