-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: conversation_turns_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/02_conversation_turns.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'query_engine'
          AND table_name = 'conversation_turns'
    ) THEN
        RAISE NOTICE 'PASS : conversation_turns table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : conversation_turns table is missing.';
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
          AND table_name = 'conversation_turns'
          AND column_name = 'sender_type'
    ) THEN
        RAISE NOTICE 'PASS : sender_type column exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : sender_type column is missing.';
    END IF;
END;
$$;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_type t
        JOIN pg_namespace n ON t.typnamespace = n.oid
        WHERE n.nspname = 'query_engine'
          AND t.typname = 'sender_type_enum'
    ) THEN
        RAISE NOTICE 'PASS : sender_type_enum exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : sender_type_enum is missing.';
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
          AND table_name = 'conversation_turns'
          AND constraint_type = 'UNIQUE'
          AND constraint_name = 'uq_conversation_turn'
    ) THEN
        RAISE NOTICE 'PASS : uq_conversation_turn exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : uq_conversation_turn is missing.';
    END IF;
END;
$$;
