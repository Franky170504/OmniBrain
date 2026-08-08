-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: lookup_tables_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/00_lookup_tables.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'query_statuses'
    ) THEN
        RAISE NOTICE 'PASS : query_statuses table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : query_statuses table is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'query_intents'
    ) THEN
        RAISE NOTICE 'PASS : query_intents table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : query_intents table is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'retrieval_strategies'
    ) THEN
        RAISE NOTICE 'PASS : retrieval_strategies table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : retrieval_strategies table is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'query_priorities'
    ) THEN
        RAISE NOTICE 'PASS : query_priorities table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : query_priorities table is missing.';
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
          AND table_name = 'query_priorities'
          AND column_name = 'priority_code'
    ) THEN
        RAISE NOTICE 'PASS : priority_code column exists in query_priorities.';
    ELSE
        RAISE EXCEPTION 'FAIL : priority_code column is missing from query_priorities.';
    END IF;
END;
$$;
