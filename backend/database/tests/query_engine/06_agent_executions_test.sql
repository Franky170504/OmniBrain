-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: agent_executions_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/06_agent_executions.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'agent_executions'
    ) THEN
        RAISE NOTICE 'PASS : agent_executions table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : agent_executions table is missing.';
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
          AND table_name = 'agent_executions'
          AND column_name = 'agent_name'
    ) THEN
        RAISE NOTICE 'PASS : agent_name column exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : agent_name column is missing.';
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
          AND constraint_name = 'fk_agent_execution_query'
    ) THEN
        RAISE NOTICE 'PASS : fk_agent_execution_query exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_agent_execution_query is missing.';
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
          AND table_name = 'agent_executions'
          AND constraint_type = 'UNIQUE'
          AND constraint_name = 'uq_execution_sequence'
    ) THEN
        RAISE NOTICE 'PASS : uq_execution_sequence exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : uq_execution_sequence is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.triggers
        WHERE event_object_schema = 'query_engine'
          AND event_object_table = 'agent_executions'
          AND trigger_name = 'trg_agent_executions_updated_at'
    ) THEN
        RAISE NOTICE 'PASS : trg_agent_executions_updated_at trigger exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : trg_agent_executions_updated_at trigger is missing.';
    END IF;
END;
$$;
