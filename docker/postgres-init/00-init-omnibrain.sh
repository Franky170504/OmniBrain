#!/usr/bin/env bash
set -Eeuo pipefail

SCHEMA_DIR="/omnibrain-schema"

run_sql() {
  local file="$1"
  echo "[postgres-init] Applying ${file#${SCHEMA_DIR}/}"
  psql \
    --set ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --file "$file"
}

# Keep this explicit: some schema files depend on objects created by earlier files.
run_sql "$SCHEMA_DIR/00_extensions.sql"
run_sql "$SCHEMA_DIR/01_schemas.sql"
run_sql "$SCHEMA_DIR/02_auth.sql"
run_sql "$SCHEMA_DIR/03_auth_sessions.sql"
run_sql "$SCHEMA_DIR/04_common_functions.sql"
run_sql "$SCHEMA_DIR/05_knowledge.sql"
run_sql "$SCHEMA_DIR/06_structured.sql"

for file in "$SCHEMA_DIR"/07_query_engine/*.sql; do
  run_sql "$file"
done

echo "[postgres-init] OmniBrain database initialization complete."
