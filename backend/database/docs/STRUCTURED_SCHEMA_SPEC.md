# Structured Schema Specification

**Project:** OmniBrain – Enterprise Multi-Modal RAG Platform

**Schema:** `structured`

**Database:** PostgreSQL 17+

**Version:** 1.0

---

# Overview

The `structured` schema is the central metadata repository for structured data sources integrated into OmniBrain.

It manages metadata describing external data sources, datasets, database tables, columns, relationships, statistics, refresh history, and resource tagging without storing the actual structured data.

This schema enables OmniBrain to discover, organize, profile, and retrieve structured datasets while maintaining clear separation between metadata, source systems, analytics, authentication, and AI services.

The schema provides the relational foundation for integrating databases, spreadsheets, flat files, cloud storage, and APIs into OmniBrain's Retrieval-Augmented Generation (RAG) platform.

---

# Purpose

The purpose of the `structured` schema is to:

- Register structured data sources used by OmniBrain.
- Organize datasets originating from different systems.
- Maintain metadata for tables and columns.
- Store relationships between structured datasets.
- Maintain profiling and statistical metadata.
- Record dataset refresh history.
- Support metadata-driven discovery and filtering.
- Provide reliable metadata for analytics and AI workflows.

The schema stores only metadata and never stores the actual records from external datasets.

---

# Scope

The `structured` schema manages metadata for the following entities:

- Data Sources
- Datasets
- Dataset Tables
- Dataset Columns
- Dataset Relationships
- Dataset Relationship Columns
- Dataset Statistics
- Table Statistics
- Column Statistics
- Tags
- Resource Tag Mapping
- Dataset Refresh History

The schema intentionally excludes the following:

| Component | Managed By |
|-----------|------------|
| Actual database records | External databases |
| CSV, Excel, JSON and Parquet file contents | External storage |
| Database credentials and secrets | Secure configuration / Secret Manager |
| Binary files | MinIO |
| Vector embeddings | Qdrant |
| Authentication and authorization | `auth` schema |
| Query execution | `query_engine` schema |
| Audit logs | `audit` schema |

This separation keeps the schema lightweight while allowing OmniBrain to integrate multiple structured data platforms through metadata.

---

# Architecture

The `structured` schema follows a metadata-first architecture for structured data integration.

```
              External Data Sources
                       │
      ┌────────────────┼────────────────┐
      │                │                │
 Databases        Files & Objects      APIs
      │                │                │
      └────────────────┼────────────────┘
                       │
               Metadata Extraction
                       │
                       ▼
         PostgreSQL (structured schema)
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   Dataset Catalog  Statistics   Relationships
                       │
                       ▼
          Query Engine / AI Services
```

Within PostgreSQL, the metadata hierarchy is organized as follows:

```
Data Source
│
└── Dataset
      │
      ├── Dataset Table
      │      │
      │      ├── Dataset Column
      │      ├── Table Statistics
      │      └── Column Statistics
      │
      ├── Dataset Relationships
      │        └── Relationship Columns
      │
      ├── Dataset Statistics
      ├── Refresh History
      └── Resource Tag Mapping
               │
               └── Tags
```

This hierarchy reflects how structured metadata is organized within OmniBrain.

---

# Design Principles

The `structured` schema is designed around the following principles.

## Metadata First

Only metadata describing structured data assets is stored in PostgreSQL.

Actual database records, spreadsheets, and files remain in their original systems.

---

## Separation of Concerns

Each platform manages the data it is optimized for.

| System | Responsibility |
|---------|----------------|
| PostgreSQL | Structured metadata |
| External Databases | Business data |
| MinIO | Binary assets |
| Qdrant | Vector embeddings |

---

## Source Agnostic

The schema supports metadata from multiple structured data sources through a common relational model.

Supported source types include relational databases, flat files, spreadsheets, cloud storage, and REST APIs.

---

## Normalized Relational Design

Metadata is organized using normalized tables to minimize redundancy and simplify long-term maintenance.

Each table has a clearly defined responsibility.

---

## UUID-Based Identity

Primary entities use UUID identifiers to provide globally unique references across distributed systems.

---

## Referential Integrity

Relationships between sources, datasets, tables, columns, statistics, and tags are enforced through foreign key constraints to maintain metadata consistency.

---

## Scalability

The schema is designed to efficiently support:

- Multiple data sources
- Large numbers of datasets
- Thousands of tables
- Millions of columns
- Metadata profiling
- Enterprise-scale cataloging

Performance is achieved through normalized relationships and appropriate indexing.

