-- ============================================================================
-- OmniBrain Database Module
--
-- File: auth_test.sql
--
-- Purpose:
--     Enterprise validation tests for the Authentication Schema
--
-- Schema:
--     auth
--
-- SQL Under Test:
--     schema/02_auth.sql
--
-- Notes:
--      Safe to execute multiple times
--      Executes inside a transaction
--      Rolls back automatically
--      Prints PASS/FAIL messages
-- ============================================================================

BEGIN;

DO
$$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '======================================================';
    RAISE NOTICE '      OmniBrain Authentication Schema Test Suite';
    RAISE NOTICE '======================================================';
    RAISE NOTICE '';
END;
$$;

-- ============================================================================
-- TEST 1
-- Verify auth schema exists
-- ============================================================================

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.schemata
        WHERE schema_name = 'auth'
    ) THEN
        RAISE NOTICE 'PASS : Auth schema exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : Auth schema does not exist.';
    END IF;
END;
$$;

-- ============================================================================
-- TEST 2
-- Verify roles table exists
-- ============================================================================

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'auth'
          AND table_name = 'roles'
    ) THEN
        RAISE NOTICE 'PASS : roles table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : roles table is missing.';
    END IF;
END;
$$;

-- ============================================================================
-- TEST 3
-- Verify users table exists
-- ============================================================================

DO
$$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'auth'
          AND table_name = 'users'
    ) THEN
        RAISE NOTICE 'PASS : users table exists.';
    ELSE
        RAISE EXCEPTION 'FAIL : users table is missing.';
    END IF;
END;
$$;

-- ============================================================================
-- TEST 4
-- Verify seeded roles
-- ============================================================================

DO
$$
DECLARE
    role_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO role_count
    FROM auth.roles
    WHERE role_name IN
    (
        'Admin',
        'Editor',
        'Viewer'
    );

    IF role_count = 3 THEN
        RAISE NOTICE 'PASS : Default roles seeded successfully.';
    ELSE
        RAISE EXCEPTION
        'FAIL : Expected 3 default roles but found %.',
        role_count;
    END IF;

END;
$$;

-- ============================================================================
-- TEST 5
-- Verify UUID generation
-- ============================================================================

DO
$$
DECLARE
    generated_uuid UUID;
BEGIN

    INSERT INTO auth.users
    (
        role_id,
        email,
        full_name
    )
    VALUES
    (
        (
            SELECT role_id
            FROM auth.roles
            WHERE role_name = 'Viewer'
        ),
        'uuid_test@omnibrain.ai',
        'UUID Validation User'
    )
    RETURNING user_id
    INTO generated_uuid;

    IF generated_uuid IS NOT NULL THEN

        RAISE NOTICE
        'PASS : UUID generated successfully (%).',
        generated_uuid;

    ELSE

        RAISE EXCEPTION
        'FAIL : UUID generation failed.';

    END IF;

END;
$$;

-- ============================================================================
-- TEST 6
-- Verify created_at default
-- ============================================================================

DO
$$
DECLARE
    created_timestamp TIMESTAMPTZ;
BEGIN

    SELECT created_at
    INTO created_timestamp
    FROM auth.users
    WHERE email='uuid_test@omnibrain.ai';

    IF created_timestamp IS NOT NULL THEN

        RAISE NOTICE
        'PASS : created_at assigned automatically.';

    ELSE

        RAISE EXCEPTION
        'FAIL : created_at is NULL.';

    END IF;

END;
$$;

-- ============================================================================
-- PART 1 COMPLETE
-- Remaining tests:
--
-- • Duplicate email validation
-- • Invalid email validation
-- • Foreign key validation
-- • CHECK constraints
-- • Trigger validation
-- • updated_at validation
-- • Index validation
-- • Summary
-- • Rollback
-- ============================================================================

-- ============================================================================
-- TEST 7
-- Verify user insertion
-- ============================================================================

DO
$$
DECLARE
    user_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO user_count
    FROM auth.users
    WHERE email = 'uuid_test@omnibrain.ai';

    IF user_count = 1 THEN
        RAISE NOTICE 'PASS : User inserted successfully.';
    ELSE
        RAISE EXCEPTION
        'FAIL : User insertion validation failed.';
    END IF;

END;
$$;

-- ============================================================================
-- TEST 8
-- Verify default values
-- ============================================================================

DO
$$
DECLARE
    active_status BOOLEAN;
