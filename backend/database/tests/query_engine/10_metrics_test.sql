-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: metrics_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/10_metrics.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'metrics'
    ) THEN
        RAISE NOTICE 'PASS : metrics table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : metrics table is missing.';
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
          AND table_name = 'metrics'
          AND column_name = 'metric_scope'
    ) THEN
        RAISE NOTICE 'PASS : metric_scope column exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : metric_scope column is missing.';
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
          AND constraint_name = 'fk_metrics_query'
    ) THEN
        RAISE NOTICE 'PASS : fk_metrics_query exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_metrics_query is missing.';
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
          AND constraint_name = 'fk_metrics_agent_execution'
    ) THEN
        RAISE NOTICE 'PASS : fk_metrics_agent_execution exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_metrics_agent_execution is missing.';
    END IF;
END;
$$;
