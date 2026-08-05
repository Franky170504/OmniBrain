# Authentication Schema Test Plan

## Goal

Validate correctness of the authentication schema.

---

# Test Cases

## Table Creation

- roles created successfully
- users created successfully

---

## Primary Keys

Insert role

Verify UUID generated.

Insert user

Verify UUID generated.

---

## Unique Constraints

Attempt duplicate role_name.

Expected

FAIL

Attempt duplicate email.

Expected

FAIL

---

## Foreign Key

Insert user with invalid role_id.

Expected

FAIL

---

## Default Values

Insert user without is_active.

Expected

TRUE

Insert timestamps.

Expected

CURRENT_TIMESTAMP

---

## Delete Rule

Delete role referenced by users.

Expected

FAIL

---

## Update Rule

Update role_id.

Expected

CASCADE

---

## Performance

Insert 10,000 users.

Measure

Insert time

Query time

Index usage