BEGIN

    SELECT
        is_active
    INTO
        active_status
    FROM auth.users
    WHERE email = 'uuid_test@omnibrain.ai';

    IF active_status = TRUE THEN

        RAISE NOTICE
        'PASS : is_active default value applied.';

    ELSE

        RAISE EXCEPTION
        'FAIL : is_active default value incorrect.';

    END IF;

END;
$$;

-- ============================================================================
-- TEST 9
-- Verify duplicate email constraint
-- ============================================================================

DO
$$
BEGIN

    BEGIN

        INSERT INTO auth.users
        (
            role_id,
            email,
            full_name
        )
        VALUES
        (
            (
                SELECT role_id
                FROM auth.roles
                WHERE role_name = 'Viewer'
            ),
            'uuid_test@omnibrain.ai',
            'Duplicate Email User'
        );

        RAISE EXCEPTION
        'FAIL : Duplicate email was accepted.';

    EXCEPTION

        WHEN unique_violation THEN

            RAISE NOTICE
            'PASS : Duplicate email correctly rejected.';

    END;

END;
$$;

-- ============================================================================
-- TEST 10
-- Verify invalid email format
-- ============================================================================

DO
$$
BEGIN

    BEGIN

        INSERT INTO auth.users
        (
            role_id,
            email,
            full_name
        )
        VALUES
        (
            (
                SELECT role_id
                FROM auth.roles
                WHERE role_name='Viewer'
            ),
            'invalid-email',
            'Invalid Email User'
        );

        RAISE EXCEPTION
        'FAIL : Invalid email accepted.';

    EXCEPTION

        WHEN check_violation THEN

            RAISE NOTICE
            'PASS : Invalid email rejected by CHECK constraint.';

    END;

END;
$$;

-- ============================================================================
-- TEST 11
-- Verify empty full_name validation
-- ============================================================================

DO
$$
BEGIN

    BEGIN

        INSERT INTO auth.users
        (
            role_id,
            email,
            full_name
        )
        VALUES
        (
            (
                SELECT role_id
                FROM auth.roles
                WHERE role_name='Viewer'
            ),
            'empty_name@omnibrain.ai',
            ''
        );

        RAISE EXCEPTION
        'FAIL : Empty full_name accepted.';

    EXCEPTION

        WHEN check_violation THEN

            RAISE NOTICE
            'PASS : Empty full_name rejected.';

    END;

END;
$$;

-- ============================================================================
-- END OF PART 2
--
-- Remaining Tests
--
-- • Invalid role_id foreign key
-- • Delete restrictions
-- • updated_at trigger validation
-- • Index validation
-- • Constraint validation
-- • Final summary
-- • ROLLBACK
-- ============================================================================


-- ============================================================================
-- TEST 12
-- Verify Foreign Key Constraint (role_id)
-- ============================================================================

DO
$$
BEGIN

    BEGIN

        INSERT INTO auth.users
        (
            role_id,
            email,
            full_name
        )
        VALUES
        (
            gen_random_uuid(),
            'invalid_fk@omnibrain.ai',
            'Invalid FK User'
        );

        RAISE EXCEPTION
        'FAIL : Invalid role_id accepted.';

    EXCEPTION

        WHEN foreign_key_violation THEN

            RAISE NOTICE
            'PASS : Foreign key constraint working correctly.';

    END;

END;
$$;

-- ============================================================================
-- TEST 13
-- Verify DELETE Restriction on roles
-- ============================================================================

DO
$$
DECLARE
    viewer_role UUID;
BEGIN

    SELECT role_id
    INTO viewer_role
    FROM auth.roles
    WHERE role_name='Viewer';

    BEGIN

        DELETE
        FROM auth.roles
        WHERE role_id = viewer_role;

        RAISE EXCEPTION
        'FAIL : Referenced role deleted successfully.';

    EXCEPTION

        WHEN foreign_key_violation THEN

            RAISE NOTICE
            'PASS : Referenced role cannot be deleted.';

    END;

END;
$$;

-- ============================================================================
-- TEST 14
-- Verify updated_at Trigger
-- ============================================================================

DO
$$
DECLARE
    v_user_id UUID;
    old_updated_at TIMESTAMPTZ;
    new_updated_at TIMESTAMPTZ;