---

## Extensibility

The schema is designed to accommodate future capabilities, including:

- Additional connector types
- Advanced data lineage
- Data quality monitoring
- Schema evolution tracking
- AI-assisted metadata enrichment
- Enterprise governance features

---

## PostgreSQL as the Source of Truth

PostgreSQL serves as the authoritative repository for all structured metadata within OmniBrain.

External systems remain the source of business data, while the `structured` schema maintains the metadata required for discovery, integration, analytics, and AI-driven retrieval.


---

# Responsibilities

The `structured` schema is responsible for managing the complete metadata lifecycle of structured data sources integrated into OmniBrain.

It acts as the central metadata layer between external structured data sources, ingestion services, analytics components, and AI-driven retrieval pipelines.

## Core Responsibilities

### Data Source Management

- Register external data sources.
- Maintain source metadata.
- Track source type and connection information.
- Monitor source status.

### Dataset Management

- Register datasets from external sources.
- Organize datasets within the metadata catalog.
- Maintain dataset ownership and lifecycle.
- Track dataset versions and refresh information.

### Schema Management

- Store metadata for dataset tables.
- Maintain column definitions.
- Preserve schema structure.
- Track schema changes.

### Relationship Management

- Store relationships between dataset tables.
- Maintain foreign key mappings.
- Preserve data lineage across datasets.

### Metadata Management

- Store descriptive metadata.
- Maintain dataset statistics.
- Store table statistics.
- Store column statistics.
- Support metadata-based discovery.

### Search & Discovery

Provide metadata required for:

- Dataset discovery
- Metadata filtering
- Column search
- Relationship traversal
- AI-assisted structured data retrieval

### Resource Classification

- Manage reusable tags.
- Associate resources with tags.
- Support metadata categorization.

### Data Integrity

Maintain consistency through:

- Foreign key relationships
- Primary key constraints
- Unique constraints
- Check constraints
- Controlled cascading operations

---

# Responsibilities Outside the Structured Schema

The `structured` schema stores only metadata describing structured data assets.

Other responsibilities are handled by dedicated components.

| Component | Responsibility |
|-----------|----------------|
| External Databases | Store business data |
| Data Warehouses | Analytical datasets |
| Cloud Storage | CSV, Excel, JSON, Parquet files |
| MinIO | Binary assets |
| Qdrant | Vector embeddings |
| `auth` schema | Authentication and authorization |
| `query_engine` schema | Query execution and conversations |
| `audit` schema | Audit logs and activity history |

This separation ensures that the schema remains focused on metadata management rather than data storage.

---

# Core Entity Model

The `structured` schema consists of metadata entities that collectively describe structured data assets integrated into OmniBrain.

Each entity has a single responsibility and participates in a normalized relational model.

| Entity | Purpose |
|---------|---------|
| Data Sources | Register external structured data sources |
| Datasets | Represent logical datasets |
| Dataset Tables | Store table metadata |
| Dataset Columns | Store column metadata |
| Dataset Relationships | Define relationships between tables |
| Relationship Columns | Map relationship columns |
| Dataset Statistics | Store dataset-level metrics |
| Table Statistics | Store table-level metrics |
| Column Statistics | Store column-level metrics |
| Tags | Reusable metadata labels |
| Resource Tag Mapping | Associate resources with tags |
| Dataset Refresh History | Track synchronization history |

---

# Entity Hierarchy

The metadata hierarchy implemented in the database is shown below.

```
Data Source
│
└── Dataset
      │
      ├── Dataset Table
      │      │
      │      ├── Dataset Column
      │      ├── Table Statistics
      │      └── Column Statistics
      │
      ├── Dataset Relationships
      │        └── Relationship Columns
      │
      ├── Dataset Statistics
      ├── Dataset Refresh History
      └── Resource Tag Mapping
               │
               └── Tags
```

Each entity is connected through foreign key relationships, forming a normalized metadata catalog.

---

# Entity Overview

## Data Source

Represents an external system connected to OmniBrain.

Examples include:

- PostgreSQL
- MySQL
- SQL Server
- Oracle
- CSV
- Excel
- REST API
- Snowflake

A data source can contain multiple datasets.

---

## Dataset

Represents a logical collection of structured data obtained from a data source.

Examples include:

- Employee Database
- Sales Records
- Customer Analytics
- Inventory Dataset

Each dataset belongs to one data source.

---

## Dataset Table

Represents an individual table within a dataset.

Each dataset may contain multiple tables.

---

## Dataset Column

