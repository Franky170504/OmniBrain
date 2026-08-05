# OmniBrain Database Design Specification (DDS)

**Project Name:** OmniBrain – Enterprise Agentic Multi-Modal RAG Platform

**Document Type:** Database Design Specification (DDS)

**Version:** 1.0

**Owner:** Database Engineering Team

**Chief Database Architect:** DBMS Team

**Status:** Draft (Implementation Phase)

---

# Table of Contents

1. Introduction
2. Project Overview
3. Database Objectives
4. Scope
5. Non-Goals
6. Overall Database Architecture
7. Polyglot Storage Strategy
8. PostgreSQL Responsibilities
9. External Storage Responsibilities
10. Database Schemas
11. Data Lifecycle
12. Entity Design
13. Relationship Design
14. Security Design
15. Performance Strategy
16. Index Strategy
17. Backup Strategy
18. Scaling Strategy
19. Future Enhancements

---

# 1. Introduction

OmniBrain is an enterprise-grade Agentic Multi-Modal Retrieval-Augmented Generation (RAG) platform capable of ingesting, processing, indexing, retrieving, and reasoning over multiple forms of information including:

- PDF Documents
- DOCX Documents
- Images
- Tables
- Charts
- Structured Databases
- Knowledge Graphs
- Audio (future)
- Video (future)

This document specifies the complete database architecture used by OmniBrain.

---

# 2. Project Overview

Unlike traditional applications, OmniBrain does not store only transactional information.

It acts as a metadata backbone for an AI-powered knowledge platform.

The PostgreSQL database stores:

- document metadata
- knowledge hierarchy
- users
- permissions
- retrieval history
- feedback
- structured data catalog
- audit logs

while delegating vector search and object storage to specialized systems.

---

# 3. Database Objectives

The database has six primary objectives.

## Objective 1

Maintain a normalized metadata catalog.

---

## Objective 2

Provide reliable transactional storage.

---

## Objective 3

Support enterprise-scale document management.

---

## Objective 4

Support hybrid retrieval.

---

## Objective 5

Maintain complete query history.

---

## Objective 6

Provide observability and auditability.

---

# 4. Scope

The PostgreSQL subsystem is responsible for:

✓ User management

✓ Role management

✓ Domains

✓ Collections

✓ Documents

✓ Document versions

✓ Pages

✓ Chunks

✓ Images

✓ Tables

✓ Tags

✓ Structured data catalog

✓ Retrieval history

✓ User feedback

✓ Audit logs

---

# 5. Out of Scope

The PostgreSQL database does NOT store

- embeddings

- original PDF files

- image binaries

- audio

- video

- LLM prompts

- LLM responses

- cache

These responsibilities belong to external systems.

---

# 6. Overall Database Architecture

OmniBrain follows a Polyglot Persistence architecture.

Each storage system has exactly one responsibility.

PostgreSQL

↓

Metadata

Qdrant

↓

Embeddings

MinIO

↓

Binary Objects

Redis

↓

Caching

Neo4j

↓

Knowledge Graph

No storage responsibility overlaps another.

---

# 7. Polyglot Storage Strategy

## PostgreSQL

Primary relational database.

Stores metadata.

## Qdrant

Stores vector embeddings.

Supports semantic similarity search.

## MinIO

Stores original binary files.

## Redis

Stores query cache.

## Neo4j

Stores graph relationships.

Future feature.

---

# 8. PostgreSQL Responsibilities

PostgreSQL is the system of record.

Responsibilities include

Authentication

Authorization

Knowledge Metadata

Document Hierarchy

Structured Data Metadata

Query History

Audit

Feedback

Relational Integrity

---

# 9. External Storage Responsibilities

Qdrant

Stores only embeddings.

MinIO

Stores only original files.

Redis

Stores temporary cache.

Neo4j

Stores graph relationships.

---

# 10. Database Schemas

The database consists of five schemas.

auth

knowledge

structured

query_engine

audit

Each schema is independently maintained.

Cross-schema relationships are permitted only through foreign keys.

---

# 11. Data Lifecycle

Every document follows this lifecycle.

Upload

↓

Parser

↓

Metadata Extraction

↓

PostgreSQL

↓

OCR (if required)

↓

Chunking

↓

Embedding Generation

↓

Qdrant

↓

Retrieval

↓

Metadata Hydration

↓

Evidence Fusion

↓

LLM

↓

User Response

↓

Query Logging

↓

Audit

---

# 12. Entity Design

Every entity in the system has a clearly defined responsibility.

Each entity specification includes

Purpose

Columns

Primary Key

Foreign Keys

Constraints

Indexes

Relationships

Lifecycle

Future Extensions

Each entity will be documented individually.

---

# 13. Relationship Design

Relationships follow Third Normal Form.

One-to-One

Used sparingly.

One-to-Many

Preferred.

Many-to-Many

Resolved through junction tables.

Circular dependencies are prohibited.

---

# 14. Security Design

Authentication handled through FastAPI.

Passwords stored only as hashes.

No plaintext credentials.

Least privilege principle.

Schema-level separation.

Audit logging for sensitive operations.

---

# 15. Performance Strategy

Use normalized storage.

Avoid duplicate metadata.

Use composite indexes for common query paths.

Use GIN indexes for text search.

Use BRIN indexes for append-only logs.

Never store embeddings inside PostgreSQL.

---

# 16. Index Strategy

Every foreign key receives an index.

Primary keys create implicit B-tree indexes.

Composite indexes are created only for frequently executed queries.

Index usage will be monitored through PostgreSQL query statistics.

---

# 17. Backup Strategy

Daily backup.

Point-in-Time Recovery (PITR).

Weekly verification.

Monthly restore testing.

---

# 18. Scaling Strategy

Current Architecture

Single PostgreSQL instance.

Future

Read replicas.

Connection pooling.

Partitioning.

Horizontal object storage scaling.

Neo4j integration.

---

# 19. Future Enhancements

Multi-tenancy

Document version branching

Workflow engine

Background job queue

Distributed ingestion

Semantic cache optimization

Knowledge graph synchronization

Advanced audit analytics

---

END OF DOCUMENT