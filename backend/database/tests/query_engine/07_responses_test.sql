-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: responses_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/07_responses.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'responses'
    ) THEN
        RAISE NOTICE 'PASS : responses table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : responses table is missing.';
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
          AND table_name = 'responses'
          AND column_name = 'response_text'
    ) THEN
        RAISE NOTICE 'PASS : response_text column exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : response_text column is missing.';
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
          AND constraint_name = 'fk_response_query'
    ) THEN
        RAISE NOTICE 'PASS : fk_response_query exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_response_query is missing.';
    END IF;
END;
$$;
