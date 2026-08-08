-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: queries_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/03_queries.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'queries'
    ) THEN
        RAISE NOTICE 'PASS : queries table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : queries table is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'query_engine'
          AND table_name = 'queries'
          AND column_name = 'original_query'
    ) THEN
        RAISE NOTICE 'PASS : original_query column exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : original_query column is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.referential_constraints
        WHERE constraint_schema = 'query_engine'
          AND constraint_name = 'fk_query_status'
    ) THEN
        RAISE NOTICE 'PASS : fk_query_status exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_query_status is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.referential_constraints
        WHERE constraint_schema = 'query_engine'
          AND constraint_name = 'fk_query_intent'
    ) THEN
        RAISE NOTICE 'PASS : fk_query_intent exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_query_intent is missing.';
    END IF;
END;
$$;
