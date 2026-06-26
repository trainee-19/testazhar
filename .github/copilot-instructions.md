# Project: Mergington High School Activities API
# Copilot Instructions

## Purpose
This project provides a REST API for viewing and managing extracurricular activities at Mergington High School.

## NEVER_MODIFY — UAT-locked code
The following have passed User Acceptance Testing and must NOT be modified by any Copilot suggestion. If Copilot suggests changes to these, reject the suggestion immediately.

### UAT-locked route functions (src/app.py)
- `get_activities()` — GET /activities
- `signup_for_activity()` — POST /activities/{activity_name}/signup

### UAT-locked test file
- `src/tests/test_app.py` — ALL existing test functions are locked.
  Never delete, rename, or modify any existing test function.

## Scope of Copilot assistance
Copilot may help with:
- Adding the new GET /activities/{activity_name} endpoint
- Updating documentation for the new endpoint only
- Suggesting safe, isolated code changes that do not touch locked routes

## Constraints
- Keep all existing public endpoints unchanged
- Preserve the current response behavior for locked routes
- Return JSON with a 404 error message when an activity name is invalid
- Do not add new imports unless they are clearly needed
- Never suggest changes that reduce test coverage
- Never remove or rename any existing public API endpoint

## Capstone — AI Ask Endpoint

### New in-scope files (capstone only)
- `src/app.py` — add /api/ask endpoint and classify_query() below existing routes
- `src/extensions/kb_extension.py` — RAG tool wrapper
- `src/sql/text2sql.py` — Text2SQL tool wrapper
- `src/static/ask.html` — frontend widget
- `src/tests/test_app.py` — new tests at BOTTOM only

### Capstone NEVER_MODIFY (in addition to existing NEVER_MODIFY list)
- src/static/index.html — existing UI must not change
- The ACTIVITIES dictionary — do not restructure, rename, or move
- Any existing route function signatures

### Query routing logic
- "Tell me about", "What is", "Describe", "How does" → RAG tool
- "How many", "Which activities", "List all", "How many spots" → Text2SQL
- "Sign up", "Register", "Join" → return link to existing signup endpoint (do not implement)

### API contract for /api/ask
POST /api/ask
Body: {"question": "string"}
Response 200: {"answer": "string", "source": "rag"|"text2sql"|"direct", "confidence": 0-1}
Response 400: {"error": "question field required"}
Response 500: {"error": "classification failed"}

## Capstone — AI Ask Endpoint

### New in-scope files (capstone only)
- `src/app.py` — add /api/ask endpoint and classify_query() below existing routes
- `src/extensions/kb_extension.py` — RAG tool wrapper
- `src/sql/text2sql.py` — Text2SQL tool wrapper
- `src/static/ask.html` — frontend widget
- `src/tests/test_app.py` — new tests at BOTTOM only

### Capstone NEVER_MODIFY (in addition to existing NEVER_MODIFY list)
- src/static/index.html — existing UI must not change
- The ACTIVITIES dictionary — do not restructure, rename, or move
- Any existing route function signatures

### Query routing logic
- "Tell me about", "What is", "Describe", "How does" → RAG tool
- "How many", "Which activities", "List all", "How many spots" → Text2SQL
- "Sign up", "Register", "Join" → return link to existing signup endpoint (do not implement)

### API contract for /api/ask
POST /api/ask
Body: {"question": "string"}
Response 200: {"answer": "string", "source": "rag"|"text2sql"|"direct", "confidence": 0-1}
Response 400: {"error": "question field required"}
Response 500: {"error": "classification failed"}