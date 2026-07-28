from __future__ import annotations

import os
from config.settings import settings

def configure_langsmith() -> None:
    if not settings.langsmith_tracing:
        return
    if not settings.langsmith_api_key:
        return

    os.environ["LANGSMITH_TRACING"] = settings.langsmith_tracing
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint