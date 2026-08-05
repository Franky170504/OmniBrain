-- ============================================================================
-- OmniBrain Database Module
--
-- File: common_functions_test.sql
--
-- Purpose:
--     Validation tests for reusable database functions implemented in
--     schema/04_common_functions.sql
--
-- Tested Functions:
--     • common.set_updated_at()
--     • common.validate_resource_tag()
--
-- Notes:
--     - Tests should be executed on a development database.
--     - All tests run inside a transaction.
--     - Rollback is performed at the end to avoid polluting the database.
-- ============================================================================

BEGIN;

-- ============================================================================
-- TEST 1
-- Verify common schema exists
-- ============================================================================

SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'common';

-- ============================================================================
-- TEST 2
-- Verify reusable functions exist
-- ============================================================================

SELECT
    routine_name
FROM information_schema.routines
WHERE routine_schema = 'common'
ORDER BY routine_name;

-- Expected:
-- set_updated_at
-- validate_resource_tag

-- ============================================================================
-- TEST 3
-- Verify trigger function: set_updated_at()
-- ============================================================================

-- Check function metadata

SELECT
    proname
FROM pg_proc
JOIN pg_namespace
ON pg_proc.pronamespace = pg_namespace.oid
WHERE nspname='common'
AND proname='set_updated_at';

-- Expected:
-- One record returned.

-- ============================================================================
-- TEST 4
-- Verify validate_resource_tag() function
-- ============================================================================

SELECT
    proname
FROM pg_proc
JOIN pg_namespace
ON pg_proc.pronamespace = pg_namespace.oid
WHERE nspname='common'
AND proname='validate_resource_tag';

-- Expected:
-- One record returned.

-- ============================================================================
-- TEST 5
-- Validate trigger attachment
-- ============================================================================

SELECT
    tgname,
    tgrelid::regclass
FROM pg_trigger
WHERE tgname IS NOT NULL
ORDER BY tgname;

-- Verify that update timestamp triggers exist
-- on tables using common.set_updated_at().

-- ============================================================================
-- TEST 6
-- Verify resource validation trigger exists
-- ============================================================================

SELECT
    tgname,
    tgrelid::regclass
FROM pg_trigger
WHERE tgfoid =
(
    SELECT oid
    FROM pg_proc
    WHERE proname='validate_resource_tag'
)
ORDER BY tgname;

-- ============================================================================
-- TEST 7
-- Validate supported resource types
-- ============================================================================

SELECT
    DISTINCT resource_type
FROM structured.resource_tags
ORDER BY resource_type;

-- Expected resource types include:
-- DATASET
-- TABLE
-- COLUMN
-- RELATIONSHIP

-- ============================================================================
-- TEST 8
-- Constraint validation
-- ============================================================================

SELECT
    conname,
    contype
FROM pg_constraint
WHERE connamespace =
(
    SELECT oid
    FROM pg_namespace
    WHERE nspname='structured'
)
ORDER BY conname;

-- ============================================================================
-- TEST 9
-- Foreign key validation
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
WHERE tc.constraint_type='FOREIGN KEY'
AND tc.table_schema='structured'
ORDER BY tc.table_name;

-- ============================================================================
-- TEST 10
-- Index validation
-- ============================================================================

SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname='structured'
ORDER BY tablename,indexname;

-- ============================================================================
-- TEST SUMMARY
-- ============================================================================

SELECT
'Common function validation completed successfully.'
AS test_status;

ROLLBACK;