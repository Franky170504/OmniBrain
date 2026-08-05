# Authentication Schema Specification

## Schema

auth

---

# Purpose

The authentication schema manages user identity and authorization.

This schema is intentionally independent from the Knowledge Base.

It should remain small, stable, and highly secure.

Responsibilities include:

- User accounts
- Role management
- Authentication metadata
- Authorization support

It does NOT store:

- Documents
- Chunks
- Images
- Queries
- Embeddings
- OCR metadata

---

# Tables

## roles

Purpose

Defines every role supported by OmniBrain.

Examples

- Admin
- Editor
- Viewer

Expected Growth

Very Low

Estimated Records

< 50

---

## users

Purpose

Stores authenticated human users.

Every user belongs to exactly one role.

Expected Growth

Medium

Estimated Records

1,000–100,000+

---

# Relationship

roles (1)

↓

users (N)

---

# Index Strategy

roles

Primary Key

Unique(role_name)

users

Primary Key

Unique(email)

Foreign Key(role_id)

Index(is_active)

---

# Security

Passwords are NOT stored in this table.

Authentication provider handles password hashing.

Only password hashes should ever be persisted.

---

# Future Extensions

Possible future additions

- last_login_at
- failed_login_attempts
- account_status
- profile_picture
- organization_id
- MFA support