from __future__ import annotations

import os
from typing import Any

import streamlit as st

from api_client import OmniBrainAPIClient


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

    /* =========================================================
       OMNIBRAIN — DARK TEAL GLASS THEME
       ========================================================= */

    :root {
        --ob-black: #091413;
        --ob-deep: #0c211c;
        --ob-green: #285A48;
        --ob-teal: #408A71;
        --ob-mint: #B0E4CC;
        --ob-white: #f4fbf8;
        --ob-muted: #a7bbb3;
        --ob-border: rgba(176, 228, 204, 0.16);
        --ob-glass: rgba(18, 45, 38, 0.62);
    }

    /* ---------- APP BACKGROUND ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 82% 4%,
                rgba(64, 138, 113, 0.40) 0%,
                rgba(40, 90, 72, 0.25) 24%,
                transparent 52%
            ),
            radial-gradient(
                circle at 55% 35%,
                rgba(64, 138, 113, 0.18),
                transparent 42%
            ),
            linear-gradient(
                145deg,
                #091413 0%,
                #0b1d19 38%,
                #102d24 70%,
                #285A48 100%
            );

        color: var(--ob-white);
        min-height: 100vh;
    }

    /* subtle top glow */

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background:
            radial-gradient(
                circle at 90% 10%,
                rgba(176, 228, 204, 0.10),
                transparent 22%
            );
        z-index: 0;
    }

    /* ---------- MAIN CONTAINER ---------- */

    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 4rem;
        max-width: 1500px;
    }
    /* ---------- HIDE STREAMLIT TOP BAR ---------- */

    header[data-testid="stHeader"] {
        display: none !important;
    }

    [data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
    }

    .main .block-container {
        padding-top: 0.5rem !important;
    }
    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        min-width: 335px !important;
        max-width: 335px !important;
        background:
            linear-gradient(
                180deg,
                #06100e 0%,
                #091413 45%,
                #10251f 100%
            );

        border-right: 1px solid rgba(176, 228, 204, 0.10);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }

    [data-testid="stSidebar"] * {
        color: var(--ob-white);
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(176, 228, 204, 0.14);
        margin: 1.5rem 0;
    }

    [data-testid="stSidebar"] input {
        background: rgba(20, 47, 39, 0.72) !important;
        border: 1px solid rgba(176, 228, 204, 0.12) !important;
        color: white !important;
        border-radius: 10px !important;
    }

    /* ---------- HERO ---------- */

    .hero {
        position: relative;
        padding: 1.25rem 0 1.05rem;
    }

    .eyebrow {
        color: #a7e8c5;
        font-weight: 800;
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 0.65rem;
    }

    .hero h1 {
        color: #F4FBF8 !important;
        -webkit-text-fill-color: #F4FBF8 !important;
        background: none !important;
        -webkit-background-clip: initial !important;
        background-clip: initial !important;

        font-size: 3.15rem !important;
        font-weight: 800 !important;
        letter-spacing: -.045em;
        line-height: 1.05;
        margin: .2rem 0 .65rem;
    }
     
    

    .hero h1 span {
        color: #8FE0B8 !important;
        -webkit-text-fill-color: #8FE0B8 !important;
        background: none !important;
        -webkit-background-clip: initial !important;
        background-clip: initial !important;
    }

    .hero p {
        color: #e8f1ed !important;
        font-size: 1.05rem;
        line-height: 1.6;
        max-width: 48rem;
        margin: 0;
    }
    /* ---------- TABS ---------- */

    
    

    
    /* ---------- GLASS CARDS ---------- */

    .document-card {
        background:
            linear-gradient(
                145deg,
                rgba(40, 90, 72, .42),
                rgba(9, 20, 19, .55)
            );

        border: 1px solid var(--ob-border);
        border-radius: 18px;
        padding: 1.15rem 1.3rem;
        box-shadow:
            0 15px 45px rgba(0, 0, 0, .22),
            inset 0 1px 0 rgba(255,255,255,.04);

        backdrop-filter: blur(14px);
    }

    .document-card strong {
        color: var(--ob-white);
    }

    /* ---------- SOURCE CARDS ---------- */

    .source-card {
        background: rgba(40, 90, 72, .30);
        border: 1px solid rgba(176, 228, 204, .13);
        border-left: 3px solid var(--ob-teal);
        padding: .8rem 1rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: .5rem;
    }

    .status-dot {
        color: var(--ob-mint);
        font-size: .9rem;
    }

    /* ---------- INDEX SUMMARY METRICS ---------- */

    .summary-metric {
        padding: .15rem .2rem;
    }

    .summary-metric-icon {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(64, 138, 113, .18);
        border: 1px solid rgba(176, 228, 204, .18);
        color: #B0E4CC;
        font-size: 1.05rem;
        margin-bottom: .7rem;
    }

    .summary-metric-title {
        color: #9DB3AA;
        font-size: .78rem;
        font-weight: 600;
        margin-bottom: .15rem;
    }

    .summary-metric-value {
        color: #F4FBF8;
        font-size: 1.9rem;
        font-weight: 700;
        line-height: 1.1;
    }

    .summary-metric-caption {
        color: #8FA69D;
        font-size: .72rem;
        margin-top: .3rem;
    }
    /* ---------- METRICS ---------- */

    # [data-testid="stMetric"] {
    #     background:
    #         linear-gradient(
    #             145deg,
    #             rgba(40, 90, 72, .36),
    #             rgba(9, 20, 19, .50)
    #         );

    #     border: 1px solid var(--ob-border);
    #     border-radius: 16px;
    #     padding: 1rem;
    #     box-shadow:
    #         0 12px 30px rgba(0,0,0,.20);
    # }

    [data-testid="stMetricLabel"] {
        color: #9db3aa !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--ob-white) !important;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        border-radius: 11px !important;
        border: 1px solid rgba(176, 228, 204, .25) !important;
        background: rgba(20, 47, 39, .70) !important;
        color: var(--ob-white) !important;
        font-weight: 700 !important;
        transition: all .2s ease;
    }

    .stButton > button:hover {
        border-color: var(--ob-mint) !important;
        background: rgba(64, 138, 113, .35) !important;
        color: white !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"] {
        background:
            linear-gradient(
                135deg,
                #285A48,
                #408A71
            ) !important;

        border: 1px solid rgba(176, 228, 204, .35) !important;

        box-shadow:
            0 8px 24px rgba(64, 138, 113, .25);
    }

    .stButton > button[kind="primary"]:hover {
        background:
            linear-gradient(
                135deg,
                #408A71,
                #B0E4CC
            ) !important;

        color: #091413 !important;
        box-shadow:
            0 10px 30px rgba(176, 228, 204, .22);
    }

    /* ---------- FILE UPLOADER ---------- */

    [data-testid="stFileUploader"] {
        background:
            radial-gradient(
                circle at center,
                rgba(64, 138, 113, .18),
                rgba(9, 20, 19, .35)
            ) !important;

        border: 1px dashed rgba(176, 228, 204, .55) !important;
        border-radius: 16px !important;
        padding: .8rem !important;
    }

    [data-testid="stFileUploader"] section {
        background: transparent !important;
    }

    [data-testid="stFileUploader"] small {
        color: #9db3aa !important;
    }

    /* ---------- CHAT ---------- */

    [data-testid="stChatMessage"] {
        background: rgba(18, 45, 38, .42);
        border: 1px solid rgba(176, 228, 204, .10);
        border-radius: 16px;
        margin-bottom: .75rem;
    }

    [data-testid="stChatInput"] {
        border-color: rgba(176, 228, 204, .25) !important;
    }

    [data-testid="stChatInput"] > div {
        background: rgba(9, 20, 19, .75) !important;
        border: 1px solid rgba(176, 228, 204, .22) !important;
    }

    /* ---------- EXPANDERS ---------- */

    [data-testid="stExpander"] {
        background: rgba(18, 45, 38, .42) !important;
        border: 1px solid rgba(176, 228, 204, .13) !important;
        border-radius: 13px !important;
    }

    /* ---------- ALERTS ---------- */

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    /* ---------- CODE ---------- */

    code {
        color: var(--ob-mint) !important;
    }

    /* ---------- DIVIDERS ---------- */

    hr {
        border-color: rgba(176, 228, 204, .12) !important;
    }

    /* ---------- TEXT ---------- */

    .stMarkdown,
    .stCaption {
        color: #c0d0ca;
    }

    h1, h2, h3, h4 {
        color: var(--ob-white) !important;
    }

    .document-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.1rem;
    margin-top: .8rem;
    background: rgba(15, 35, 38, .75);
    border: 1px solid rgba(176, 228, 204, .16);
    border-radius: 14px;
}

