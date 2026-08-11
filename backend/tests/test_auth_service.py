import hashlib
import hmac
import json
import time
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.core.app_config import app_settings
from app.database.models.authentication.token_session import TokenSession
from app.database.models.authentication.user import User
from app.services.auth_service import AuthService, RateLimitExceeded


def make_fake_session(user=None, token_session=None, count=0, oldest=None):
    class FakeResult:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

        def scalar_one(self):
            return self.value

    class FakeSession:
        def __init__(self):
            self.user = user
            self.token_session = token_session
            self.count = count
            self.oldest = oldest
            self.added = []
            self.flushed = False
            self.executed = []

        def get(self, model, key):
            if model is User:
                return self.user if self.user and self.user.user_id == key else None
            if model is TokenSession:
                return self.token_session if self.token_session and self.token_session.token_id == key else None
            return None

        def add(self, obj):
            self.added.append(obj)

        def flush(self):
            self.flushed = True

        def execute(self, statement, params=None):
            stmt = str(statement)
            self.executed.append(stmt)
            if "pg_advisory_xact_lock" in stmt:
                return None
            if "FROM auth.roles" in stmt or "FROM roles" in stmt:
                return FakeResult(uuid.uuid4())
            if "count" in stmt and "auth_rate_limit_events" in stmt:
                return FakeResult(self.count)
            if "ORDER BY" in stmt and "auth_rate_limit_events" in stmt:
                return FakeResult(self.oldest)
            return FakeResult(None)

    return FakeSession()


class FakeTransaction:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakeDatabase:
    def __init__(self, session):
        self.session = session

    def transaction(self):
        return FakeTransaction(self.session)