BEGIN

    INSERT INTO auth.users
    (
        role_id,
        email,
        full_name
    )
    VALUES
    (
        (
            SELECT role_id
            FROM auth.roles
            WHERE role_name='Viewer'
        ),
        'trigger_test@omnibrain.ai',
        'Trigger Test'
    )
    RETURNING
        user_id,
        updated_at
    INTO
        v_user_id,
        old_updated_at;

    PERFORM pg_sleep(1);

    UPDATE auth.users
    SET full_name = full_name || ' Updated'
    WHERE user_id = v_user_id;

    SELECT updated_at
    INTO new_updated_at
    FROM auth.users
    WHERE user_id = v_user_id;

    IF new_updated_at > old_updated_at THEN
        RAISE NOTICE
        'PASS : updated_at trigger executed successfully.';
    ELSE
        RAISE EXCEPTION
        'FAIL : updated_at trigger did not update timestamp.';
    END IF;

END;
$$;

-- ============================================================================
-- END OF PART 3
--
-- Remaining Tests
--
-- • Index validation
-- • Constraint validation
-- • Seed data validation
-- • Summary
-- • Rollback
--
-- ============================================================================

-- ============================================================================
-- TEST 16
-- Verify Indexes
-- ============================================================================

DO
$$
DECLARE

    idx_count INTEGER;

BEGIN

    SELECT COUNT(*)
    INTO idx_count
    FROM pg_indexes
    WHERE schemaname='auth';

    IF idx_count >= 4 THEN

        RAISE NOTICE
        'PASS : Indexes created successfully (% indexes found).',
        idx_count;

    ELSE

        RAISE EXCEPTION
        'FAIL : Expected indexes are missing. Only % found.',
        idx_count;

    END IF;

END;
$$;

-- ============================================================================
-- TEST 17
-- Verify Constraints
-- ============================================================================

DO
$$
DECLARE

    constraint_count INTEGER;

BEGIN

    SELECT COUNT(*)
    INTO constraint_count
    FROM information_schema.table_constraints
    WHERE table_schema='auth';

    IF constraint_count > 0 THEN

        RAISE NOTICE
        'PASS : Constraints detected (% constraints found).',
        constraint_count;

    ELSE

        RAISE EXCEPTION
        'FAIL : No constraints found in auth schema.';

    END IF;

END;
$$;

-- ============================================================================
-- TEST 18
-- Verify Seed Data
-- ============================================================================

DO
$$
DECLARE

    admin_exists BOOLEAN;
    editor_exists BOOLEAN;
    viewer_exists BOOLEAN;

BEGIN

    SELECT EXISTS
    (
        SELECT 1
        FROM auth.roles
        WHERE role_name='Admin'
    )
    INTO admin_exists;

    SELECT EXISTS
    (
        SELECT 1
        FROM auth.roles
        WHERE role_name='Editor'
    )
    INTO editor_exists;

    SELECT EXISTS
    (
        SELECT 1
        FROM auth.roles
        WHERE role_name='Viewer'
    )
    INTO viewer_exists;

    IF admin_exists
       AND editor_exists
       AND viewer_exists THEN

        RAISE NOTICE
        'PASS : Default roles verified successfully.';

    ELSE

        RAISE EXCEPTION
        'FAIL : Default role validation failed.';

    END IF;

END;
$$;

-- ============================================================================
-- TEST SUMMARY
-- ============================================================================

DO
$$
BEGIN

    RAISE NOTICE '';
    RAISE NOTICE '======================================================';
    RAISE NOTICE '      ALL AUTH SCHEMA TESTS COMPLETED SUCCESSFULLY';
    RAISE NOTICE '======================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Validated Components';
    RAISE NOTICE '--------------------';
    RAISE NOTICE '✓ Auth schema';
    RAISE NOTICE '✓ Roles table';
    RAISE NOTICE '✓ Users table';
    RAISE NOTICE '✓ Default roles';
    RAISE NOTICE '✓ UUID generation';
    RAISE NOTICE '✓ Default values';
    RAISE NOTICE '✓ UNIQUE constraints';
    RAISE NOTICE '✓ CHECK constraints';
    RAISE NOTICE '✓ Foreign keys';
    RAISE NOTICE '✓ Delete restrictions';
    RAISE NOTICE '✓ Update trigger';
    RAISE NOTICE '✓ Indexes';
    RAISE NOTICE '✓ Database constraints';
    RAISE NOTICE '';
END;
$$;

-- ============================================================================
-- CLEANUP
-- ============================================================================

ROLLBACK;

-- ============================================================================
-- End of File
-- ============================================================================
