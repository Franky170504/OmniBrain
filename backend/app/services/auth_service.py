from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from sqlalchemy import func, select, text

from app.core.app_config import app_settings
from app.database.database_service import DatabaseService
from app.database.models.authentication.auth_rate_limit_event import AuthRateLimitEvent
from app.database.models.authentication.role import Role
from app.database.models.authentication.token_session import TokenSession
from app.database.models.authentication.user import User


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__("Rate limit exceeded")


class AuthService:
    def __init__(self, database_service: DatabaseService | None = None) -> None:
        self.database_service = database_service or DatabaseService()
        self.password_hasher = PasswordHasher()

    @staticmethod
    def _part(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")

    @staticmethod
    def _unpart(value: str) -> bytes:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

    def _secret(self) -> bytes:
        if not app_settings.AUTH_JWT_SECRET:
            raise RuntimeError("AUTH_JWT_SECRET is required for authentication.")
        return app_settings.AUTH_JWT_SECRET.encode("utf-8")

    def _verify_signature(self, signing_input: bytes, signature: str) -> bool:
        signature_bytes = self._unpart(signature)
        secrets = [self._secret()] + list(app_settings.auth_jwt_previous_secrets)
        for secret in secrets:
            expected = hmac.new(secret, signing_input, hashlib.sha256).digest()
            if hmac.compare_digest(expected, signature_bytes):
                return True
        return False

    def _normalize_claims(self, token: str) -> dict[str, object]:
        try:
            header, payload, signature = token.split(".")
            signing_input = f"{header}.{payload}".encode("ascii")
            if not self._verify_signature(signing_input, signature):
                raise ValueError("Invalid token signature")
            claims = json.loads(self._unpart(payload))
            header_claims = json.loads(self._unpart(header))
            if header_claims.get("alg") != "HS256":
                raise ValueError("Invalid token algorithm")
            if claims.get("type") != "access" or int(claims["exp"]) <= int(time.time()):
                raise ValueError("Expired or invalid token")
            if "sub" not in claims:
                raise ValueError("Invalid token payload")
            return claims
        except (KeyError, ValueError, TypeError, json.JSONDecodeError, UnicodeError) as exc:
            raise ValueError("Invalid access token") from exc

    def _generate_access_token(self, user_id: uuid.UUID, session) -> str:
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(seconds=app_settings.AUTH_TOKEN_TTL_SECONDS)
        token_id = uuid.uuid4()
        header = self._part(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
        payload = self._part(
            json.dumps(
                {
                    "sub": str(user_id),
                    "type": "access",
                    "iat": int(issued_at.timestamp()),
                    "exp": int(expires_at.timestamp()),
                    "jti": str(token_id),
                },
                separators=(",", ":"),
            ).encode()
        )
        signing_input = f"{header}.{payload}".encode("ascii")
        signature = self._part(hmac.new(self._secret(), signing_input, hashlib.sha256).digest())
        session.add(
            TokenSession(
                token_id=token_id,
                user_id=user_id,
                issued_at=issued_at,
                expires_at=expires_at,
            )
        )
        session.flush()
        return f"{header}.{payload}.{signature}"

    def _token_claims_to_user_id(self, claims: dict[str, object]) -> uuid.UUID:
        return uuid.UUID(str(claims["sub"]))

    def _get_jti_from_claims(self, claims: dict[str, object]) -> str | None:
        return claims.get("jti")

    def _validate_session_record(self, session, token_id: str) -> None:
        token_session = session.get(TokenSession, uuid.UUID(token_id))
        if token_session is None:
            raise ValueError("Invalid access token")
        if token_session.revoked_at is not None:
            raise ValueError("Invalid access token")
        if token_session.expires_at <= datetime.now(timezone.utc):
            raise ValueError("Invalid access token")

    def _parse_access_token(self, token: str) -> tuple[uuid.UUID, str | None]:
        claims = self._normalize_claims(token)
        user_id = self._token_claims_to_user_id(claims)
        jti = self._get_jti_from_claims(claims)
        return user_id, jti

    def derive_rate_limit_key(self, endpoint: str, client_ip: str, normalized_email: str | None = None) -> str:
        return self._derive_rate_limit_key(endpoint=endpoint, client_ip=client_ip, normalized_email=normalized_email)

    def enforce_rate_limit(self, endpoint: str, request_key: str) -> None:
        try:
            self._enforce_rate_limit(endpoint=endpoint, request_key=request_key)
        except RateLimitExceeded as exc:
            raise

    def _derive_rate_limit_key(self, endpoint: str, client_ip: str, normalized_email: str | None = None) -> str:
        pieces = [app_settings.AUTH_RATE_LIMIT_KEY_SALT, endpoint, client_ip]
        if normalized_email:
            pieces.append(normalized_email)
        digest = hashlib.sha256("|".join(pieces).encode("utf-8")).hexdigest()
        return digest

    def _advisory_lock_key(self, request_key: str) -> int:
        digest = hashlib.sha256(request_key.encode("utf-8")).digest()
        lock_value = int.from_bytes(digest[:8], byteorder="big", signed=False)
        if lock_value >= 2**63:
            lock_value -= 2**64
        return lock_value

    def _enforce_rate_limit(self, endpoint: str, request_key: str) -> None:
        window_seconds = app_settings.AUTH_RATE_LIMIT_WINDOW_SECONDS
        max_requests = app_settings.AUTH_RATE_LIMIT_MAX_REQUESTS
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
        lock_id = self._advisory_lock_key(request_key)

        with self.database_service.transaction() as session:
            session.execute(text("SELECT pg_advisory_xact_lock(:lock_id)"), {"lock_id": lock_id})
            total = session.execute(
                select(func.count())
                .select_from(AuthRateLimitEvent)
                .where(
                    AuthRateLimitEvent.endpoint == endpoint,
                    AuthRateLimitEvent.request_key == request_key,
                    AuthRateLimitEvent.created_at >= cutoff,
                )
            ).scalar_one()
            if total >= max_requests:
                oldest = session.execute(
                    select(AuthRateLimitEvent.created_at)
                    .where(
                        AuthRateLimitEvent.endpoint == endpoint,
                        AuthRateLimitEvent.request_key == request_key,
                        AuthRateLimitEvent.created_at >= cutoff,
                    )
                    .order_by(AuthRateLimitEvent.created_at.asc())
                    .limit(1)
                ).scalar_one_or_none()
                if oldest is not None:
                    retry_after = max(0, int((oldest + timedelta(seconds=window_seconds) - datetime.now(timezone.utc)).total_seconds()))
                else:
                    retry_after = window_seconds
                raise RateLimitExceeded(retry_after)

            session.execute(
                text(
                    "DELETE FROM auth.auth_rate_limit_events "
                    "WHERE created_at < :cutoff"
                ),
                {"cutoff": cutoff},
            )
            session.add(
                AuthRateLimitEvent(
                    endpoint=endpoint,
                    request_key=request_key,
                )
            )
            session.flush()

    def _build_access_token_response(self, user_id: uuid.UUID, token: str) -> dict[str, str]:
        return {"user_id": str(user_id), "access_token": token, "token_type": "bearer"}

    def logout(self, token: str) -> None:
        _, jti = self._parse_access_token(token)
        if jti is None:
            return
        with self.database_service.transaction() as session:
            token_session = session.get(TokenSession, uuid.UUID(jti))
            if token_session is None or token_session.revoked_at is not None:
                return
            token_session.revoked_at = datetime.now(timezone.utc)
            token_session.revocation_reason = "logout"
            session.add(token_session)
            session.flush()

    def register(self, *, email: str, password: str, full_name: str) -> dict[str, str]:
        with self.database_service.transaction() as session:
            if session.execute(select(User).where(User.email == email)).scalar_one_or_none() is not None:
                raise ValueError("An account with that email already exists.")
            role_id = session.execute(select(Role.role_id).where(Role.role_name == "Viewer")).scalar_one_or_none()
            if role_id is None:
                raise RuntimeError("Viewer role is not configured.")
            user = User(user_id=uuid.uuid4(), role_id=role_id, email=email, full_name=full_name, password_hash=self.password_hasher.hash(password), is_active=True)
            session.add(user)
            session.flush()
            token = self._generate_access_token(user.user_id, session)
            return self._build_access_token_response(user.user_id, token)

    def login(self, *, email: str, password: str) -> dict[str, str]:
        with self.database_service.transaction() as session:
            user = session.execute(select(User).where(User.email == email, User.is_active.is_(True))).scalar_one_or_none()
            if user is None or not user.password_hash:
                raise ValueError("Invalid credentials.")
            try:
                self.password_hasher.verify(user.password_hash, password)
            except (VerifyMismatchError, VerificationError):
                raise ValueError("Invalid credentials.")
            token = self._generate_access_token(user.user_id, session)
            return self._build_access_token_response(user.user_id, token)

    def authenticate(self, token: str) -> str:
        user_id, jti = self._parse_access_token(token)
        with self.database_service.transaction() as session:
            user = session.get(User, user_id)
            if user is None or not user.is_active:
                raise ValueError("Invalid credentials.")
            if jti is not None:
                self._validate_session_record(session, jti)
        return str(user_id)

    def is_admin(self, user_id: str) -> bool:
        with self.database_service.transaction() as session:
            user = session.execute(
                select(User)
                .join(Role, Role.role_id == User.role_id)
                .where(User.user_id == uuid.UUID(user_id), User.is_active.is_(True))
            ).scalar_one_or_none()
            return bool(user is not None and user.role.role_name == "Admin")