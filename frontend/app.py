from __future__ import annotations

import os
from typing import Any

import streamlit as st

from frontend.api_client import OmniBrainAPIClient


DEFAULT_BACKEND_URL = os.getenv("OMNIBRAIN_API_URL","http://127.0.0.1:8000")

st.set_page_config(page_title="OmniBrain",layout="wide")

def initialize_state() -> None:
    defaults: dict[str, Any] = {
        "user_id": "local-user",
        "document_id": None,
        "document_name": None,
        "upload_result": None,
        "messages": [],
        "backend_url": DEFAULT_BACKEND_URL,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_source(source: dict[str, Any], index: int) -> None:
    filename = source.get("filename") or "Unknown document"
    page_start = source.get("page_start")
    page_end = source.get("page_end")
    score = source.get("score")

    if page_start is None:
        page_label = "Page unavailable"
    elif page_end is None or page_start == page_end:
        page_label = f"Page {page_start}"
    else:
        page_label = f"Pages {page_start}–{page_end}"

    with st.expander(
        f"Source {index}: {filename} — {page_label}"
    ):
        st.write(
            {
                "document_id": source.get("document_id"),
                "chunk_id": source.get("chunk_id"),
                "point_id": source.get("point_id"),
                "filename": filename,
                "page_start": page_start,
                "page_end": page_end,
                "score": score,
            }
        )


initialize_state()

st.title("OmniBrain")
st.caption(
    "Upload PDFs, index them in Qdrant, and ask questions "
    "through the LangGraph supervisor."
)

with st.sidebar:
    st.header("Connection")
    backend_url = st.text_input("FastAPI URL",value=st.session_state.backend_url).strip()
    st.session_state.backend_url = backend_url
    user_id = st.text_input("User ID",value=st.session_state.user_id).strip()
    st.session_state.user_id = user_id or "local-user"
    client = OmniBrainAPIClient(base_url=st.session_state.backend_url)
    if st.button("Check backend health", use_container_width=True):
        try:
            health = client.health()
            st.success("Backend is reachable.")
            st.json(health)
        except Exception as exc:
            st.error(str(exc))

    st.divider()
    st.subheader("Current document")
    if st.session_state.document_id:
        st.success(st.session_state.document_name or "Document selected")
        st.code(st.session_state.document_id)
        if st.button("Clear selected document",use_container_width=True,):
            st.session_state.document_id = None
            st.session_state.document_name = None
            st.session_state.upload_result = None
            st.rerun()
    else:
        st.info("No document selected.")

upload_tab, chat_tab, status_tab = st.tabs(
    [
        "Upload Document",
        "Chat",
        "Status",
    ]
)

with upload_tab:
    st.subheader("Upload and index a PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        st.write(
            {
                "filename": uploaded_file.name,
                "type": uploaded_file.type,
                "size_bytes": uploaded_file.size,
            }
        )

    upload_clicked = st.button("Upload and index",type="primary",disabled=uploaded_file is None)

    if upload_clicked and uploaded_file is not None:
        if not st.session_state.user_id:
            st.error("User ID is required.")
        else:
            try:
                with st.spinner(
                    "Uploading, parsing, and indexing document..."
                ):
                    result = client.upload_document(
                        file_name=uploaded_file.name,
                        file_bytes=uploaded_file.getvalue(),
                        content_type=(
                            uploaded_file.type
                            or "application/pdf"
                        ),
                        user_id=st.session_state.user_id,
                    )

                st.session_state.upload_result = result
                st.session_state.document_id = result.get(
                    "document_id"
                )
                st.session_state.document_name = result.get(
                    "filename",
                    uploaded_file.name,
                )

                st.success(
                    result.get(
                        "message",
                        "Document uploaded and indexed.",
                    )
                )

            except Exception as exc:
                st.error(str(exc))

    if st.session_state.upload_result:
        result = st.session_state.upload_result

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Pages",
            result.get("page_count", 0),
        )

        col2.metric(
            "Chunks",
            result.get("chunk_count", 0),
        )

        col3.metric(
            "Images",
            result.get("image_count", 0),
        )

        col4.metric(
            "Indexed points",
            result.get("indexed_points", 0),
        )

        st.write("Document ID")

        st.code(
            result.get("document_id", "Unavailable")
        )

        with st.expander("Full upload response"):
            st.json(result)

with chat_tab:
    st.subheader("Chat with OmniBrain")

    if st.session_state.document_id:
        st.info(
            f"Selected document: "
            f"{st.session_state.document_name}"
        )
    else:
        st.warning(
            "No document is selected. General questions can still "
            "be routed to the general agent."
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            route = message.get("route")
            route_reason = message.get("route_reason")
            sources = message.get("sources", [])

            if route:
                st.caption(f"Agent route: `{route}`")

            if route_reason:
                st.caption(route_reason)

            if sources:
                for index, source in enumerate(sources,start=1):
                    render_source(source, index)

    question = st.chat_input("Ask a question about your document...")

    if question:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        try:
            with st.chat_message("assistant"):
                with st.spinner(
                    "Supervisor is selecting an agent..."
                ):
                    result = client.chat(
                        question=question,
                        user_id=st.session_state.user_id,
                        document_id=(
                            st.session_state.document_id
                        ),
                    )

                answer = result.get(
                    "answer",
                    "No answer was returned.",
                )

                sources = result.get("sources", [])
                route = result.get("route")
                route_reason = result.get("route_reason")

                st.markdown(answer)

                if route:
                    st.caption(f"Agent route: `{route}`")

                if route_reason:
                    st.caption(route_reason)

                if sources:
                    st.markdown("#### Sources")

                    for index, source in enumerate(
                        sources,
                        start=1,
                    ):
                        render_source(source, index)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "route": route,
                    "route_reason": route_reason,
                }
            )

        except Exception as exc:
            error_message = str(exc)

            with st.chat_message("assistant"):
                st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Error: {error_message}",
                    "sources": [],
                    "route": None,
                    "route_reason": None,
                }
            )

    if st.session_state.messages:
        if st.button("Clear chat history"):
            st.session_state.messages = []
            st.rerun()

with status_tab:
    st.subheader("Frontend session")

    st.write(
        {
            "backend_url": st.session_state.backend_url,
            "user_id": st.session_state.user_id,
            "document_id": st.session_state.document_id,
            "document_name": st.session_state.document_name,
            "message_count": len(
                st.session_state.messages
            ),
        }
    )

    if st.button("Refresh backend status"):
        try:
            health = client.health()
            st.success("Backend is healthy.")
            st.json(health)
        except Exception as exc:
            st.error(str(exc))

    if st.session_state.upload_result:
        with st.expander("Last upload response"):
            st.json(st.session_state.upload_result)