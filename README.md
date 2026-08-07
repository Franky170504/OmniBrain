# OmniBrain

An agentic, multi-modal RAG workspace for uploading PDFs and asking grounded questions with cited evidence.

## Quick start

1. Create and activate a virtual environment, then install the backend and UI dependencies:

   ```powershell
   python -m pip install -r backend/requirements.txt -r frontend/requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your Groq and Qdrant credentials. LangSmith tracing is optional; leave `LANGSMITH_TRACKING=false` to run without it.

3. Start Qdrant locally with Docker (`docker compose up -d`) or use a Qdrant Cloud URL and API key in `.env`.

4. Start the FastAPI backend from the project root:

   ```powershell
   python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
   ```

5. In a second terminal, start the Streamlit research workspace:

   ```powershell
   python -m streamlit run frontend/app.py
   ```

The Streamlit app is normally available at `http://127.0.0.1:8501`. The FastAPI documentation is at `http://127.0.0.1:8000/docs`.

## API keys

- [Groq](https://console.groq.com/)
- [Qdrant Cloud](https://cloud.qdrant.io/)
- [LangSmith](https://smith.langchain.com/) (optional)
