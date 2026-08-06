# Query Engine Schema Test Plan

## Goal

Validate the query engine schema and its supporting objects.

## Scope

- `backend/database/schema/06_query_engine/`
- Query lifecycle tracking, retrieval metadata, agent execution logging, responses, citations, feedback, and metrics

## Test Focus

- Schema existence
- Table creation
- Primary keys
- Foreign keys
- Unique constraints
- Check constraints
- Trigger behavior
- Index presence

## Core Objects

- `query_statuses`
- `query_intents`
- `retrieval_strategies`
- `query_priorities`
- `chat_sessions`
- `conversation_turns`
- `queries`
- `retrieved_context`
- `context_items`
- `agent_executions`
- `responses`
- `citations`
- `feedback`
- `metrics`

## Validation

Ensure each object is created correctly and supports expected relationships.

- Foreign keys reference the correct target tables and schemas
- Required columns are present
- Unique and check constraints are enforced
- Query engine indexes are available for lookup and analytics

## Tests

Use SQL validation scripts in `backend/database/tests/query_engine/`.