Represents metadata describing a table column.

Each column belongs to exactly one dataset table.

---

## Dataset Relationship

Represents relationships between dataset tables.

These relationships preserve the logical connections within structured data.

---

## Relationship Columns

Stores column-level mappings used by dataset relationships.

Each mapping defines how two tables are connected.

---

## Dataset Statistics

Stores dataset-level profiling information such as size, refresh status, and overall metadata.

---

## Table Statistics

Stores profiling information for individual tables.

Examples include:

- Row count
- Storage size
- Last analyzed timestamp

---

## Column Statistics

Stores metadata describing individual columns.

Examples include:

- Null count
- Distinct values
- Data distribution
- Minimum and maximum values

---

## Tags

Represents reusable labels used to classify structured resources.

Tags improve metadata filtering and discovery.

---

## Resource Tag Mapping

Implements the many-to-many relationship between structured resources and tags.

---

## Dataset Refresh History

Stores synchronization history for datasets.

Refresh history helps monitor metadata freshness and track update operations.

---

# Relationship Model

The relationships implemented in the schema are summarized below.

| Parent | Child | Relationship |
|---------|-------|--------------|
| Data Source | Dataset | One-to-Many |
| Dataset | Dataset Table | One-to-Many |
| Dataset Table | Dataset Column | One-to-Many |
| Dataset | Dataset Statistics | One-to-One |
| Dataset Table | Table Statistics | One-to-One |
| Dataset Column | Column Statistics | One-to-One |
| Dataset Table | Dataset Relationships | One-to-Many |
| Dataset Relationship | Relationship Columns | One-to-Many |
| Dataset | Dataset Refresh History | One-to-Many |
| Resource | Tag | Many-to-Many |

---

# Referential Integrity

The schema enforces the following principles:

- Every child entity references a valid parent.
- Orphan metadata records are not permitted.
- Primary keys remain immutable.
- Relationships are maintained using foreign keys.
- Many-to-many relationships are implemented through junction tables.
- Metadata remains consistent across all structured resources.

---

# Naming Conventions

The schema follows a consistent naming convention throughout the project.

## Schema

```
structured
```

---

## Tables

- Lowercase
- Snake case
- Plural nouns

Examples:

```
data_sources
datasets
dataset_tables
dataset_columns
dataset_relationships
relationship_columns
dataset_statistics
table_statistics
column_statistics
tags
resource_tag_mapping
dataset_refresh_history
```

---

## Columns

- Snake case
- Descriptive names
- Singular identifiers

Examples:

```
source_id
dataset_id
table_id
column_id
relationship_id
created_at
updated_at
```

---

## Keys

| Type | Convention |
|------|------------|
| Primary Key | `<entity>_id` |
| Foreign Key | Parent entity primary key |
| Junction Table | Composite foreign keys where applicable |

---

## Timestamp Columns

Timestamp fields follow a consistent naming convention.

```
created_at
updated_at
```

Additional operational timestamps may be maintained for refresh history and synchronization events where applicable.

---

## General Conventions

- UUID primary keys
- Snake case naming
- Explicit foreign keys
- Normalized relationships
- Consistent timestamp fields
- PostgreSQL standard data types
- Metadata-first architecture


---

# Schema Overview

The `structured` schema organizes metadata describing structured data assets integrated into OmniBrain.

The schema follows a hierarchical design in which every structured dataset originates from a registered data source and is further organized into tables, columns, relationships, statistics, tags, and refresh history.

```
Data Source
│
└── Dataset
      │
      ├── Dataset Table
      │      ├── Dataset Column
      │      ├── Table Statistics
      │      └── Column Statistics
      │
      ├── Dataset Relationships
      │      └── Dataset Relationship Columns
      │
      ├── Dataset Statistics
      ├── Dataset Refresh History
      └── Resource Tags
               │
               └── Tags
```

The schema is fully normalized and stores only metadata required for discovery, profiling, governance, and Retrieval-Augmented Generation (RAG) workflows.

---

# Table Specifications

---

# 1. data_sources

## Purpose

The `data_sources` table stores metadata describing external structured data sources registered with OmniBrain.

A data source represents the origin of structured datasets, including relational databases, spreadsheets, flat files, cloud storage, and REST APIs.

---

## Responsibilities

- Register structured data sources.
- Store source metadata.
- Track source type.
- Maintain connection metadata.
- Monitor source status.

---

## Primary Key

