-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: indexes_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/11_indexes.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'query_engine'
          AND indexname = 'idx_conversation_turns_session_created'
    ) THEN
        RAISE NOTICE 'PASS : idx_conversation_turns_session_created exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : idx_conversation_turns_session_created is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'query_engine'
          AND indexname = 'uq_final_response'
    ) THEN
        RAISE NOTICE 'PASS : uq_final_response exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : uq_final_response is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'query_engine'
          AND indexname = 'uq_agent_tool_call'
    ) THEN
        RAISE NOTICE 'PASS : uq_agent_tool_call exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : uq_agent_tool_call is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'query_engine'
          AND indexname = 'idx_metrics_scope_created'
    ) THEN
        RAISE NOTICE 'PASS : idx_metrics_scope_created exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : idx_metrics_scope_created is missing.';
    END IF;
END;
$$;
