from __future__ import annotations

import json
import re
from typing import Any

from groq import Groq
from sqlalchemy import text

from app.core.app_config import settings
from app.database.database_service import (
    DatabaseService,
)


class VisionService:
    """
    Retrieves extracted visual information from
    PostgreSQL and explains it.

    Current information sources:

    Images:
    - caption
    - alt_text
    - OCR text
    - dimensions

    Tables:
    - title
    - summary
    - column headers
    - row/column count

    This service currently reasons over extracted
    visual metadata. It does not claim to inspect
    the image pixels directly.
    """

    def __init__(
        self,
        database_service: DatabaseService | None = None,
    ) -> None:
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is required "
                "for VisionService."
            )

        self.database_service = (
            database_service
            or DatabaseService()
        )

        self.client = Groq(
            api_key=settings.groq_api_key
        )

        self.model = settings.groq_model

    def answer(
        self,
        *,
        question: str,
        document_id: str,
    ) -> dict[str, Any]:
        page_number = (
            self._extract_page_number(
                question
            )
        )

        images = self._get_images(
            document_id=document_id,
            page_number=page_number,
        )

        tables = self._get_tables(
            document_id=document_id,
            page_number=page_number,
        )

        context: list[
            dict[str, Any]
        ] = []

        for image in images:
            context.append(
                {
                    "type": "image",
                    **image,
                }
            )

        for table in tables:
            context.append(
                {
                    "type": "table",
                    **table,
                }
            )

        if not context:
            page_suffix = (
                f" on page {page_number}"
                if page_number
                else ""
            )

            return {
                "answer": (
                    "I could not find extracted "
                    f"visual content{page_suffix}."
                ),
                "sources": [],
                "visual_context": [],
                "visual_type": None,
                "page_number": page_number,
                "error": None,
            }

        answer = self._explain(
            question=question,
            context=context,
        )

        sources = self._build_sources(
            context
        )

        visual_types = {
            item["type"]
            for item in context
        }

        visual_type = (
            next(iter(visual_types))
            if len(visual_types) == 1
            else "mixed"
        )

        return {
            "answer": answer,
            "sources": sources,
            "visual_context": context,
            "visual_type": visual_type,
            "page_number": page_number,
            "error": None,
        }

    @staticmethod
    def _extract_page_number(
        question: str,
    ) -> int | None:
        match = re.search(
            r"\bpage\s+(\d+)\b",
            question,
            flags=re.IGNORECASE,
        )

        if not match:
            return None

        return int(
            match.group(1)
        )

    def _get_images(
        self,
        *,
        document_id: str,
        page_number: int | None,
    ) -> list[dict[str, Any]]:
        sql = """
        SELECT
            i.image_id::text AS image_id,
            p.page_number,
            i.image_index,
            i.original_filename,
            i.image_format,
            i.mime_type,
            i.bucket_name,
            i.object_path,
            i.width_px,
            i.height_px,
            i.caption,
            i.alt_text,
            i.ocr_text

        FROM knowledge.images AS i

        INNER JOIN knowledge.pages AS p
            ON p.page_id = i.page_id

        WHERE
            p.document_id = CAST(
                :document_id AS UUID
            )

            AND p.is_active = TRUE
            AND i.is_active = TRUE
        """

        params: dict[
            str,
            Any,
        ] = {
            "document_id": document_id
        }

        if page_number is not None:
            sql += """
            AND p.page_number =
                :page_number
            """

            params["page_number"] = (
                page_number
            )

        sql += """
        ORDER BY
            p.page_number,
            i.image_index

        LIMIT 20
        """

        with (
            self.database_service.transaction()
            as session
        ):
            result = session.execute(
                text(sql),
                params,
            )

            return [
                dict(row)
                for row
                in result.mappings().all()
            ]

    def _get_tables(
        self,
        *,
        document_id: str,
        page_number: int | None,
    ) -> list[dict[str, Any]]:
        sql = """
        SELECT
            t.table_id::text AS table_id,
            p.page_number,
            t.table_index,
            t.table_title,
            t.table_type,
            t.has_header,
            t.bucket_name,
            t.object_path,
            t.storage_format,
            t.row_count,
            t.column_count,
            t.column_headers,
            t.table_summary

        FROM knowledge.tables AS t

        INNER JOIN knowledge.pages AS p
            ON p.page_id = t.page_id

        WHERE
            p.document_id = CAST(
                :document_id AS UUID
            )

            AND p.is_active = TRUE
            AND t.is_active = TRUE
        """

        params: dict[
            str,
            Any,
        ] = {
            "document_id": document_id
        }

        if page_number is not None:
            sql += """
            AND p.page_number =
                :page_number
            """

            params["page_number"] = (
                page_number
            )

        sql += """
        ORDER BY
            p.page_number,
            t.table_index

        LIMIT 20
        """

        with (
            self.database_service.transaction()
            as session
        ):
            result = session.execute(
                text(sql),
                params,
            )

            return [
                dict(row)
                for row
                in result.mappings().all()
            ]

    def _build_sources(
        self,
        context: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        sources: list[
            dict[str, Any]
        ] = []

        for item in context:
            page_number = item.get(
                "page_number"
            )

            if item["type"] == "image":
                sources.append(
                    {
                        "image_id": (
                            item.get(
                                "image_id"
                            )
                        ),
                        "table_id": None,
                        "filename": (
                            item.get(
                                "original_filename"
                            )
                            or "Document image"
                        ),
                        "page_start": (
                            page_number
                        ),
                        "page_end": (
                            page_number
                        ),
                        "score": 1.0,
                        "object_path": (
                            item.get(
                                "object_path"
                            )
                        ),
                    }
                )

            elif item["type"] == "table":
                sources.append(
                    {
                        "image_id": None,
                        "table_id": (
                            item.get(
                                "table_id"
                            )
                        ),
                        "filename": (
                            item.get(
                                "table_title"
                            )
                            or "Document table"
                        ),
                        "page_start": (
                            page_number
                        ),
                        "page_end": (
                            page_number
                        ),
                        "score": 1.0,
                        "object_path": (
                            item.get(
                                "object_path"
                            )
                        ),
                    }
                )

        return sources

    def _explain(
        self,
        *,
        question: str,
        context: list[
            dict[str, Any]
        ],
    ) -> str:
        safe_context: list[
            dict[str, Any]
        ] = []

        for item in context:
            if item["type"] == "image":
                safe_context.append(
                    {
                        "type": "image",
                        "page_number": (
                            item.get(
                                "page_number"
                            )
                        ),
                        "image_index": (
                            item.get(
                                "image_index"
                            )
                        ),
                        "filename": (
                            item.get(
                                "original_filename"
                            )
                        ),
                        "caption": (
                            item.get(
                                "caption"
                            )
                        ),
                        "alt_text": (
                            item.get(
                                "alt_text"
                            )
                        ),
                        "ocr_text": (
                            item.get(
                                "ocr_text"
                            )
                        ),
                        "width_px": (
                            item.get(
                                "width_px"
                            )
                        ),
                        "height_px": (
                            item.get(
                                "height_px"
                            )
                        ),
                    }
                )

            elif item["type"] == "table":
                safe_context.append(
                    {
                        "type": "table",
                        "page_number": (
                            item.get(
                                "page_number"
                            )
                        ),
                        "table_index": (
                            item.get(
                                "table_index"
                            )
                        ),
                        "title": (
                            item.get(
                                "table_title"
                            )
                        ),
                        "table_type": (
                            item.get(
                                "table_type"
                            )
                        ),
                        "row_count": (
                            item.get(
                                "row_count"
                            )
                        ),
                        "column_count": (
                            item.get(
                                "column_count"
                            )
                        ),
                        "column_headers": (
                            item.get(
                                "column_headers"
                            )
                        ),
                        "summary": (
                            item.get(
                                "table_summary"
                            )
                        ),
                    }
                )

        serialized_context = json.dumps(
            safe_context,
            ensure_ascii=False,
            default=str,
        )

        prompt = f"""
You are OmniBrain's visual-document analyst.

Answer the user's question only from the extracted
visual metadata below.

The visual metadata may represent:

- images
- tables
- charts
- graphs
- figures
- diagrams

For images you may receive:

- caption
- alt text
- OCR text
- dimensions

For tables you may receive:

- title
- columns
- row count
- column count
- extracted summary

Important:

Do NOT claim that you directly inspected image pixels.

If the available metadata is not sufficient to answer
the question, say so clearly.

User question:

{question}

Visual metadata:

{serialized_context}
""".strip()

        response = (
            self.client
            .chat
            .completions
            .create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Explain extracted visual "
                            "document information "
                            "accurately."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.1,
                max_tokens=700,
            )
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        if not answer:
            return (
                "Visual information was found, "
                "but no explanation was produced."
            )

        return str(answer)