| Column | Type |
|---------|------|
| `source_id` | UUID |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Identification | Source name and identifier |
| Source Information | Source type and platform |
| Connection Metadata | Connection configuration metadata |
| Status | Source lifecycle state |
| Ownership | Created and updated metadata |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Data Source → Dataset | One-to-Many |

A single data source may contain multiple datasets.

---

## Constraints

- UUID primary key
- Required source metadata
- Foreign key integrity
- Automatic timestamp tracking

---

## Indexing

Indexes support:

- Source lookup
- Metadata filtering
- Dataset discovery
- Join optimization

---

## Example

```
Data Source

Name: Production PostgreSQL
Type: PostgreSQL
Status: Active
```

---

## Notes

- The table stores metadata only.
- Credentials and secrets are intentionally excluded.

---

# 2. datasets

## Purpose

The `datasets` table stores metadata describing logical datasets obtained from registered data sources.

Each dataset represents a structured collection of related data managed within OmniBrain.

---

## Responsibilities

- Register datasets.
- Organize datasets within the metadata catalog.
- Maintain dataset ownership.
- Track dataset lifecycle.
- Support discovery and retrieval.

---

## Primary Key

| Column | Type |
|---------|------|
| `dataset_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `source_id` | `data_sources.source_id` |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Identification | Dataset name and identifier |
| Source | Parent data source |
| Description | Dataset metadata |
| Lifecycle | Status and refresh information |
| Ownership | Created and updated metadata |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Data Source → Dataset | Many-to-One |
| Dataset → Dataset Tables | One-to-Many |
| Dataset → Dataset Statistics | One-to-One |
| Dataset → Dataset Refresh History | One-to-Many |

---

## Constraints

- UUID primary key
- Mandatory parent data source
- Required dataset metadata
- Foreign key enforcement
- Timestamp tracking

---

## Indexing

Indexes support:

- Dataset lookup
- Source filtering
- Metadata filtering
- Join performance

---

## Example

```
Dataset

Name: Customer Analytics
Source: Production PostgreSQL
Status: Active
```

---

## Notes

- A dataset represents metadata describing structured data.
- Business records remain stored in the original source system.

---

# 3. dataset_tables

## Purpose

The `dataset_tables` table stores metadata describing individual tables belonging to a dataset.

Each record represents one logical table discovered during metadata extraction.

---

## Responsibilities

- Register dataset tables.
- Preserve table metadata.
- Maintain table ownership.
- Support schema discovery.
- Provide metadata for downstream profiling.

---

## Primary Key

| Column | Type |
|---------|------|
| `table_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `dataset_id` | `datasets.dataset_id` |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Identification | Table name and identifier |
| Dataset | Parent dataset |
| Schema Information | Database schema metadata |
| Description | Table metadata |
| Ownership | Created and updated metadata |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Dataset → Dataset Table | One-to-Many |
| Dataset Table → Dataset Column | One-to-Many |
| Dataset Table → Table Statistics | One-to-One |
| Dataset Table → Dataset Relationships | One-to-Many |

---

## Constraints

- UUID primary key
- Mandatory parent dataset
- Foreign key enforcement
- Required metadata fields
- Timestamp tracking

---

## Indexing

Indexes support:

- Table lookup
- Dataset filtering
- Metadata discovery
- Relationship traversal

---

## Example

```
Dataset

Customer Analytics

└── Tables

    • customers
    • orders
    • payments
```

---

## Notes

- Each record describes a logical table within a dataset.
- The table stores metadata only and does not contain business records.


---

# 4. dataset_columns

## Purpose

The `dataset_columns` table stores metadata describing individual columns within dataset tables.

Each record represents a single column discovered during metadata extraction and preserves its structural properties for discovery, profiling, governance, and AI-assisted retrieval.

---

## Responsibilities

- Register table columns.
- Store column metadata.
- Preserve column definitions.
- Support schema discovery.
- Enable metadata profiling.

---

## Primary Key

| Column | Type |
|---------|------|
| `column_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `table_id` | `dataset_tables.table_id` |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Identification | Column name and identifier |
| Parent Table | Associated dataset table |
| Data Definition | Data type, length, precision, scale |
| Constraints | Nullable and key information |
| Description | Column metadata |
| Ownership | Created and updated metadata |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Dataset Table → Dataset Column | One-to-Many |
| Dataset Column → Column Statistics | One-to-One |

---

## Constraints

- UUID primary key
- Mandatory parent table
- Foreign key enforcement
- Required metadata fields
- Automatic timestamp tracking

---

## Indexing

Indexes support:

- Column lookup
- Schema discovery
- Metadata filtering
- Join optimization

---

## Example

```
Table: customers

