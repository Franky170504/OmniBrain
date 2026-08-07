from __future__ import annotations

import streamlit as st

from api_client import OmniBrainAPIClient

st.set_page_config(page_title="OmniBrain", layout="wide")
st.title("OmniBrain")
st.caption("Agentic document analysis with PostgreSQL history + Qdrant retrieval")

def init_state() -> None:
    defaults = {
        "backend_url": "http://127.0.0.1:8000",
        "user_id": "local-user",
        "document_id": None,
        "document_name": None,
        "session_id": None,
        "messages": [],
        "upload_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

with st.sidebar:
    st.header("Connection")
    st.session_state.backend_url = st.text_input(
        "Backend URL", value=st.session_state.backend_url
    ).rstrip("/")
    st.session_state.user_id = st.text_input(
        "User ID / alias", value=st.session_state.user_id
    ).strip()
    client = OmniBrainAPIClient(st.session_state.backend_url)

    if st.button("Check backend health", use_container_width=True):
        try:
            st.json(client.health())
        except Exception as exc:
            st.error(str(exc))

    st.divider()
    st.write("Selected document:")
    st.code(st.session_state.document_id or "None")
    st.write("Chat session:")
    st.code(st.session_state.session_id or "New session")

upload_tab, chat_tab, history_tab, status_tab = st.tabs(
    ["Upload", "Chat", "History", "Status"]
)

with upload_tab:
    st.subheader("Upload and index a PDF")
    uploaded = st.file_uploader("Choose PDF", type=["pdf"])
    if uploaded is not None:
        st.write(
            {
                "filename": uploaded.name,
                "type": uploaded.type,
                "size_bytes": uploaded.size,
            }
        )
        if st.button("Upload and index", type="primary"):
            try:
                with st.spinner("Parsing, embedding, indexing, and saving metadata..."):
                    result = client.upload(
                        file_name=uploaded.name,
                        file_bytes=uploaded.getvalue(),
                        user_id=st.session_state.user_id,
                    )
                st.session_state.upload_result = result
                st.session_state.document_id = result["document_id"]
                st.session_state.document_name = result["filename"]
                st.session_state.session_id = None
                st.session_state.messages = []
                st.success(result["message"])
                st.json(result)
            except Exception as exc:
                st.error(str(exc))

    st.divider()
    if st.button("Refresh my indexed documents"):
        try:
            docs = client.list_documents(user_id=st.session_state.user_id)
            st.session_state["documents"] = docs
        except Exception as exc:
            st.error(str(exc))

    docs = st.session_state.get("documents", [])
    if docs:
        options = {
            f"{d['original_filename']} — {d['processing_status']} — {d['document_id']}": d
            for d in docs
        }
        selected_label = st.selectbox("Use an existing document", list(options))
        if st.button("Select document"):
            selected = options[selected_label]
            st.session_state.document_id = str(selected["document_id"])
            st.session_state.document_name = selected["original_filename"]
            st.session_state.session_id = None
            st.session_state.messages = []
            st.success(f"Selected {selected['original_filename']}")

with chat_tab:
    st.subheader("Chat")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("route"):
                st.caption(
                    f"Route: {message['route']} | Reason: {message.get('route_reason') or 'n/a'}"
                )
            if message.get("sources"):
                with st.expander("Sources"):
                    st.json(message["sources"])

    question = st.chat_input("Ask about the selected document or a general question")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        try:
            with st.chat_message("assistant"):
                with st.spinner("Running LangGraph..."):
                    result = client.chat(
                        question=question,
                        user_id=st.session_state.user_id,
                        document_id=st.session_state.document_id,
                        session_id=st.session_state.session_id,
                    )
                st.session_state.session_id = result["session_id"]
                st.markdown(result["answer"])
                st.caption(
                    f"Route: {result.get('route')} | Reason: {result.get('route_reason') or 'n/a'}"
                )
                if result.get("sources"):
                    with st.expander("Sources"):
                        st.json(result["sources"])
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "route": result.get("route"),
                    "route_reason": result.get("route_reason"),
                    "sources": result.get("sources", []),
                }
            )
        except Exception as exc:
            st.error(str(exc))

with history_tab:
    st.subheader("Persisted PostgreSQL chat history")
    if st.button("Refresh sessions"):
        try:
            st.session_state["sessions"] = client.list_sessions(
                user_id=st.session_state.user_id
            )
        except Exception as exc:
            st.error(str(exc))

    sessions = st.session_state.get("sessions", [])
    if sessions:
        session_map = {
            f"{item.get('title') or 'Untitled'} — {item['session_id']}": item
            for item in sessions
        }
        chosen = st.selectbox("Saved session", list(session_map))
        if st.button("Load session"):
            selected = session_map[chosen]
            try:
                messages = client.get_messages(
                    user_id=st.session_state.user_id,
                    session_id=str(selected["session_id"]),
                )
                st.session_state.session_id = str(selected["session_id"])
                st.session_state.document_id = (
                    str(selected["selected_document_id"])
                    if selected.get("selected_document_id")
                    else None
                )
                st.session_state.messages = [
                    {
                        "role": "assistant" if m["role"] == "ASSISTANT" else "user",
                        "content": m["content"],
                        "route": (m.get("metadata") or {}).get("route"),
                        "route_reason": (m.get("metadata") or {}).get("route_reason"),
                        "sources": (m.get("metadata") or {}).get("sources", []),
                    }
                    for m in messages
                    if m["role"] in ("USER", "ASSISTANT")
                ]
                st.success("Session loaded. Open the Chat tab.")
            except Exception as exc:
                st.error(str(exc))

with status_tab:
    st.subheader("Current application state")
    st.json(
        {
            "backend_url": st.session_state.backend_url,
            "user_id": st.session_state.user_id,
            "document_id": st.session_state.document_id,
            "document_name": st.session_state.document_name,
            "session_id": st.session_state.session_id,
            "message_count": len(st.session_state.messages),
        }
    )