def generate_token_with_fixed_jti(service, user_id, token_id, session):
    with patch("app.services.auth_service.uuid.uuid4", return_value=token_id):
        return service._generate_access_token(user_id, session)


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.previous_secret = app_settings.AUTH_JWT_SECRET
        self.previous_previous_secrets = app_settings.AUTH_JWT_PREVIOUS_JWT_SECRETS
        app_settings.AUTH_JWT_SECRET = "test-only-signing-secret"
        app_settings.AUTH_JWT_PREVIOUS_JWT_SECRETS = None

    def tearDown(self):
        app_settings.AUTH_JWT_SECRET = self.previous_secret
        app_settings.AUTH_JWT_PREVIOUS_JWT_SECRETS = self.previous_previous_secrets

    def test_token_session_is_created_with_jti(self):
        user_id = uuid.uuid4()
        fake_session = make_fake_session()
        service = AuthService(database_service=FakeDatabase(fake_session))

        token = service._generate_access_token(user_id, fake_session)
        self.assertEqual(len(fake_session.added), 1)
        token_session = fake_session.added[0]
        self.assertIsInstance(token_session, TokenSession)
        self.assertEqual(str(token_session.token_id), service._parse_access_token(token)[1])
        self.assertIsNotNone(token_session.issued_at)
        self.assertIsNotNone(token_session.expires_at)

    def test_valid_session_authenticates(self):
        user_id = uuid.uuid4()
        token_id = uuid.uuid4()
        user = User(user_id=user_id, role_id=uuid.uuid4(), email="test@example.com", full_name="Test", password_hash="hash", is_active=True)
        token_session = TokenSession(token_id=token_id, user_id=user_id, issued_at=datetime.now(timezone.utc), expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600))
        fake_session = make_fake_session(user=user, token_session=token_session)
        service = AuthService(database_service=FakeDatabase(fake_session))

        token = generate_token_with_fixed_jti(service, user_id, token_id, fake_session)
        self.assertEqual(service.authenticate(token), str(user_id))

    def test_revoked_session_is_rejected(self):
        user_id = uuid.uuid4()
        token_id = uuid.uuid4()
        user = User(user_id=user_id, role_id=uuid.uuid4(), email="test@example.com", full_name="Test", password_hash="hash", is_active=True)
        token_session = TokenSession(token_id=token_id, user_id=user_id, issued_at=datetime.now(timezone.utc), expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600), revoked_at=datetime.now(timezone.utc))
        fake_session = make_fake_session(user=user, token_session=token_session)
        service = AuthService(database_service=FakeDatabase(fake_session))

        token = generate_token_with_fixed_jti(service, user_id, token_id, fake_session)
        with self.assertRaisesRegex(ValueError, "Invalid access token"):
            service.authenticate(token)

    def test_missing_session_is_rejected(self):
        user_id = uuid.uuid4()
        user = User(user_id=user_id, role_id=uuid.uuid4(), email="test@example.com", full_name="Test", password_hash="hash", is_active=True)
        token = AuthService(database_service=FakeDatabase(make_fake_session()))._generate_access_token(user_id, make_fake_session())
        service = AuthService(database_service=FakeDatabase(make_fake_session(user=user, token_session=None)))

        with self.assertRaisesRegex(ValueError, "Invalid access token"):
            service.authenticate(token)

    def test_logout_revokes_current_token_idempotently(self):
        user_id = uuid.uuid4()
        token_id = uuid.uuid4()
        token_session = TokenSession(token_id=token_id, user_id=user_id, issued_at=datetime.now(timezone.utc), expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600))
        fake_session = make_fake_session(token_session=token_session)
        service = AuthService(database_service=FakeDatabase(fake_session))

        token = generate_token_with_fixed_jti(service, user_id, token_id, fake_session)
        service.logout(token)
        self.assertIsNotNone(token_session.revoked_at)
        previous_revoked_at = token_session.revoked_at
        service.logout(token)
        self.assertEqual(previous_revoked_at, token_session.revoked_at)

    def test_logout_revoked_token_cannot_authenticate(self):
        user_id = uuid.uuid4()
        token_id = uuid.uuid4()
        user = User(user_id=user_id, role_id=uuid.uuid4(), email="test@example.com", full_name="Test", password_hash="hash", is_active=True)
        token_session = TokenSession(token_id=token_id, user_id=user_id, issued_at=datetime.now(timezone.utc), expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600), revoked_at=datetime.now(timezone.utc))
        fake_session = make_fake_session(user=user, token_session=token_session)
        service = AuthService(database_service=FakeDatabase(fake_session))

        token = generate_token_with_fixed_jti(service, user_id, token_id, fake_session)
        with self.assertRaisesRegex(ValueError, "Invalid access token"):
            service.authenticate(token)

    def test_legacy_token_without_jti_authenticates(self):
        user_id = uuid.uuid4()
        user = User(user_id=user_id, role_id=uuid.uuid4(), email="test@example.com", full_name="Test", password_hash="hash", is_active=True)
        service = AuthService(database_service=FakeDatabase(make_fake_session(user=user)))

        header = service._part(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
        payload = service._part(json.dumps({"sub": str(user_id), "type": "access", "iat": int(time.time()), "exp": int(time.time()) + 3600}, separators=(",", ":")).encode())
        signature = service._part(hmac.new(service._secret(), f"{header}.{payload}".encode("ascii"), hashlib.sha256).digest())
        token = f"{header}.{payload}.{signature}"

        self.assertEqual(service.authenticate(token), str(user_id))

    def test_expired_token_is_rejected(self):
        user_id = uuid.uuid4()
        service = AuthService(database_service=FakeDatabase(make_fake_session()))
        token = service._generate_access_token(user_id, make_fake_session())

        with patch("app.services.auth_service.time.time", return_value=time.time() + 7200):
            with self.assertRaisesRegex(ValueError, "Invalid access token"):
                service.authenticate(token)

    def test_malformed_token_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid access token"):
            AuthService().authenticate("not.a.token")

    def test_wrong_signature_is_rejected(self):
        user_id = uuid.uuid4()
        service = AuthService()
        token = service._generate_access_token(user_id, make_fake_session())
        bad_token = token[:-1] + ("A" if token[-1] != "A" else "B")

        with self.assertRaisesRegex(ValueError, "Invalid access token"):
            service.authenticate(bad_token)

    def test_wrong_algorithm_is_rejected(self):
        user_id = uuid.uuid4()
        service = AuthService()
        header = service._part(json.dumps({"alg": "HS384", "typ": "JWT"}, separators=(",", ":")).encode())
        payload = service._part(json.dumps({"sub": str(user_id), "type": "access", "iat": int(time.time()), "exp": int(time.time()) + 3600, "jti": str(uuid.uuid4())}, separators=(",", ":")).encode())
        signature = service._part(hmac.new(service._secret(), f"{header}.{payload}".encode("ascii"), hashlib.sha256).digest())
        token = f"{header}.{payload}.{signature}"

        with self.assertRaisesRegex(ValueError, "Invalid access token"):
            service.authenticate(token)

    def test_wrong_token_type_is_rejected(self):
        user_id = uuid.uuid4()
        service = AuthService()
        header = service._part(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
        payload = service._part(json.dumps({"sub": str(user_id), "type": "refresh", "iat": int(time.time()), "exp": int(time.time()) + 3600, "jti": str(uuid.uuid4())}, separators=(",", ":")).encode())
        signature = service._part(hmac.new(service._secret(), f"{header}.{payload}".encode("ascii"), hashlib.sha256).digest())
        token = f"{header}.{payload}.{signature}"

        with self.assertRaisesRegex(ValueError, "Invalid access token"):
            service.authenticate(token)

    def test_secret_rotation_verifies_previous_secret(self):
        user_id = uuid.uuid4()
        token_id = uuid.uuid4()
        original_secret = "old-secret"
        new_secret = "new-secret"
        app_settings.AUTH_JWT_SECRET = original_secret
        service = AuthService()
        user = User(user_id=user_id, role_id=uuid.uuid4(), email="test@example.com", full_name="Test", password_hash="hash", is_active=True)
        token_session = TokenSession(token_id=token_id, user_id=user_id, issued_at=datetime.now(timezone.utc), expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600))
        token = generate_token_with_fixed_jti(service, user_id, token_id, make_fake_session(user=user, token_session=token_session))

        app_settings.AUTH_JWT_SECRET = new_secret
        app_settings.AUTH_JWT_PREVIOUS_JWT_SECRETS = original_secret
        service.database_service = FakeDatabase(make_fake_session(user=user, token_session=token_session))

        self.assertEqual(service.authenticate(token), str(user.user_id))

    def test_previous_secret_does_not_sign_new_tokens(self):
        app_settings.AUTH_JWT_SECRET = "current-secret"
        app_settings.AUTH_JWT_PREVIOUS_JWT_SECRETS = "old-secret"
        service = AuthService()

        self.assertEqual(service._secret(), b"current-secret")

    def test_removed_previous_secret_rejects_old_token(self):
        user_id = uuid.uuid4()
        token_id = uuid.uuid4()
        original_secret = "old-secret"
        app_settings.AUTH_JWT_SECRET = original_secret
        service = AuthService()
        user = User(user_id=user_id, role_id=uuid.uuid4(), email="test@example.com", full_name="Test", password_hash="hash", is_active=True)
        token_session = TokenSession(token_id=token_id, user_id=user_id, issued_at=datetime.now(timezone.utc), expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600))
        token = generate_token_with_fixed_jti(service, user_id, token_id, make_fake_session(user=user, token_session=token_session))

        app_settings.AUTH_JWT_SECRET = "new-secret"
        app_settings.AUTH_JWT_PREVIOUS_JWT_SECRETS = None
        service.database_service = FakeDatabase(make_fake_session(user=user, token_session=token_session))

        with self.assertRaisesRegex(ValueError, "Invalid access token"):
            service.authenticate(token)

    def test_missing_secret_is_rejected(self):
        app_settings.AUTH_JWT_SECRET = None

        with self.assertRaisesRegex(RuntimeError, "AUTH_JWT_SECRET"):
            AuthService()._secret()

    def test_rate_limit_derivation_does_not_include_password(self):
        request_key = AuthService().derive_rate_limit_key(
            endpoint="login",
            client_ip="127.0.0.1",
            normalized_email="user@example.com",
        )

        self.assertNotIn("password", request_key)

    def test_rate_limit_lock_is_used(self):
        fake_session = make_fake_session(count=0, oldest=datetime.now(timezone.utc))
        service = AuthService(database_service=FakeDatabase(fake_session))
        service._enforce_rate_limit(endpoint="login", request_key="rate-limit-key")

        self.assertTrue(any("pg_advisory_xact_lock" in sql for sql in fake_session.executed))

    def test_rate_limit_exceeded_returns_retry_after(self):
        oldest = datetime.now(timezone.utc) - timedelta(seconds=10)
        fake_session = make_fake_session(count=10, oldest=oldest)
        service = AuthService(database_service=FakeDatabase(fake_session))

        with self.assertRaises(RateLimitExceeded) as context:
            service._enforce_rate_limit(endpoint="login", request_key="rate-limit-key")

        self.assertGreaterEqual(context.exception.retry_after, 0)

    def test_rate_limit_cleanup_runs(self):
        fake_session = make_fake_session(count=0, oldest=datetime.now(timezone.utc))
        service = AuthService(database_service=FakeDatabase(fake_session))
        service._enforce_rate_limit(endpoint="login", request_key="rate-limit-key")

        self.assertTrue(any("DELETE FROM auth.auth_rate_limit_events" in sql for sql in fake_session.executed))


if __name__ == "__main__":
    unittest.main()