Columns

• customer_id
• first_name
• last_name
• email
• phone
• created_at
```

---

## Notes

- Each record represents metadata for a single structured data column.
- Actual column values remain in the external data source.

---

# 5. dataset_relationships

## Purpose

The `dataset_relationships` table stores metadata describing logical relationships between dataset tables.

These relationships preserve structural connections across datasets and enable navigation during metadata exploration and query generation.

---

## Responsibilities

- Store table relationships.
- Maintain relational metadata.
- Preserve data lineage.
- Support relationship traversal.

---

## Primary Key

| Column | Type |
|---------|------|
| `relationship_id` | UUID |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Identification | Relationship identifier |
| Source Table | Parent table |
| Target Table | Referenced table |
| Relationship Type | Logical relationship metadata |
| Ownership | Created and updated metadata |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Dataset Relationship → Relationship Columns | One-to-Many |

---

## Constraints

- UUID primary key
- Required relationship metadata
- Foreign key integrity
- Timestamp tracking

---

## Indexing

Indexes support:

- Relationship lookup
- Join traversal
- Metadata discovery

---

## Example

```
customers

customer_id
      │
      ▼

orders

customer_id
```

---

## Notes

- Relationship metadata supports navigation across structured datasets.
- The table stores metadata only and does not enforce business constraints on external systems.

---

# 6. dataset_relationship_columns

## Purpose

The `dataset_relationship_columns` table stores column-level mappings used to define relationships between structured tables.

Each record identifies the participating columns that form a relationship.

---

## Responsibilities

- Map relationship columns.
- Preserve column-level lineage.
- Support relationship discovery.
- Maintain normalized relationship metadata.

---

## Primary Key

| Column | Type |
|---------|------|
| `relationship_column_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `relationship_id` | `dataset_relationships.relationship_id` |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Identification | Relationship column identifier |
| Parent Relationship | Associated relationship |
| Source Column | Referencing column |
| Target Column | Referenced column |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Dataset Relationship → Relationship Columns | One-to-Many |

---

## Constraints

- UUID primary key
- Mandatory relationship reference
- Foreign key enforcement

---

## Indexing

Indexes support:

- Relationship traversal
- Column mapping
- Metadata joins

---

## Example

```
Relationship

customers.customer_id

↓

orders.customer_id
```

---

## Notes

- Stores mappings only.
- Does not duplicate column metadata.

---

# 7. dataset_statistics

## Purpose

The `dataset_statistics` table stores profiling information describing datasets at a high level.

These statistics provide summary information that supports discovery, monitoring, and optimization without scanning external data sources.

---

## Responsibilities

- Store dataset profiling metadata.
- Maintain summary statistics.
- Support monitoring.
- Improve dataset discovery.

---

## Primary Key

| Column | Type |
|---------|------|
| `dataset_statistics_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `dataset_id` | `datasets.dataset_id` |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Dataset | Parent dataset |
| Profile | Summary metrics |
| Refresh | Latest profiling information |
| Ownership | Created and updated metadata |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Dataset → Dataset Statistics | One-to-One |

---

## Constraints

- UUID primary key
- Mandatory dataset reference
- Foreign key enforcement
- Timestamp tracking

---

## Indexing

Indexes support:

- Dataset profiling
- Metadata retrieval
- Performance optimization

---

## Example

```
Dataset Statistics

Tables: 18

Columns: 245

Last Profiled:
2026-07-30
```

---

## Notes

- Statistics summarize dataset metadata only.
- Business data remains stored within the external source system.



---

# 8. table_statistics

## Purpose

The `table_statistics` table stores profiling and summary metadata for individual dataset tables.

These statistics provide insights into table characteristics without accessing the underlying business data.

---

## Responsibilities

- Store table profiling information.
- Maintain summary statistics.
- Support metadata analysis.
- Improve dataset discovery.

---

## Primary Key

| Column | Type |
|---------|------|
| `table_statistics_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `table_id` | `dataset_tables.table_id` |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Parent Table | Associated dataset table |
| Profile | Table-level statistics |
| Analysis | Profiling metadata |
| Ownership | Created and updated metadata |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Dataset Table → Table Statistics | One-to-One |

---

## Constraints

- UUID primary key
- Mandatory table reference
- Foreign key enforcement
- Timestamp tracking

---

## Indexing

Indexes support:

- Table profiling
- Metadata retrieval
- Join optimization

---

## Example

```
Table Statistics

Rows: 2,450,000

Columns: 24

Last Profiled:
2026-07-30
```

