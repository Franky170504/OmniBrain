-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: feedback_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/09_feedback.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'feedback'
    ) THEN
        RAISE NOTICE 'PASS : feedback table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : feedback table is missing.';
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
          AND table_name = 'feedback'
          AND column_name = 'feedback_type'
    ) THEN
        RAISE NOTICE 'PASS : feedback_type column exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : feedback_type column is missing.';
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
          AND constraint_name = 'fk_feedback_user'
    ) THEN
        RAISE NOTICE 'PASS : fk_feedback_user exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_feedback_user is missing.';
    END IF;
END;
$$;
