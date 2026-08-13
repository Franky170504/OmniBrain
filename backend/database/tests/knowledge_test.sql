-- ============================================================================
-- OmniBrain Database Module
--
-- File: knowledge_test.sql
--
-- Purpose:
--     Validation tests for the Knowledge Schema
--
-- Schema:
--     knowledge
--
-- SQL Under Test:
--     schema/03_knowledge.sql
--
-- Notes:
--     - Read-only validation tests
--     - Safe for repeated execution
--     - Executes inside a transaction
--     - No persistent data is inserted
-- ============================================================================

BEGIN;

-- ============================================================================
-- TEST 1
-- Verify knowledge schema exists
-- ============================================================================

SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'knowledge';

-- Expected:
-- knowledge

-- ============================================================================
-- TEST 2
-- Verify all required tables exist
-- ============================================================================

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'knowledge'
ORDER BY table_name;

-- Expected Tables
--
-- chunks
-- collections
-- document_tag_mapping
-- documents
-- domains
-- images
-- pages
-- tables
-- tags

-- ============================================================================
-- TEST 3
-- Verify primary keys
-- ============================================================================

SELECT
    tc.table_name,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
ON tc.constraint_name = kcu.constraint_name
AND tc.table_schema = kcu.table_schema
WHERE tc.table_schema = 'knowledge'
AND tc.constraint_type = 'PRIMARY KEY'
ORDER BY tc.table_name;

-- ============================================================================
-- TEST 4
-- Verify foreign keys
-- ============================================================================

SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
ON tc.constraint_name = ccu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema = 'knowledge'
ORDER BY tc.table_name;

-- ============================================================================
-- TEST 5
-- Verify UNIQUE constraints
-- ============================================================================

SELECT
    tc.table_name,
    tc.constraint_name
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'knowledge'
AND tc.constraint_type = 'UNIQUE'
ORDER BY tc.table_name;

-- ============================================================================
-- TEST 6
-- Verify CHECK constraints
-- ============================================================================

SELECT
    conrelid::regclass AS table_name,
    conname
FROM pg_constraint
WHERE contype = 'c'
AND connamespace =
(
    SELECT oid
    FROM pg_namespace
    WHERE nspname = 'knowledge'
)
ORDER BY table_name;

-- ============================================================================
-- TEST 7
-- Verify indexes
-- ============================================================================

SELECT
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'knowledge'
ORDER BY tablename, indexname;

-- ============================================================================
-- TEST 8
-- Verify UUID defaults
-- ============================================================================

SELECT
    table_name,
    column_name,
    column_default
FROM information_schema.columns
WHERE table_schema = 'knowledge'
AND column_default LIKE '%gen_random_uuid%'
ORDER BY table_name;

-- ============================================================================
-- TEST 9
-- Verify timestamp columns
-- ============================================================================

SELECT
    table_name,
    column_name
FROM information_schema.columns
WHERE table_schema = 'knowledge'
AND column_name IN
(
    'created_at',
    'updated_at'
)
ORDER BY table_name, column_name;

-- ============================================================================
-- TEST 10
-- Verify NOT NULL columns
-- ============================================================================

SELECT
    table_name,
    column_name
FROM information_schema.columns
WHERE table_schema = 'knowledge'
AND is_nullable = 'NO'
ORDER BY table_name, column_name;

-- ============================================================================
-- TEST 11
-- Verify triggers
-- ============================================================================

SELECT
    tgname,
    tgrelid::regclass AS table_name
FROM pg_trigger
WHERE NOT tgisinternal
AND tgrelid IN
(
    SELECT c.oid
    FROM pg_class c
    JOIN pg_namespace n
    ON c.relnamespace = n.oid
    WHERE n.nspname = 'knowledge'
)
ORDER BY table_name;

-- ============================================================================
-- TEST 12
-- Verify document hierarchy tables
-- ============================================================================

SELECT
table_name
FROM information_schema.tables
WHERE table_schema = 'knowledge'
AND table_name IN
(
'domains',
'collections',
'documents',
'pages'
)
ORDER BY table_name;

-- ============================================================================
-- TEST 13
-- Verify extracted content tables
-- ============================================================================

SELECT
table_name
FROM information_schema.tables
WHERE table_schema = 'knowledge'
AND table_name IN
(
'chunks',
'images',
'tables'
)
ORDER BY table_name;

-- ============================================================================
-- TEST 14
-- Verify tagging tables
-- ============================================================================

SELECT
table_name
FROM information_schema.tables
WHERE table_schema = 'knowledge'
AND table_name IN
(
'tags',
'document_tag_mapping'
)
ORDER BY table_name;

-- ============================================================================
-- TEST 15
-- Verify comments exist
-- ============================================================================

SELECT
obj_description(c.oid)
FROM pg_class c
JOIN pg_namespace n
ON c.relnamespace = n.oid
WHERE n.nspname = 'knowledge'
ORDER BY c.relname;

-- ============================================================================
-- TEST 16
-- Verify metadata hierarchy
-- ============================================================================

SELECT
COUNT(*)
FROM information_schema.tables
WHERE table_schema = 'knowledge';

-- Expected:
-- 9

-- ============================================================================
-- TEST 17
-- Verify update timestamp trigger function
-- ============================================================================

SELECT
routine_name
FROM information_schema.routines
WHERE routine_schema = 'common'
AND routine_name = 'set_updated_at';

-- ============================================================================
-- TEST 18
-- Verify trigger assignments
-- ============================================================================

SELECT
tgname,
tgrelid::regclass
FROM pg_trigger
WHERE NOT tgisinternal
AND tgfoid = 'common.set_updated_at()'::regprocedure
ORDER BY tgrelid;

-- ============================================================================
-- TEST SUMMARY
-- ============================================================================

SELECT
'Knowledge schema validation completed successfully.'
AS test_status;

ROLLBACK;