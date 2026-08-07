from __future__ import annotations
from typing import Any
import requests
class OmniBrainAPIClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout_seconds: int = 300,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _handle_response(
        self,
        response: requests.Response,
    ) -> dict[str, Any]:
        if response.ok:
            try:
                return response.json()
            except ValueError as exc:
                raise RuntimeError(
                    "Backend returned a successful response, "
                    "but the response was not valid JSON."
                ) from exc

        detail = self._extract_error_detail(response)

        raise RuntimeError(
            f"Backend request failed "
            f"({response.status_code}): {detail}"
        )

    @staticmethod
    def _extract_error_detail(
        response: requests.Response,
    ) -> str:
        try:
            payload = response.json()

            if isinstance(payload, dict):
                detail = payload.get("detail")

                if detail is not None:
                    if isinstance(detail, str):
                        return detail

                    return str(detail)

                message = payload.get("message")

                if message is not None:
                    return str(message)

                return str(payload)

            return str(payload)

        except ValueError:
            text = response.text.strip()

            if text:
                return text

            return "Backend returned an unknown error."

    def health(self) -> dict[str, Any]:
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=30,
            )

            return self._handle_response(response)

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Could not connect to the OmniBrain backend. "
                f"Make sure FastAPI is running at "
                f"{self.base_url}."
            ) from exc

        except requests.Timeout as exc:
            raise RuntimeError(
                "Backend health check timed out."
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Health request failed: {exc}"
            ) from exc

    def upload(
        self,
        *,
        file_name: str,
        file_bytes: bytes,
        user_id: str,
    ) -> dict[str, Any]:
        if not file_name:
            raise ValueError(
                "file_name must not be empty."
            )

        if not file_bytes:
            raise ValueError(
                "The uploaded file is empty."
            )

        if not user_id.strip():
            raise ValueError(
                "user_id must not be empty."
            )

        files = {
            "file": (
                file_name,
                file_bytes,
            )
        }

        data = {
            "user_id": user_id.strip(),
        }

        try:
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                data=data,
                timeout=self.timeout_seconds,
            )

            return self._handle_response(response)

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Could not connect to the OmniBrain backend. "
                f"Make sure FastAPI is running at "
                f"{self.base_url}."
            ) from exc

        except requests.Timeout as exc:
            raise RuntimeError(
                "Document upload timed out. "
                "The PDF may be large or processing may "
                "be taking too long."
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Upload request failed: {exc}"
            ) from exc

    def chat(
        self,
        *,
        question: str,
        user_id: str,
        document_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        if not question.strip():
            raise ValueError(
                "question must not be empty."
            )

        if not user_id.strip():
            raise ValueError(
                "user_id must not be empty."
            )

        payload: dict[str, Any] = {
            "question": question.strip(),
            "user_id": user_id.strip(),
            "document_id": document_id,
            "session_id": session_id,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.timeout_seconds,
            )

            return self._handle_response(response)

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Could not connect to the OmniBrain backend. "
                f"Make sure FastAPI is running at "
                f"{self.base_url}."
            ) from exc

        except requests.Timeout as exc:
            raise RuntimeError(
                "Chat request timed out."
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Chat request failed: {exc}"
            ) from exc

    def get_chat_history(
        self,
        *,
        session_id: str,
    ) -> list[dict[str, Any]]:
        if not session_id:
            raise ValueError(
                "session_id must not be empty."
            )

        try:
            response = requests.get(
                (
                    f"{self.base_url}/sessions/"
                    f"{session_id}/messages"
                ),
                timeout=30,
            )

            if response.ok:
                try:
                    payload = response.json()
                except ValueError as exc:
                    raise RuntimeError(
                        "Backend returned invalid JSON "
                        "for chat history."
                    ) from exc

                if isinstance(payload, list):
                    return payload

                raise RuntimeError(
                    "Backend returned an unexpected "
                    "chat history response."
                )

            detail = self._extract_error_detail(
                response
            )

            raise RuntimeError(
                f"History request failed "
                f"({response.status_code}): {detail}"
            )

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Could not connect to the OmniBrain backend."
            ) from exc

        except requests.Timeout as exc:
            raise RuntimeError(
                "Chat history request timed out."
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                f"History request failed: {exc}"
            ) from exc

    def get_sessions(
        self,
        *,
        user_id: str,
    ) -> list[dict[str, Any]]:
        if not user_id.strip():
            raise ValueError(
                "user_id must not be empty."
            )

        try:
            response = requests.get(
                f"{self.base_url}/sessions",
                params={
                    "user_id": user_id.strip(),
                },
                timeout=30,
            )

            if response.ok:
                try:
                    payload = response.json()
                except ValueError as exc:
                    raise RuntimeError(
                        "Backend returned invalid JSON "
                        "for sessions."
                    ) from exc

                if isinstance(payload, list):
                    return payload

                raise RuntimeError(
                    "Backend returned an unexpected "
                    "sessions response."
                )

            detail = self._extract_error_detail(
                response
            )

            raise RuntimeError(
                f"Sessions request failed "
                f"({response.status_code}): {detail}"
            )

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Could not connect to the OmniBrain backend."
            ) from exc

        except requests.Timeout as exc:
            raise RuntimeError(
                "Sessions request timed out."
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Sessions request failed: {exc}"
            ) from exc