.file-icon {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(64, 138, 113, .18);
    border: 1px solid rgba(176, 228, 204, .20);
    color: #B0E4CC;
    font-weight: 800;
    font-size: .72rem;
}

.file-info {
    display: flex;
    flex-direction: column;
    gap: .25rem;
}

.file-info strong {
    color: #F4FBF8;
    font-size: .95rem;
}

.file-info span {
    color: #9FB7AE;
    font-size: .8rem;
}

.workflow-step {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: .75rem 0;
}

.workflow-icon {
    min-width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(64, 138, 113, .20);
    border: 1px solid rgba(176, 228, 204, .22);
    color: #B0E4CC;
    font-weight: 800;
}

.workflow-content {
    padding-top: .15rem;
}

.workflow-title {
    color: #F4FBF8;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: .25rem;
}

.workflow-description {
    color: #A9BCB5;
    font-size: .9rem;
    line-height: 1.5;
}   

/* ---------- UPLOAD + WORKFLOW GLASS CARDS ---------- */

/* ---------- UPLOAD + WORKFLOW GLASS CARDS ---------- */


    /* ---------- MAIN WORKSPACE PANELS ---------- */

[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    background:
        linear-gradient(
            145deg,
            rgba(18, 45, 38, 0.72),
            rgba(9, 20, 19, 0.55)
        ) !important;

    border: 1px solid rgba(176, 228, 204, 0.12) !important;
    border-radius: 18px !important;

    padding: 1.5rem !important;

    box-shadow:
        0 18px 45px rgba(0, 0, 0, 0.18),
        inset 0 1px 0 rgba(255,255,255,0.025);

    backdrop-filter: blur(14px);
}
    /* Compact workspace cards */