---

## Notes

- Statistics summarize table metadata only.
- Business records remain in the original source.

---

# 9. column_statistics

## Purpose

The `column_statistics` table stores profiling information for individual columns.

These statistics assist data discovery, quality assessment, and AI-assisted understanding of structured datasets.

---

## Responsibilities

- Store column profiling metadata.
- Maintain summary statistics.
- Support metadata exploration.
- Improve analytical queries.

---

## Primary Key

| Column | Type |
|---------|------|
| `column_statistics_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `column_id` | `dataset_columns.column_id` |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Parent Column | Associated dataset column |
| Distribution | Statistical summary |
| Quality | Profiling information |
| Ownership | Created and updated metadata |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Dataset Column → Column Statistics | One-to-One |

---

## Constraints

- UUID primary key
- Mandatory column reference
- Foreign key enforcement

---

## Indexing

Indexes support:

- Column profiling
- Metadata filtering
- Query optimization

---

## Example

```
Column Statistics

Distinct Values: 1,024

Null Values: 8

Minimum Value

Maximum Value
```

---

## Notes

- Statistics describe metadata only.
- Raw column values remain external.

---

# 10. tags

## Purpose

The `tags` table stores reusable labels used to classify structured resources within OmniBrain.

---

## Responsibilities

- Store reusable tags.
- Support metadata classification.
- Enable resource filtering.
- Improve metadata discovery.

---

## Primary Key

| Column | Type |
|---------|------|
| `tag_id` | UUID |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Identification | Tag name |
| Description | Tag metadata |
| Ownership | Created and updated metadata |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Tag ↔ Structured Resources | Many-to-Many |

---

## Constraints

- UUID primary key
- Unique tag name
- Required tag metadata

---

## Indexing

Indexes support:

- Tag lookup
- Metadata filtering
- Resource discovery

---

## Example

```
Tags

• Finance

• HR

• Sales

• Inventory
```

---

## Notes

Tags are reusable across all supported structured resources.

---

# 11. resource_tags

## Purpose

The `resource_tags` table implements the many-to-many relationship between structured resources and reusable tags.

---

## Responsibilities

- Associate resources with tags.
- Eliminate metadata duplication.
- Maintain normalized relationships.

---

## Primary Key

Composite Primary Key

| Column |
|---------|
| Resource Identifier |
| Tag Identifier |

---

## Foreign Keys

| Column | References |
|---------|------------|
| Resource | Structured resource |
| Tag | `tags.tag_id` |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Resource ↔ Tag | Many-to-Many |

---

## Constraints

- Composite primary key
- Mandatory resource reference
- Mandatory tag reference
- Duplicate mappings not permitted

---

## Indexing

Indexes support:

- Tag-based filtering
- Resource lookup
- Join optimization

---

## Example

```
Dataset

Customer Analytics

↓

Tags

• Production

• Finance

• Reporting
```

---

## Notes

The table stores relationships only and does not duplicate resource metadata.

---

# 12. dataset_refresh_history

## Purpose

The `dataset_refresh_history` table records synchronization events for datasets.

It provides historical metadata describing refresh operations and supports monitoring of dataset freshness.

---

## Responsibilities

- Record refresh operations.
- Maintain synchronization history.
- Track refresh status.
- Support operational monitoring.

---

## Primary Key

| Column | Type |
|---------|------|
| `refresh_history_id` | UUID |

---

## Foreign Key

| Column | References |
|---------|------------|
| `dataset_id` | `datasets.dataset_id` |

---

## Key Metadata

| Category | Description |
|----------|-------------|
| Dataset | Parent dataset |
| Refresh | Synchronization metadata |
| Status | Refresh outcome |
| Timing | Refresh timestamps |

---

## Relationships

| Relationship | Type |
|--------------|------|
| Dataset → Refresh History | One-to-Many |

---

## Constraints

- UUID primary key
- Mandatory dataset reference
- Foreign key enforcement
- Timestamp tracking

---

## Indexing

Indexes support:

- Refresh history lookup
- Dataset monitoring
- Operational reporting

---

## Example

```
Dataset Refresh

Status:
Completed

Started:
10:00 AM

