# Run OmniBrain Locally (Windows)

Run these commands from the project root:

```powershell
cd "C:\Users\user\OneDrive\Desktop\Axlero Internship\OmniBrain"
```

## 1. Start the backend and required services

Docker Desktop must be running and a local `.env` file must contain the required API keys and database settings. Never commit `.env`.

```powershell
docker compose up -d --build
docker compose ps
```

Open the backend API documentation at `http://127.0.0.1:8000/docs`.

## 2. Start the frontend

Open a second PowerShell terminal and run:

```powershell
cd "C:\Users\user\OneDrive\Desktop\Axlero Internship\OmniBrain"
python -m streamlit run frontend\app.py
```

Open the Streamlit URL shown in the terminal, normally `http://127.0.0.1:8501`.

## Alternative: start only the backend manually

Use this only after PostgreSQL, MinIO, and Qdrant are already running through Docker. Do not run it at the same time as the Docker backend container.

```powershell
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```