[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-height: 0 !important;
}

/* Reduce empty space inside workspace cards */
[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div {
    gap: 0.6rem !important;
}

/* Keep section headings tight */
[data-testid="stHorizontalBlock"] h3 {
    margin-top: 0 !important;
    margin-bottom: 0.35rem !important;
}

/* Compact captions */
[data-testid="stHorizontalBlock"] [data-testid="stCaptionContainer"] {
    margin-bottom: 0.8rem !important;
}

/* =========================================================
   TOP WORKSPACE NAVIGATION
   ========================================================= */

[data-baseweb="tab-list"] {
    width: 100% !important;
    height: 56px !important;

    display: flex !important;
    align-items: stretch !important;

    background: rgba(10, 42, 38, 0.72) !important;

    border: 1px solid rgba(143, 224, 184, 0.16) !important;
    border-radius: 12px !important;

    padding: 0 8px !important;
    gap: 0 !important;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.025),
        0 8px 24px rgba(0,0,0,0.10) !important;

    overflow: hidden !important;
}


/* Individual tabs */

[data-baseweb="tab-list"] > button {
    position: relative !important;

    flex: 1 1 0 !important;

    height: 54px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    background: transparent !important;

    border: none !important;
    border-radius: 9px !important;

    color: #D7E8E1 !important;

    font-size: 0.92rem !important;
    font-weight: 500 !important;

    padding: 0 18px !important;

    transition:
        background 0.2s ease,
        color 0.2s ease !important;
}


/* Remove Streamlit's default active border */

[data-baseweb="tab-list"] > button::after {
    display: none !important;
}


/* Hover */

[data-baseweb="tab-list"] > button:hover {
    background: rgba(143, 224, 184, 0.055) !important;
    color: #F1FAF6 !important;
}


/* Active tab */

[data-baseweb="tab-list"] > button[aria-selected="true"] {
    background: rgba(143, 224, 184, 0.08) !important;
    color: #F3FBF8 !important;

    box-shadow:
        inset 0 -2px 0 #8FE0B8 !important;
}


/* =========================================================
   ICONS
   ========================================================= */

[data-baseweb="tab-list"] > button:nth-child(1)::before {
    content: "▤";
    font-size: 1rem;
    margin-right: 10px;
    color: #E5F3EE;
}

[data-baseweb="tab-list"] > button:nth-child(2)::before {
    content: "▱";
    font-size: 1rem;
    margin-right: 10px;
    color: #E5F3EE;
}