Finished:
10:02 AM
```

---

## Notes

Refresh history stores operational metadata only and does not contain business data.

---

# Constraints

The `structured` schema enforces constraints to maintain metadata consistency and referential integrity.

## Primary Keys

Each primary entity uses a UUID-based primary key.

The `resource_tags` junction table uses a composite primary key.

---

## Foreign Keys

Foreign key constraints maintain hierarchical relationships throughout the schema.

Examples include:

- Data Source → Dataset
- Dataset → Dataset Table
- Dataset Table → Dataset Column
- Dataset → Dataset Statistics
- Dataset Table → Table Statistics
- Dataset Column → Column Statistics
- Dataset → Dataset Refresh History
- Dataset Relationship → Relationship Columns
- Resource → Resource Tags

---

## Unique Constraints

Unique constraints prevent duplicate metadata where uniqueness is required.

Typical examples include:

- Tag names
- Resource-tag mappings

---

## Check Constraints

Check constraints validate controlled metadata values before storage.

Examples include:

- Status values
- Processing states
- Metadata validation rules

---

## NOT NULL Constraints

Mandatory metadata fields are enforced using `NOT NULL` constraints.

---

## Default Values

Default values are used where appropriate for:

- UUID generation
- Creation timestamps
- Update timestamps
- Default processing states

---

## Referential Integrity

Foreign key constraints ensure that metadata relationships remain valid and prevent orphan records.

---

# Indexing Strategy

The `structured` schema uses indexing to optimize metadata retrieval and relationship traversal.

## Primary Indexes

Every table is indexed through its primary key.

---

## Foreign Key Indexes

Indexes on foreign key columns improve join performance and hierarchical navigation.

---

## Metadata Indexes

Indexes support common access patterns, including:

- Source lookup
- Dataset discovery
- Table lookup
- Column lookup
- Tag filtering
- Refresh history

---

## Composite Indexes

Composite indexes improve performance for junction tables and frequently joined metadata.

---

## Performance Considerations

The indexing strategy is designed to support:

- Fast metadata discovery
- Efficient schema exploration
- Low-latency joins
- Enterprise-scale structured data cataloging



---

# Referential Integrity

The `structured` schema enforces referential integrity through foreign key constraints to maintain consistency across all structured metadata.

Each child entity must reference a valid parent entity, ensuring that metadata remains accurate and preventing orphan records.

## Relationship Summary

| Parent Table | Child Table | Relationship |
|--------------|-------------|--------------|
| `data_sources` | `datasets` | One-to-Many |
| `datasets` | `dataset_tables` | One-to-Many |
| `dataset_tables` | `dataset_columns` | One-to-Many |
| `dataset_tables` | `dataset_relationships` | One-to-Many |
| `dataset_relationships` | `dataset_relationship_columns` | One-to-Many |
| `datasets` | `dataset_statistics` | One-to-One |
| `dataset_tables` | `table_statistics` | One-to-One |
| `dataset_columns` | `column_statistics` | One-to-One |
| `datasets` | `dataset_refresh_history` | One-to-Many |
| `tags` | `resource_tags` | One-to-Many |

---

## Integrity Rules

The schema follows these principles:

- Every child record must reference an existing parent record.
- Foreign key constraints enforce ownership relationships.
- Orphan metadata records are not permitted.
- Primary keys remain immutable.
- Metadata consistency is maintained across all entities.
- Many-to-many relationships are implemented through junction tables.

These rules ensure reliable navigation and management of structured metadata throughout OmniBrain.

---

# Cascade Policies

Cascade policies define how dependent metadata is handled when parent entities are removed.

Dependent metadata should be removed automatically where ownership exists, while higher-level organizational entities should be protected against accidental deletion.

## Cascading Relationships

| Parent | Child | Delete Policy |
|---------|-------|---------------|
| Datasets | Dataset Tables | Cascade |
| Dataset Tables | Dataset Columns | Cascade |
| Dataset Tables | Table Statistics | Cascade |
| Dataset Columns | Column Statistics | Cascade |
| Dataset Relationships | Dataset Relationship Columns | Cascade |
| Datasets | Dataset Statistics | Cascade |
| Datasets | Dataset Refresh History | Cascade |
| Tags | Resource Tags | Cascade |

---

## Restricted Relationships

Higher-level entities are protected from accidental deletion.

| Parent | Child | Delete Policy |
|---------|-------|---------------|
| Data Sources | Datasets | Restricted |

This prevents accidental removal of entire metadata catalogs while dependent datasets still exist.

---

## Benefits

The cascade strategy provides:

- Automatic cleanup of dependent metadata.
- Prevention of orphan records.
- Consistent hierarchical relationships.
- Simplified maintenance of structured metadata.

---

# Storage Integration

The `structured` schema stores metadata only.

Actual structured data remains in external systems while PostgreSQL manages the metadata required for discovery, governance, and AI-assisted retrieval.

## Storage Architecture

| Component | Responsibility |
|-----------|----------------|
| PostgreSQL (`structured`) | Structured metadata |
| External Databases | Business data |
| Cloud Storage | CSV, Excel, JSON, Parquet files |
| MinIO | Binary assets |
| Qdrant | Vector embeddings |

---

## PostgreSQL

Stores:

- Data source metadata
- Dataset metadata
- Table metadata
- Column metadata
- Relationship metadata
- Statistical metadata
- Tags
- Refresh history

---

## External Data Sources

Business data remains within its original system.

Examples include:

- PostgreSQL
- MySQL
- SQL Server
- Oracle
- Snowflake
- CSV
- Excel
- REST APIs

The `structured` schema stores references and metadata rather than business records.

---

## MinIO

Stores binary assets associated with structured data workflows where required.

Examples include exported files, reports, and supporting artifacts.

---

## Qdrant

Stores vector embeddings generated from structured metadata for semantic search and AI-assisted retrieval.

Embedding vectors are linked back to PostgreSQL metadata during query execution.

---

## Retrieval Flow

```
User Query
      │
      ▼
