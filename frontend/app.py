from __future__ import annotations

import os
from typing import Any

import streamlit as st

from frontend.api_client import OmniBrainAPIClient


DEFAULT_BACKEND_URL = os.getenv("OMNIBRAIN_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="OmniBrain | Research workspace",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp { background: #f5f7fb; color: #172033; }
      [data-testid="stSidebar"] { background: #10182d; }
      [data-testid="stSidebar"] * { color: #f5f7ff; }
      .hero { padding: 1.7rem 0 1.15rem; }
      .eyebrow { color: #6d5dfc; font-weight: 700; font-size: .78rem; letter-spacing: .13em; text-transform: uppercase; }
      .hero h1 { color: #111a30; font-size: 3rem; letter-spacing: -.06em; margin: .25rem 0; }
      .hero p { color: #62708a; font-size: 1.07rem; max-width: 44rem; }
      .document-card { background: #ffffff; border: 1px solid #e6eaf2; border-radius: 18px; padding: 1.05rem 1.25rem; box-shadow: 0 6px 25px rgba(30, 42, 75, .05); }
      .document-card strong { color: #15213b; }
      .source-card { background: #f7f8ff; border-left: 3px solid #6d5dfc; padding: .7rem .85rem; border-radius: 0 10px 10px 0; margin-bottom: .45rem; }
      .status-dot { color: #19a974; font-size: .9rem; }
      [data-testid="stMetric"] { background: #ffffff; border: 1px solid #e7eaf2; border-radius: 14px; padding: .65rem .85rem; }
      .stButton > button[kind="primary"] { background: #6658f5; border-color: #6658f5; }
      .stButton > button[kind="primary"]:hover { background: #5144db; border-color: #5144db; }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_state() -> None:
    defaults: dict[str, Any] = {
        "user_id": "local-user",
        "document_id": None,
        "document_name": None,
        "upload_result": None,
        "messages": [],
        "backend_url": DEFAULT_BACKEND_URL,
        "backend_online": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_source(source: dict[str, Any], index: int) -> None:
    filename = source.get("filename") or "Unknown document"
    page_start, page_end = source.get("page_start"), source.get("page_end")
    if page_start is None:
        page_label = "Page unavailable"
    elif page_end is None or page_start == page_end:
        page_label = f"Page {page_start}"
    else:
        page_label = f"Pages {page_start}-{page_end}"

    with st.expander(f"{index:02d}  {filename} - {page_label}"):
        st.markdown(
            f"<div class='source-card'><strong>{filename}</strong><br>{page_label}"
            f" &nbsp;|&nbsp; relevance: {source.get('score', 'n/a')}</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"Chunk ID: {source.get('chunk_id', 'Unavailable')}")


def check_health(client: OmniBrainAPIClient) -> None:
    try:
        client.health()
        st.session_state.backend_online = True
    except Exception:
        st.session_state.backend_online = False


initialize_state()
client = OmniBrainAPIClient(base_url=st.session_state.backend_url)

with st.sidebar:
    st.markdown("## OmniBrain")
    st.caption("MULTI-MODAL RESEARCH WORKSPACE")
    st.divider()
    st.markdown("### Workspace settings")
    st.session_state.backend_url = st.text_input("API URL", value=st.session_state.backend_url).strip()
    st.session_state.user_id = st.text_input("Researcher ID", value=st.session_state.user_id).strip() or "local-user"
    client = OmniBrainAPIClient(base_url=st.session_state.backend_url)
    if st.button("Test connection", use_container_width=True):
        check_health(client)
    if st.session_state.backend_online is True:
        st.success("Backend connected")
    elif st.session_state.backend_online is False:
        st.warning("Backend offline - start FastAPI first")

    st.divider()
    st.markdown("### Active source")
    if st.session_state.document_id:
        st.markdown(f"**{st.session_state.document_name or 'Untitled document'}**")
        st.caption("Ready for cited questions")
        if st.button("Clear document", use_container_width=True):
            st.session_state.document_id = None
            st.session_state.document_name = None
            st.session_state.upload_result = None
            st.rerun()
    else:
        st.caption("Upload a PDF to ground your answers in evidence.")

st.markdown(
    """<div class="hero"><div class="eyebrow">Agentic multi-modal RAG</div>
    <h1>Research with receipts.</h1>
    <p>Upload a report, let OmniBrain index it, and ask questions with transparent agent routing and page-level evidence.</p></div>""",
    unsafe_allow_html=True,
)

upload_tab, chat_tab, status_tab = st.tabs(["01  Add a source", "02  Ask OmniBrain", "Workspace"])

with upload_tab:
    left, right = st.columns([1.3, 1], gap="large")
    with left:
        st.subheader("Build your evidence base")
        st.caption("PDFs are parsed, chunked, and indexed for retrieval.")
        uploaded_file = st.file_uploader("Drop a PDF here", type=["pdf"], accept_multiple_files=False)
        if uploaded_file is not None:
            st.markdown(
                f"<div class='document-card'><strong>{uploaded_file.name}</strong><br>"
                f"{uploaded_file.size / 1_048_576:.2f} MB • ready to index</div>",
                unsafe_allow_html=True,
            )
        if st.button("Index document", type="primary", disabled=uploaded_file is None):
            try:
                with st.spinner("Parsing, embedding, and indexing your document..."):
                    result = client.upload_document(
                        file_name=uploaded_file.name,
                        file_bytes=uploaded_file.getvalue(),
                        content_type=uploaded_file.type or "application/pdf",
                        user_id=st.session_state.user_id,
                    )
                st.session_state.upload_result = result
                st.session_state.document_id = result.get("document_id")
                st.session_state.document_name = result.get("filename", uploaded_file.name)
                st.success(result.get("message", "Document indexed successfully."))
            except Exception as exc:
                st.error(f"Could not index this document: {exc}")
    with right:
        st.subheader("How it works")
        st.markdown("**1. Parse** - text and structure are extracted from your PDF.")
        st.markdown("**2. Retrieve** - relevant chunks are found in Qdrant.")
        st.markdown("**3. Reason** - the supervisor selects the right specialist agent.")
        st.markdown("**4. Cite** - answers link back to their source pages.")

    if st.session_state.upload_result:
        result = st.session_state.upload_result
        st.divider()
        st.subheader("Index summary")
        metrics = st.columns(4)
        for column, label, key in zip(metrics, ["Pages", "Chunks", "Images", "Indexed points"], ["page_count", "chunk_count", "image_count", "indexed_points"]):
            column.metric(label, result.get(key, 0))

with chat_tab:
    st.subheader("Ask a grounded question")
    if st.session_state.document_id:
        st.markdown(f"<div class='document-card'><span class='status-dot'>●</span> Using <strong>{st.session_state.document_name}</strong></div>", unsafe_allow_html=True)
    else:
        st.info("You can ask a general question, but upload a PDF for grounded, cited answers.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("route"):
                st.caption(f"Routed to: {message['route']}")
            for index, source in enumerate(message.get("sources", []), start=1):
                render_source(source, index)

    question = st.chat_input("Ask about a claim, chart, trend, or finding...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        try:
            with st.chat_message("assistant"):
                with st.spinner("Selecting the best research agent..."):
                    result = client.chat(question=question, user_id=st.session_state.user_id, document_id=st.session_state.document_id)
                answer, sources = result.get("answer", "No answer was returned."), result.get("sources", [])
                st.markdown(answer)
                if result.get("route"):
                    st.caption(f"Routed to: {result['route']}")
                if sources:
                    st.markdown("#### Evidence")
                    for index, source in enumerate(sources, start=1):
                        render_source(source, index)
            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources, "route": result.get("route")})
        except Exception as exc:
            st.error(f"OmniBrain could not answer yet: {exc}")
    if st.session_state.messages and st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

with status_tab:
    st.subheader("Workspace status")
    st.json({
        "backend_url": st.session_state.backend_url,
        "researcher": st.session_state.user_id,
        "active_document": st.session_state.document_name,
        "conversation_messages": len(st.session_state.messages),
    })
    if st.button("Refresh backend status"):
        check_health(client)
        st.rerun()
