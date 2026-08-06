-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: citations_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/08_citations.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'citations'
    ) THEN
        RAISE NOTICE 'PASS : citations table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : citations table is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_schema = 'query_engine'
          AND table_name = 'citations'
          AND constraint_type = 'UNIQUE'
          AND constraint_name = 'uq_response_citation_order'
    ) THEN
        RAISE NOTICE 'PASS : uq_response_citation_order exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : uq_response_citation_order is missing.';
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
          AND constraint_name = 'fk_citation_context_item'
    ) THEN
        RAISE NOTICE 'PASS : fk_citation_context_item exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_citation_context_item is missing.';
    END IF;
END;
$$;
