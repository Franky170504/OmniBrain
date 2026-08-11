import uuid
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.dependencies import get_authenticated_user_id


class TestAuthenticatedUserDependency(unittest.TestCase):
    def test_returns_validated_auth_service_principal(self):
        principal = uuid.uuid4()
        request = SimpleNamespace(state=SimpleNamespace())
        auth_service = MagicMock()
        auth_service.authenticate.return_value = str(principal)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="signed-token")

        self.assertEqual(get_authenticated_user_id(request, credentials, auth_service), str(principal))
        self.assertEqual(request.state.authenticated_user_id, str(principal))

    def test_rejects_missing_principal(self):
        request = SimpleNamespace(state=SimpleNamespace())

        with self.assertRaisesRegex(HTTPException, "Authentication is required"):
            get_authenticated_user_id(request, None, MagicMock())

    def test_rejects_non_uuid_principal(self):
        request = SimpleNamespace(state=SimpleNamespace())
        auth_service = MagicMock()
        auth_service.authenticate.side_effect = ValueError("Invalid access token")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token")

        with self.assertRaisesRegex(HTTPException, "principal is invalid"):
            get_authenticated_user_id(request, credentials, auth_service)


if __name__ == "__main__":
    unittest.main()