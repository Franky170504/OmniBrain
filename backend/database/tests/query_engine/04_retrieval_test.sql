-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: retrieval_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/04_retrieved_context.sql and 05_context_items.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'retrieved_context'
    ) THEN
        RAISE NOTICE 'PASS : retrieved_context table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : retrieved_context table is missing.';
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
          AND table_name = 'context_items'
    ) THEN
        RAISE NOTICE 'PASS : context_items table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : context_items table is missing.';
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
          AND table_name = 'context_items'
          AND column_name = 'citation_label'
    ) THEN
        RAISE NOTICE 'PASS : citation_label column exists in context_items.';
    ELSE
        RAISE EXCEPTION 'FAIL : citation_label column is missing from context_items.';
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
          AND constraint_name = 'fk_retrieval_query'
    ) THEN
        RAISE NOTICE 'PASS : fk_retrieval_query exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_retrieval_query is missing.';
    END IF;
END;
$$;