Metadata Discovery (PostgreSQL)
      │
      ▼
Structured Dataset Selection
      │
      ▼
Semantic Retrieval (Qdrant)
      │
      ▼
External Data Access
      │
      ▼
LLM Response Generation
```

This architecture allows each component to focus on its specialized workload while maintaining a unified retrieval pipeline.

---

# Performance Notes

The `structured` schema is designed to efficiently support metadata cataloging, structured data discovery, and enterprise-scale retrieval.

## Design Considerations

- Normalized relational design
- UUID-based identifiers
- Indexed foreign keys
- Optimized joins
- Metadata-first architecture

---

## Optimized Operations

The schema supports efficient execution of:

- Data source discovery
- Dataset filtering
- Table lookup
- Column lookup
- Relationship traversal
- Metadata profiling
- Tag-based filtering
- Refresh history retrieval

---

## Scalability

The schema is designed to support:

- Multiple external data sources
- Thousands of datasets
- Large database catalogs
- Millions of metadata records
- Enterprise-scale structured data integration

Performance is achieved through normalized relationships, indexing, and efficient metadata organization.

---

# Future Extensions

The schema is designed to accommodate future enhancements without major structural changes.

Potential extensions include:

- Data lineage visualization
- Schema evolution tracking
- Advanced data quality monitoring
- AI-generated metadata enrichment
- Automated metadata synchronization
- Multi-cloud data source integration
- Data governance policies
- Dataset version management
- Fine-grained access control
- Enterprise metadata cataloging

These capabilities can be incorporated while preserving the existing relational design.

---

# Appendix

## Table Summary

| Table | Purpose |
|--------|---------|
| `data_sources` | Registers external structured data sources |
| `datasets` | Stores dataset metadata |
| `dataset_tables` | Stores table metadata |
| `dataset_columns` | Stores column metadata |
| `dataset_relationships` | Stores relationships between tables |
| `dataset_relationship_columns` | Stores column-level relationship mappings |
| `dataset_statistics` | Stores dataset-level statistics |
| `table_statistics` | Stores table-level statistics |
| `column_statistics` | Stores column-level statistics |
| `tags` | Stores reusable metadata tags |
| `resource_tags` | Maps resources to tags |
| `dataset_refresh_history` | Stores dataset refresh history |

---

## Complete Entity Hierarchy

```
data_sources
│
└── datasets
      │
      ├── dataset_tables
      │      │
      │      ├── dataset_columns
      │      │      └── column_statistics
      │      │
      │      ├── table_statistics
      │      │
      │      └── dataset_relationships
      │              │
      │              └── dataset_relationship_columns
      │
      ├── dataset_statistics
      ├── dataset_refresh_history
      │
      └── resource_tags
              │
              └── tags
```

---

## Schema Summary

The `structured` schema serves as the authoritative metadata repository for structured data within OmniBrain.

It catalogs external data sources, datasets, tables, columns, relationships, statistics, tags, and synchronization history while maintaining a normalized relational model.

Actual business data remains in external systems, PostgreSQL stores the metadata, MinIO manages binary assets when required, and Qdrant provides vector-based semantic retrieval.

By separating metadata from business data, the schema provides a scalable and maintainable foundation for structured data discovery, governance, analytics, and Retrieval-Augmented Generation (RAG) workflows across the OmniBrain platform.