[data-baseweb="tab-list"] > button:nth-child(3)::before {
    content: "⊞";
    font-size: 1.05rem;
    margin-right: 10px;
    color: #E5F3EE;
}


    /* =========================
   OMNIBRAIN TOP TABS
   ========================= */

.stTabs {
    width: 100% !important;
}

/* Outer navigation bar */
.stTabs [data-baseweb="tab-list"] {
    width: 100% !important;
    min-height: 56px !important;
    height: 56px !important;

    display: flex !important;
    align-items: stretch !important;

    padding: 4px !important;
    gap: 0 !important;

    background: rgba(8, 37, 34, 0.78) !important;

    border: 1px solid rgba(143, 224, 184, 0.16) !important;
    border-radius: 12px !important;

    box-sizing: border-box !important;
}

/* Each tab */
.stTabs [data-baseweb="tab-list"] > button {
    flex: 1 !important;
    width: 33.333% !important;
    max-width: none !important;

    height: 48px !important;
    min-height: 48px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    position: relative !important;

    padding: 0 24px !important;
    margin: 0 !important;

    border: 0 !important;
    border-radius: 9px !important;

    background: transparent !important;

    color: #d7e8e1 !important;

    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

/* Active tab */
.stTabs [data-baseweb="tab-list"] > button[aria-selected="true"] {
    color: #f4fbf8 !important;
    background: rgba(143, 224, 184, 0.075) !important;
}

/* Active mint underline */
.stTabs [data-baseweb="tab-highlight"] {
    background: #8fe0b8 !important;
    height: 2px !important;
    border-radius: 999px !important;
}

/* Remove Streamlit's extra bottom border */
.stTabs [data-baseweb="tab-border"] {
    background: transparent !important;
}

/* Icons */
.stTabs [data-baseweb="tab-list"] > button:nth-child(1)::before {
    content: "▤";
    margin-right: 9px;
    color: #e5f3ee;
    font-size: 15px;
}

.stTabs [data-baseweb="tab-list"] > button:nth-child(2)::before {
    content: "▱";
    margin-right: 9px;
    color: #e5f3ee;
    font-size: 15px;
}

.stTabs [data-baseweb="tab-list"] > button:nth-child(3)::before {
    content: "⊞";
    margin-right: 9px;
    color: #e5f3ee;
    font-size: 15px;
}

/* Chevron between sections */
.stTabs [data-baseweb="tab-list"] > button:nth-child(1)::after,
.stTabs [data-baseweb="tab-list"] > button:nth-child(2)::after {
    content: "›";
    position: absolute;
    right: 18px;

    color: #8fe0b8;
    font-size: 20px;
    font-weight: 300;

    background: transparent;
}
    </style>
    """,
    unsafe_allow_html=True,
)

def initialize_state() -> None:
    defaults: dict[str, Any] = {
        "user_id": None,
        "access_token": None,
        "authenticated": False,
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
    score = source.get("score")
    if page_start is None:
        page_label = "Page unavailable"
    elif page_end is None or page_start == page_end:
        page_label = f"Page {page_start}"
    else:
        page_label = f"Pages {page_start}-{page_end}"

    with st.expander(
        f"Source {index}: {filename} — {page_label}"
    ):
        st.markdown(f"**Document:** {filename}")
        st.markdown(f"**Pages:** {page_label}")

        if score is not None:
            st.caption(f"Retrieval relevance score: {score:.3f}")

initialize_state()

def check_health(client):
    try:
        client.health()
        st.session_state.backend_online = True
        st.success("● Backend connected")
    except Exception:
        st.session_state.backend_online = False
        st.warning("Backend offline — start FastAPI first")
        
client = OmniBrainAPIClient(
    base_url=st.session_state.backend_url,
    access_token=st.session_state.access_token,
)

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:1.65rem;
            font-weight:800;
            letter-spacing:-.04em;
            margin-bottom:.15rem;
        ">
            ✦ OmniBrain
        </div>

        <div style="
            color:#8fa69d;
            font-size:.68rem;
            font-weight:700;
            letter-spacing:.14em;
        ">
            MULTI-MODAL RESEARCH WORKSPACE
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        "<div style='color:#35D6A0;font-weight:700;letter-spacing:.08em;'>ACCOUNT</div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.authenticated:

        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            login_email = st.text_input(
                "Email",
                key="login_email",
            )

            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            if st.button(
                "Login",
                type="primary",
                use_container_width=True,
            ):
                try:
                    auth_result = client.login(
                        email=login_email.strip(),
                        password=login_password,
                    )

                    st.session_state.access_token = auth_result["access_token"]
                    st.session_state.user_id = auth_result["user_id"]
                    st.session_state.authenticated = True

                    st.success("Login successful.")
                    st.rerun()

                except Exception as exc:
                    st.error(f"Login failed: {exc}")

        with register_tab:
            register_name = st.text_input(
                "Full name",
                key="register_name",
            )

            register_email = st.text_input(
                "Email",
                key="register_email",
            )

            register_password = st.text_input(
                "Password",
                type="password",
                key="register_password",
            )

            if st.button(
                "Create account",
                type="primary",
                use_container_width=True,
            ):
                try:
                    auth_result = client.register(
                        full_name=register_name.strip(),
                        email=register_email.strip(),
                        password=register_password,
                    )

                    st.session_state.access_token = auth_result["access_token"]
                    st.session_state.user_id = auth_result["user_id"]
                    st.session_state.authenticated = True

                    st.success("Account created successfully.")
                    st.rerun()

                except Exception as exc:
                    st.error(f"Registration failed: {exc}")

    else:

        st.success(
            f"Signed in as {st.session_state.user_id}"
        )

        if st.button(
            "Logout",
            use_container_width=True,
        ):
            try:
                client.logout()
            except Exception:
                pass

            st.session_state.access_token = None
            st.session_state.user_id = None
            st.session_state.authenticated = False
            st.session_state.document_id = None
            st.session_state.document_name = None
            st.session_state.upload_result = None
            st.session_state.messages = []

            st.rerun()

    st.divider()

    st.markdown(
        "<div style='color:#35D6A0;font-weight:700;letter-spacing:.08em;'>WORKSPACE SETTINGS</div>",
        unsafe_allow_html=True,
    )

    st.session_state.backend_url = st.text_input(
        "API URL",
        value=st.session_state.backend_url,
    ).strip()

    # st.session_state.user_id = st.text_input(
    #     "Researcher ID",
    #     value=st.session_state.user_id,
    # ).strip() or "local-user"


    # client = OmniBrainAPIClient(
    #     base_url=st.session_state.backend_url,
    #     access_token=st.session_state.access_token,
    # )

    if st.button(
        "Test connection",
        use_container_width=True,
    ):
        check_health(client)

    if st.session_state.backend_online is True:
        st.success("●  Backend connected")

    elif st.session_state.backend_online is False:
        st.warning("Backend offline — start FastAPI first")

    st.divider()

    st.markdown(
        "<div style='color:#35D6A0;font-weight:700;letter-spacing:.08em;'>ACTIVE SOURCE</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.document_id:

        st.markdown(
            f"""
            <div class="document-card">
                <div style="font-size:1.4rem;">📄</div>
                <strong>
                    {st.session_state.document_name or "Untitled document"}
                </strong>
                <div style="
                    color:#9db3aa;
                    font-size:.8rem;
                    margin-top:.35rem;
                ">
                    ✦ Ready for cited questions
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Clear document",
            use_container_width=True,
        ):
            st.session_state.document_id = None
            st.session_state.document_name = None
            st.session_state.upload_result = None
            st.rerun()

    else:

        st.caption(
            "Upload a PDF to ground your answers in evidence."
        )

    st.divider()

    st.markdown(
        """
        <div style="
            margin-top:2rem;
            color:#78928a;
            font-size:.78rem;
            line-height:1.6;
        ">
            <div style="color:#B0E4CC;font-weight:700;">
                ✦ OmniBrain v1.0.0
            </div>
            <div>
                Agentic Multi-Modal RAG
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """<div class="hero">
<div class="eyebrow">AGENTIC MULTI-MODAL RAG ✦</div>
<h1>Research with <span>receipts.</span></h1>
<p>Upload a report, let OmniBrain index it,<br>
and ask questions with transparent agent routing and page-level evidence.</p>
</div>""",
    unsafe_allow_html=True,
)

upload_tab, chat_tab, status_tab = st.tabs(["01  Add a source", "02  Ask OmniBrain", "Workspace"])

with upload_tab:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("Build your evidence base")
        st.caption("PDFs are parsed, chunked, and indexed for retrieval.")

        uploaded_file = st.file_uploader(
            "Drag & drop a file here or click to browse",
            type=None,
            accept_multiple_files=False,
            label_visibility="visible",
        )

        if st.button(
            "✦  Index document",
            type="primary",
            disabled=uploaded_file is None,
            use_container_width=True,
        ):
            try:
                with st.spinner("Parsing, embedding, and indexing your document..."):
                    result = client.upload_document(
                        file_name=uploaded_file.name,
                        file_bytes=uploaded_file.getvalue(),
                        content_type=uploaded_file.type or "application/pdf",
                    )

                st.session_state.upload_result = result
                st.session_state.document_id = result.get("document_id")
                st.session_state.document_name = result.get(
                    "filename",
                    uploaded_file.name,
                )

            except Exception as exc:
                st.error(f"Could not index this document: {exc}")
        with right:
            st.subheader("How it works")

            steps = [
                (
                    "01",
                    "Parse",
                    "Text and structure are extracted from your PDF.",
                    "▤",
                ),
                (
                    "02",
                    "Retrieve",
                    "Relevant chunks are found in Qdrant.",
                    "◈",
                ),
                (
                    "03",
                    "Reason",
                    "The supervisor selects the right specialist agent.",
                    "✦",
                ),
                (
                    "04",
                    "Cite",
                    "Answers link back to their source pages.",
                    "↗",
                ),
            ]

            for number, title, description, icon in steps:
                st.markdown(
                    f"""
                    <div class="workflow-step">
                        <div class="workflow-icon">{icon}</div>
                        <div class="workflow-content">
                            <div class="workflow-title">
                                {number}. {title}
                            </div>
                            <div class="workflow-description">
                                {description}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    if st.session_state.upload_result:
        result = st.session_state.upload_result

        st.divider()
        st.subheader("Index summary")

        with st.container(border=True):

            metrics = st.columns(2)

            with metrics[0]:
                st.markdown(
                    f"""
                    <div class="summary-metric">
                        <div class="summary-metric-icon">▤</div>
                        <div class="summary-metric-title">Pages</div>
                        <div class="summary-metric-value">
                            {result.get("page_count", 0)}
                        </div>
                        <div class="summary-metric-caption">
                            Total pages
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with metrics[1]:
                st.markdown(
                    f"""
                    <div class="summary-metric">
                        <div class="summary-metric-icon">▧</div>
                        <div class="summary-metric-title">Images</div>
                        <div class="summary-metric-value">
                            {result.get("image_count", 0)}
                        </div>
                        <div class="summary-metric-caption">
                            Images extracted
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

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
    st.subheader("Frontend session")

    col1, col2 = st.columns(2)

    with col1:
        st.caption("Backend URL")
        st.code(st.session_state.backend_url)

        st.caption("User ID")
        st.code(st.session_state.user_id or "Not set")

    with col2:
        st.caption("Current document")
        st.write(
            st.session_state.document_name
            or "No document selected"
        )

        st.caption("Messages")
        st.metric(
            "Chat messages",
            len(st.session_state.messages),
        )

    st.divider()

    st.subheader("Backend health")

    if st.button("Refresh backend status"):
        try:
            health = client.health()

            if health.get("status") == "healthy":
                st.success("Backend is healthy.")
            else:
                st.warning("Backend responded, but may need attention.")

            qdrant = health.get("qdrant", {})

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Qdrant",
                    qdrant.get("status", "unknown").title(),
                )

            with col2:
                st.metric(
                    "Collection",
                    qdrant.get("collection_name", "unknown"),
                )

            

            if qdrant.get("collection_exists"):
                st.success("Qdrant collection is available.")
            else:
                st.warning("Qdrant collection was not found.")

        except Exception as exc:
            st.error(str(exc))

    if st.session_state.upload_result:
        with st.expander("Last upload response"):
            result = st.session_state.upload_result

            st.success(
                result.get(
                    "message",
                    "Document uploaded and indexed.",
                )
            )

            metrics = st.columns(2)

            metrics[0].metric(
                "Pages",
                result.get("page_count", 0),
            )

            metrics[1].metric(
                "Images",
                result.get("image_count", 0),
            )