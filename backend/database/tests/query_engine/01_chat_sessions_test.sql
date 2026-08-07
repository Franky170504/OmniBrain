-- ============================================================================
-- OmniBrain Query Engine Schema Test Suite
-- File: chat_sessions_test.sql
-- Schema: query_engine
-- Under test: backend/database/schema/06_query_engine/01_chat_sessions.sql
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.schemata
        WHERE schema_name = 'query_engine'
    ) THEN
        RAISE NOTICE 'PASS : query_engine schema exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : query_engine schema does not exist.';
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
          AND table_name = 'chat_sessions'
    ) THEN
        RAISE NOTICE 'PASS : chat_sessions table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : chat_sessions table is missing.';
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
          AND table_name = 'chat_sessions'
          AND column_name = 'session_title'
    ) THEN
        RAISE NOTICE 'PASS : session_title column exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : session_title column is missing.';
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
          AND t.typname = 'session_status_enum'
    ) THEN
        RAISE NOTICE 'PASS : session_status_enum type exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : session_status_enum type is missing.';
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
          AND constraint_name = 'fk_chat_session_user'
    ) THEN
        RAISE NOTICE 'PASS : fk_chat_session_user exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : fk_chat_session_user is missing.';
    END IF;
END;
$$;
