# OmniBrain

Before running the files, create venv and run the following commands:

1. pip install . e
2. docker compose up -d

Then run the file backend\app\pipeline\parsing_pipeline.py and backend\app\pipeline\ingestion.py

run the command for accessing FastAPI

1. python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
