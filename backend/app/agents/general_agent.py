from __future__ import annotations

import json
import logging

from groq import Groq

from app.agents.state import AgentState
from app.core.app_config import settings

LOGGER = logging.getLogger("omnibrain.general_agent")

class GeneralAgentNode:
    def __init__(self) -> None:
        self.client = Groq(
            api_key=settings.groq_api_key,
        )

    def __call__(self, state: AgentState) -> dict:
        question = state.get("question", "").strip()
        system_prompt = (
            "You are OmniBrain's general assistant. "
            "Answer clearly and directly."
        )
        payload_messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ]

        serialized_message_payload = json.dumps(
            payload_messages,
            ensure_ascii=False,
        )

        prompt_size_chars = sum(len(str(item.get("content") or "")) for item in payload_messages)
        message_content_chars = sum(len(str(item.get("content") or "")) for item in payload_messages)
        estimated_tokens = max(1, int((prompt_size_chars + message_content_chars) / 4))
        LOGGER.info(
            "GeneralAgentNode request stats: question_len=%d chars, prompt_chars=%d, message_content_chars=%d, estimated_tokens=%d, serialized_request_size=%d, retrieved_chunks=0, retrieved_chars=0, retrieved_tokens_estimate=0",
            len(question),
            prompt_size_chars,
            message_content_chars,
            estimated_tokens,
            len(serialized_message_payload.encode("utf-8")),
        )

        response = self.client.chat.completions.create(
            model=settings.groq_general_model,
            messages=payload_messages,
            temperature=0.2,
            max_tokens=512,
        )

        answer = response.choices[0].message.content
        if not isinstance(answer, str):
            answer = str(answer)

        return {
            "answer": answer,
            "sources": [],
            "error": None,
        }