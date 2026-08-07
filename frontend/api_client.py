from __future__ import annotations
from typing import Any

import requests

class OmniBrainAPIClient:
    def __init__(self,base_url: str = "http://127.0.0.1:8000",timeout: int = 1200) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/health", timeout=15)
        return self._handle_response(response)

    def upload_document(self,*,file_name: str,file_bytes: bytes,content_type: str,user_id: str) -> dict[str, Any]:
        files = {
            "file": (
                file_name,
                file_bytes,
                content_type,
            )
        }

        data = {"user_id": user_id}

        response = requests.post(
            f"{self.base_url}/upload",
            files=files,
            data=data,
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def chat(self,*,question: str, user_id: str, document_id: str | None = None) -> dict[str, Any]:
        payload = {
            "question": question,
            "user_id": user_id,
            "document_id": document_id,
        }

        response = requests.post(
            f"{self.base_url}/chat",
            json=payload,
            timeout=self.timeout,
        )

        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: requests.Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            body = {"detail": response.text or "Unknown server response."}

        if response.ok:
            return body

        detail = body.get("detail", body)

        raise RuntimeError(
            f"Backend request failed "
            f"({response.status_code}): {detail}"
        )