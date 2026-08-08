-- ============================================================================
-- OmniBrain Database Module
--
-- File: structured_test.sql
--
-- Purpose:
--     Validation tests for the Structured Schema
--
-- Schema:
--     structured
--
-- SQL Under Test:
--     schema/05_structured.sql
--
-- Notes:
--     - Read-only validation tests
--     - Safe for repeated execution
--     - Runs inside a transaction
--     - No persistent data is inserted
-- ============================================================================

BEGIN;

-- ============================================================================
-- TEST 1
-- Verify structured schema exists
-- ============================================================================

SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'structured';

-- Expected:
-- structured

-- ============================================================================
-- TEST 2
-- Verify all required tables exist
-- ============================================================================

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'structured'
ORDER BY table_name;

-- Expected Tables
--
-- column_statistics
-- data_sources
-- dataset_columns
-- dataset_refresh_history
-- dataset_relationship_columns
-- dataset_relationships
-- dataset_statistics
-- dataset_tables
-- datasets
-- resource_tags
-- table_statistics
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
WHERE tc.table_schema='structured'
AND tc.constraint_type='PRIMARY KEY'
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
ON tc.constraint_name=kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
ON tc.constraint_name=ccu.constraint_name
WHERE tc.constraint_type='FOREIGN KEY'
AND tc.table_schema='structured'
ORDER BY tc.table_name;

-- ============================================================================
-- TEST 5
-- Verify unique constraints
-- ============================================================================

SELECT
    tc.table_name,
    tc.constraint_name
FROM information_schema.table_constraints tc
WHERE tc.table_schema='structured'
AND tc.constraint_type='UNIQUE'
ORDER BY tc.table_name;

-- ============================================================================
-- TEST 6
-- Verify CHECK constraints
-- ============================================================================

SELECT
    conrelid::regclass AS table_name,
    conname
FROM pg_constraint
WHERE contype='c'
AND connamespace=
(
    SELECT oid
    FROM pg_namespace
    WHERE nspname='structured'
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
WHERE schemaname='structured'
ORDER BY tablename,indexname;

-- ============================================================================
-- TEST 8
-- Verify UUID defaults
-- ============================================================================

SELECT
    table_name,
    column_name,
    column_default
FROM information_schema.columns
WHERE table_schema='structured'
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
WHERE table_schema='structured'
AND column_name IN
(
    'created_at',
    'updated_at'
)
ORDER BY table_name,column_name;

-- ============================================================================
-- TEST 10
-- Verify NOT NULL columns
-- ============================================================================

SELECT
    table_name,
    column_name
FROM information_schema.columns
WHERE table_schema='structured'
AND is_nullable='NO'
ORDER BY table_name,column_name;

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
    ON c.relnamespace=n.oid
    WHERE n.nspname='structured'
)
ORDER BY table_name;

-- ============================================================================
-- TEST 12
-- Verify row-level statistics tables
-- ============================================================================

SELECT
table_name
FROM information_schema.tables
WHERE table_schema='structured'
AND table_name IN
(
'dataset_statistics',
'table_statistics',
'column_statistics'
)
ORDER BY table_name;

-- ============================================================================
-- TEST 13
-- Verify relationship tables
-- ============================================================================

SELECT
table_name
FROM information_schema.tables
WHERE table_schema='structured'
AND table_name IN
(
'dataset_relationships',
'dataset_relationship_columns'
);

-- ============================================================================
-- TEST 14
-- Verify refresh history table
-- ============================================================================

SELECT
table_name
FROM information_schema.tables
WHERE table_schema='structured'
AND table_name='dataset_refresh_history';

-- ============================================================================
-- TEST 15
-- Verify tagging tables
-- ============================================================================

SELECT
table_name
FROM information_schema.tables
WHERE table_schema='structured'
AND table_name IN
(
'tags',
'resource_tags'
);

-- ============================================================================
-- TEST 16
-- Verify metadata hierarchy
-- ============================================================================

SELECT
COUNT(*)
FROM information_schema.tables
WHERE table_schema='structured';

-- Expected:
-- 12

-- ============================================================================
-- TEST 17
-- Verify ownership functions/triggers
-- ============================================================================

SELECT
routine_name
FROM information_schema.routines
WHERE routine_schema='common'
ORDER BY routine_name;

-- ============================================================================
-- TEST SUMMARY
-- ============================================================================

SELECT
'Structured schema validation completed successfully.'
AS test_status;

ROLLBACK;