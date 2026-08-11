# OmniBrain — Quick Setup

This guide shows how to run OmniBrain locally using the repository's Docker Compose setup.
Follow the steps exactly; do not commit secrets or runtime data files.

1) Prerequisites
1. Install Docker Desktop (includes Docker Engine and `docker compose`).
2. Install Git.
3. (Optional) Python 3.14 if you want to run parts of the project without Docker.
4. (Optional) `jq` if you want command-line JSON extraction for API responses.

2) Clone the repository
1. Clone your repo (replace the placeholder):

```sh
# git clone git@github.com:your-org/omnibrain.git
git clone <REPO-URL-OR-PLACEHOLDER>
cd OmniBrain
```

3) Environment configuration
1. Copy the example environment file and edit values you need to configure:

```sh
cp .env.example .env
# Edit .env and set at least the values below (do NOT commit .env):
# - POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE, POSTGRES_USERNAME, POSTGRES_PASSWORD
# - AUTH_JWT_SECRET (set to a secure random string)
# - QDRANT_URL, QDRANT_API_KEY (optional)
# - MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
```

Only the variables above are required for a basic local start; the repository's `.env.example` contains additional optional settings.

4) Start OmniBrain (first time)

```sh
docker compose up -d --build
```

For subsequent runs you can omit `--build`:

```sh
docker compose up -d
```

The Compose file defines these services: `backend`, `minio`, `postgres`, `qdrant`.
Runtime container names used in this project are `omnibrain-api`, `omnibrain-minio`, `omnibrain-postgres`, and `omnibrain-qdrant`.

5) Verify containers

```sh
docker compose ps
```

Expected services (from `docker-compose.yaml`):
- `backend` (FastAPI / Uvicorn) — exposed on port `8000`
- `postgres` (PostgreSQL 16) — exposed on port `5432`
- `minio` (MinIO object storage) — exposed on ports `9000` (API) and `9001` (console)
- `qdrant` (Qdrant vector storage) — exposed on ports `6333` and `6334`

6) Verify FastAPI

Open the API docs (Swagger / OpenAPI):

```
http://localhost:8000/docs
```

Health endpoint implemented by the project:

```
GET http://localhost:8000/health
```

7) Verify infrastructure (URLs / ports)

- FastAPI (backend): http://localhost:8000
- PostgreSQL: localhost:5432
- Qdrant API: http://localhost:6333
- MinIO (API): http://localhost:9000
- MinIO Console: http://localhost:9001

8) Basic end-to-end test (shortest practical flow)

1. Register a user and capture the token and `user_id` from the response (copy manually or use `jq`):

```sh
RESP=$(curl -s -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"Password123","full_name":"Local User"}')
TOKEN=$(echo "$RESP" | jq -r .access_token)
USER_ID=$(echo "$RESP" | jq -r .user_id)
```

2. Upload a small PDF (replace `./sample.pdf`) — the upload endpoint requires the Bearer token:

```sh
curl -s -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@./sample.pdf"

# Response includes `document_id` plus indexing counts.
```

3. Ask a document-specific question (use returned `document_id` and `USER_ID`):

```sh
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"<USER_ID>", "document_id":"<DOCUMENT_ID>", "question":"What is the title of the document?"}'

# Response contains `answer` and `sources` (source metadata and scores).
```

Notes:
- Use the exact `user_id` returned by the register API so the retrieval layer filters correctly.
- The upload endpoint enforces authentication; the chat endpoint accepts `user_id` in the request body.

9) Database / storage architecture (very short)

```
User
  ↓
FastAPI
   ├── PostgreSQL  → structured metadata, users, relationships, transactional state
   ├── MinIO       → uploaded/raw files (object storage)
   └── Qdrant      → embeddings and semantic retrieval (vector DB)
```

10) Troubleshooting (use these repo-supported commands)

```sh
docker compose ps
docker compose logs backend
docker compose restart backend
docker compose down        # preserves volumes unless -v is provided
docker compose up -d --build
```

Extra checks:

```sh
# Qdrant collection info
curl -sS http://localhost:6333/collections/omnibrain | jq '.'

# MinIO console
http://localhost:9001
```

11) Data safety

- Do NOT delete PostgreSQL / MinIO / Qdrant volumes unless you are intentionally resetting local data.
- Do NOT run destructive SQL or DROP statements during normal startup.
- Do NOT commit `.env`, credentials, database volumes, MinIO data, or generated artifacts.

12) Shutdown (preserve data)

```sh
docker compose down
```

To remove volumes (only when intentionally wiping local data):

```sh
docker compose down -v
```

13) TL;DR

```sh
git clone <REPO-URL>
cd OmniBrain
cp .env.example .env      # edit POSTGRES_*, AUTH_JWT_SECRET, QDRANT_URL, MINIO_*
docker compose up -d --build
```

Open http://localhost:8000/docs in your browser.

---
