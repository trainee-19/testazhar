# GitHub Copilot Training — Capstone Project
## The Mergington High School AI-Powered Activities Platform
### Full Stack · End-to-End · UAT-Protected · Production-Grade

---

> **What this document is**
> The capstone project brings together every module of the training programme into one coherent deliverable. Participants work in teams of 2–3 to extend the Mergington activities API with an AI-powered question-answering layer, protected by every gate built across Day 1 and Day 2. The output is not just working code — it is an AI-assisted feature with a complete audit trail, eval scorecard, and Community of Practice KB entry.
>
> **Estimated time:** 3–4 hours (standalone session)
> **Team size:** 2–3 participants(Optional)
> **Repo:** The same repo from all previous labs
> **Prerequisite:** Labs 1–11 complete on both Day 1 and Day 2

---

## The Business Brief

Mergington High School's administration has made the following request:

> *"Parents and students spend 15 minutes on average finding activity information — schedules, capacity, eligibility. We want to add a smart Q&A page to the activities portal. Users should be able to type natural language questions and get immediate, accurate answers — whether the question is about a specific activity's description or about how many spots are left."*

Your team has been assigned to implement this feature using GitHub Copilot — with every protection layer active.

---

## What You Will Build

### The AI-Powered Activities Assistant

A new endpoint and frontend widget that accepts natural language questions and routes them intelligently:

```
User question
     │
     ▼
┌─────────────────────────────┐
│     /api/ask endpoint       │
│   (new — built by your team)│
└─────────────┬───────────────┘
              │
     classifies query type
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
Qualitative        Quantitative
question           question
(What / How /      (How many /
 Tell me about)    Which / List)
    │                   │
    ▼                   ▼
RAG Tool           Text2SQL Tool
(KB search)        (DB query)
    │                   │
    └─────────┬─────────┘
              │
              ▼
     Formatted NL answer
     returned to frontend
```

### Deliverable Checklist

```
□ /api/ask endpoint in src/app.py
□ Query classifier (rule-based or Copilot-assisted)
□ RAG tool integration (from M8 KB Extension)
□ Text2SQL tool integration (from M8 SQL pipeline)
□ Simple frontend widget in src/static/ (Ask a Question box)
□ All existing 8 tests still passing
□ New tests for /api/ask endpoint
□ copilot-instructions.md updated with capstone scope
□ SKILL.md for the /api/ask routing pattern
□ promptfoo eval config with ≥ 5 assertions
□ 7-step pre-PR pipeline passing in GitHub Actions
□ PR description with AI attribution and eval scorecard
□ CoP KB entry documenting one incident from the capstone
```

---

---

# PHASE 1 — Plan & Scope (30 min)

---

## Step 1.1 — Write the Team AI Scope Statement

Before your team opens Copilot, complete this scope statement. Every team member must agree on it.

```
╔══════════════════════════════════════════════════════════════════════════╗
║  TEAM AI SCOPE STATEMENT — CAPSTONE                                     ║
║  Team members: _________________ _________________ _________________    ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  Task:                                                                   ║
║  Add /api/ask endpoint + query classifier + RAG/Text2SQL routing         ║
║  + frontend widget to the Mergington activities API.                     ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  In scope — Copilot MAY generate or modify:                              ║
║  □ src/app.py — new endpoint and classifier function only                ║
║  □ src/extensions/kb_extension.py — RAG tool integration                ║
║  □ src/sql/text2sql.py — Text2SQL tool integration                       ║
║  □ src/static/ask.html or ask.js — frontend widget                       ║
║  □ src/tests/test_app.py — NEW tests at BOTTOM only                      ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  UAT-LOCKED — Copilot must NEVER modify:                                 ║
║  □ get_activities() in src/app.py                                        ║
║  □ signup() in src/app.py                                                ║
║  □ remove_signup() in src/app.py                                         ║
║  □ Any existing test function in src/tests/test_app.py                   ║
║  □ ACTIVITIES dictionary structure in src/app.py                         ║
║  □ src/static/index.html — existing frontend                             ║
║  □ requirements.txt — no new deps without lead approval                  ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  Tests that must remain passing after every Copilot session:             ║
║  All 8 original tests in src/tests/test_app.py                           ║
║  (plus all new tests added during capstone)                              ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  Reviewed by: _______________________   Date: ___________               ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Step 1.2 — Update copilot-instructions.md for Capstone Scope

Add the capstone context to `.github/copilot-instructions.md`. Append the following section — do not remove or change existing content:

```markdown
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
```

Commit this update before any team member runs a Copilot session:

```bash
git add .github/copilot-instructions.md
git commit -m "chore: add capstone scope to copilot-instructions.md"
git push
```

---

## Step 1.3 — Create the Feature Branch

```bash
git checkout -b feature/capstone-ai-ask
git push -u origin feature/capstone-ai-ask
```

All capstone work happens on this branch. The PR at the end of Phase 3 will merge it to `main`.

---

## Step 1.4 — Write the Eval Assertions BEFORE Building

This is the EDD principle from M7: write the eval before writing the code.

Add a new section to your `promptfooconfig.yaml` for the capstone:

```yaml
# Append to promptfooconfig.yaml

# ── Capstone: /api/ask endpoint eval ─────────────────────────────────────
- description: "Capstone: ask endpoint has correct function name"
  assert:
    - type: contains
      value: "def ask"

- description: "Capstone: ask endpoint uses correct route"
  assert:
    - type: contains
      value: "/api/ask"

- description: "Capstone: endpoint accepts POST method"
  assert:
    - type: contains
      value: "POST"

- description: "Capstone: classifier function present"
  assert:
    - type: contains
      value: "classify_query"

- description: "Capstone: RAG routing for qualitative queries"
  assert:
    - type: contains
      value: "rag"

- description: "Capstone: Text2SQL routing for quantitative queries"
  assert:
    - type: contains
      value: "text2sql"

- description: "Capstone: does NOT modify get_activities — UAT-locked"
  assert:
    - type: not-contains
      value: "def get_activities"

- description: "Capstone: does NOT modify signup — UAT-locked"
  assert:
    - type: not-contains
      value: "def signup"

- description: "Capstone: returns source field in response"
  assert:
    - type: contains
      value: '"source"'

- description: "Capstone: handles 400 for missing question field"
  assert:
    - type: contains
      value: "400"
```

Run a baseline eval now (it should fail — that is expected):

```bash
npx promptfoo eval
```

```
Baseline pass rate (before building): ______ / 10 assertions
Expected: low — this confirms the eval is correctly measuring what doesn't exist yet.
```

---

---

# PHASE 2 — Build (90–120 min)

**Team division of work:**

| Team member | Owns |
|---|---|
| Developer A | `/api/ask` endpoint + `classify_query()` in `src/app.py` |
| Developer B | RAG and Text2SQL tool integrations |
| Developer C (or A+B) | Frontend widget + new tests |

Each developer works on their own feature sub-branch and opens a PR to the capstone branch. The pipeline gates each sub-PR before it merges.

---

## Task A — The /api/ask Endpoint (Developer A · 35 min)

### A1. Write the Prompt Review Checklist first

```
□ Task: add ask() function and classify_query() below remove_signup()
□ What NOT to touch: get_activities(), signup(), remove_signup()
□ Test requirement: existing 8 tests must pass, new tests to be added
□ Scope: function-level — not "update app.py"
□ No red-flag words: no "refactor", "improve", "clean"
```

### A2. Run the scoped Copilot prompt

```
Add two new functions to src/app.py, placed BELOW remove_signup().

Function 1 — classify_query(question: str) -> str:
  Returns "rag" if the question is qualitative (what, describe, tell me about,
  how does, explain), or "text2sql" if quantitative (how many, which, list,
  count, total, how much, how full).
  Returns "unknown" for anything else.
  Use keyword matching — no external calls.
  Single function, docstring, type annotations.

Function 2 — ask() route:
  POST /api/ask
  Reads {"question": str} from request JSON.
  Returns 400 if question field missing or empty.
  Calls classify_query() to determine route.
  If "rag": calls rag_search(question) and returns result.
  If "text2sql": calls run_text2sql(question) and returns result.
  If "unknown": returns {"answer": "I can only answer questions about
  activities. Try asking what an activity is about, or how many students
  have joined.", "source": "direct", "confidence": 1.0}
  All responses: {"answer": str, "source": str, "confidence": float}
  Status 200 on success, 400 on missing field, 500 on tool error.
  Use jsonify(). Do not modify get_activities(), signup(), remove_signup().
  Do not touch src/tests/test_app.py.
```

### A3. After Copilot generates — mandatory checks

```bash
git diff --stat HEAD
```

```
Files changed: ______
Only src/app.py changed?   □ Yes   □ No — STOP and investigate

git diff src/app.py
```

```
get_activities() modified?   □ No (good)   □ Yes (STOP — revert)
signup() modified?           □ No (good)   □ Yes (STOP — revert)
remove_signup() modified?    □ No (good)   □ Yes (STOP — revert)
classify_query() present?    □ Yes         □ No — re-prompt
ask() route present?         □ Yes         □ No — re-prompt
```

```bash
pytest src/tests/test_app.py -v
```

```
All 8 original tests pass?   □ Yes — commit   □ No — investigate
```

### A4. Add stub functions for tool integrations

Before committing, add these stubs so the code runs (Developer B will replace them):

```python
# Stubs — Developer B will replace with real implementations
def rag_search(question: str) -> dict:
    """Placeholder: returns stub RAG answer."""
    return {
        "answer": f"[RAG stub] Answer about: {question}",
        "source": "rag",
        "confidence": 0.0
    }

def run_text2sql(question: str) -> dict:
    """Placeholder: returns stub Text2SQL answer."""
    return {
        "answer": f"[Text2SQL stub] Data answer for: {question}",
        "source": "text2sql",
        "confidence": 0.0
    }
```

```bash
git add src/app.py
git commit -m "feat(capstone): add /api/ask endpoint and classify_query function

- POST /api/ask routes to rag_search() or run_text2sql() by query type
- classify_query() uses keyword matching — no external calls
- Stub implementations for rag_search and run_text2sql
- UAT-locked functions untouched (git diff verified)
- All 8 existing tests pass
- Generated with GitHub Copilot assistance"
git push
```

---

## Task B — Tool Integrations (Developer B · 40 min)

### B1. RAG Tool Integration

Create `src/extensions/kb_extension.py`:

**Scoped prompt:**

```
Create src/extensions/kb_extension.py.

Task: Implement rag_search(question: str) -> dict that:
1. Loads the FAISS vector index from vector-store/index.faiss
2. Embeds the question using the same embedding model used during indexing
3. Searches the index for the top-3 most similar chunks
4. Formats the chunks into a coherent answer string
5. Returns {"answer": str, "source": "rag", "confidence": float}
   where confidence is the top chunk's similarity score (0-1)
6. Returns {"answer": "I couldn't find information about that in our
   knowledge base.", "source": "rag", "confidence": 0.0} if no
   relevant chunks are found (similarity < 0.5)

Constraint: Do not modify src/app.py, src/tests/test_app.py, or
any existing file. This is a NEW file only.
Import only libraries already in requirements.txt.
Handle FileNotFoundError if vector-store/index.faiss doesn't exist.

Format: Module-level docstring, type annotations, one public function.
```

After generating, test manually:

```bash
python -c "from src.extensions.kb_extension import rag_search; print(rag_search('Tell me about Chess Club'))"
```

```
Returns a dict with answer, source, confidence?   □ Yes   □ No — investigate
```

### B2. Text2SQL Tool Integration

Create `src/sql/text2sql.py`:

**Scoped prompt:**

```
Create src/sql/text2sql.py.

Task: Implement run_text2sql(question: str) -> dict that:
1. Injects the activities table schema into a prompt for Copilot/LLM
   Schema: activities(name TEXT, description TEXT, schedule TEXT,
   max_participants INT, participants JSONB)
2. Uses the schema-injected prompt to generate a PostgreSQL SELECT query
3. Validates the generated SQL:
   - Must be a SELECT statement — reject any DELETE, DROP, UPDATE, INSERT
   - Must use parameterised placeholders (%s) — reject f-string SQL
   - Must reference only the activities table
4. Executes the query against the PostgreSQL database (connection from env vars)
5. Formats the result as a human-readable sentence
6. Returns {"answer": str, "source": "text2sql", "confidence": float}
   where confidence is 1.0 if query executed, 0.0 if validation failed
7. Returns error dict if execution fails

Constraint: This is a NEW file. Do not touch src/app.py or any existing file.
CRITICAL: Zero string-formatted SQL. All queries MUST use %s placeholders.
No DELETE, UPDATE, DROP, INSERT — SELECT only.
Handle database connection errors gracefully.

Format: Module-level docstring, security_validate(sql) helper function,
run_text2sql() public function, type annotations.
```

After generating, verify security:

```bash
python -c "
from src.sql.text2sql import security_validate
# These must all FAIL validation (return False)
print('DELETE test:', security_validate('DELETE FROM activities'))
print('f-string test:', security_validate(\"SELECT * WHERE name = '{name}'\"))
print('Valid test:', security_validate('SELECT name FROM activities WHERE name = %s'))
"
```

```
DELETE test returns False:   □ Yes (correct)   □ No (security gap — fix before committing)
f-string test returns False: □ Yes (correct)   □ No (security gap — fix before committing)
Valid query returns True:    □ Yes (correct)   □ No (logic error — fix)
```

### B3. Replace the stubs in src/app.py

Once both tool files are working, update the stubs in `src/app.py`:

**Scoped prompt:**

```
In src/app.py, replace the two stub functions with real imports.

Replace:
  def rag_search(question: str) -> dict:
      """Placeholder: returns stub RAG answer."""
      return {...}

  def run_text2sql(question: str) -> dict:
      """Placeholder: returns stub Text2SQL answer."""
      return {...}

With:
  from src.extensions.kb_extension import rag_search
  from src.sql.text2sql import run_text2sql

Place the imports at the top of the file with other imports.
Do NOT modify any other line in src/app.py.
```

```bash
git diff --stat HEAD
pytest src/tests/test_app.py -v
```

Commit all B changes:

```bash
git add src/extensions/ src/sql/ src/app.py
git commit -m "feat(capstone): integrate RAG and Text2SQL tools into /api/ask

- src/extensions/kb_extension.py: FAISS-based RAG search
- src/sql/text2sql.py: schema-injected parameterised SQL generation
- Security: DELETE/UPDATE/DROP validation + parameterised query check
- Stub functions replaced with real imports in app.py
- All 8 existing tests pass
- Generated with GitHub Copilot assistance"
git push
```

---

## Task C — Frontend Widget + Tests (Developer C · 30 min)

### C1. Frontend Ask Widget

Create `src/static/ask.html` (or add a widget to the existing interface):

**Scoped prompt:**

```
Create src/static/ask.html — a standalone page with an AI Q&A widget.

Task: A simple HTML page with:
1. A text input labelled "Ask about our activities"
2. A Submit button that POSTs {"question": input_value} to /api/ask
3. A result area that displays the answer
4. A small indicator showing source: "Answered from knowledge base"
   (if source === "rag") or "Answered from database" (if source === "text2sql")
   or "Direct answer" (if source === "direct")
5. A confidence indicator — only show if confidence > 0.5

Constraint: Do NOT modify src/static/index.html — this is a new file.
No external CSS frameworks — inline styles only (keeps it self-contained).
Use vanilla JavaScript fetch() — no libraries.
Handle network errors and show a friendly message if /api/ask fails.

Format: Complete self-contained HTML file with embedded CSS and JS.
```

Test manually:

```bash
# Start the Flask app
python src/app.py

# In browser: open http://localhost:5000/ask.html
# Test: "Tell me about Chess Club" (should use RAG)
# Test: "How many students in Swimming?" (should use Text2SQL)
# Test: "How do I sign up?" (should return direct guidance)
```

### C2. New Tests for the /api/ask Endpoint

**Scoped prompt:**

```
Add new pytest test functions to src/tests/test_app.py.

Task: Add tests for the /api/ask endpoint. Add them at the BOTTOM
of the file, after all existing tests.

Test cases to cover:
1. POST /api/ask with a qualitative question → 200, source "rag"
2. POST /api/ask with a quantitative question → 200, source "text2sql"
3. POST /api/ask with an unknown question → 200, source "direct"
4. POST /api/ask with missing question field → 400 status
5. POST /api/ask with empty question string → 400 status

Constraint: Do NOT modify any existing test function.
Add only new functions at the BOTTOM of the file.
Use the Flask test client (client fixture).
Each test must assert: status code AND response body keys present.

Format: 5 separate test functions, names starting with test_ask_.
```

```bash
git diff src/tests/test_app.py
```

```
Only additions at the bottom?   □ Yes   □ No — STOP

pytest src/tests/test_app.py -v
```

```
All original 8 tests pass?   □ Yes   □ No — investigate
New ask tests pass?          □ Yes   □ No — fix before committing
Total tests now: ______
```

```bash
git add src/static/ask.html src/tests/test_app.py
git commit -m "feat(capstone): add frontend widget and /api/ask tests

- src/static/ask.html: standalone Q&A widget with source indicator
- 5 new test functions for /api/ask (bottom of test_app.py only)
- 0 existing tests modified
- Generated with GitHub Copilot assistance"
git push
```

---

---

# PHASE 3 — Protect & Validate (45 min)

---

## Step 3.1 — Create the Capstone SKILL.md

Create `.github/skills/ai-ask-endpoint.md`:

```markdown
# Skill: AI Ask Endpoint

## Description
Adds the /api/ask endpoint and classify_query() routing function to the
Mergington activities API. Routes natural language questions to the RAG
knowledge base (qualitative) or Text2SQL pipeline (quantitative).

## Trigger
Use when asked to: "add a question-answering endpoint", "implement NL
routing", "add an AI Q&A feature to the activities API".

Do NOT use when:
- Modifying existing activity endpoints
- Changing the ACTIVITIES dictionary
- Updating the existing frontend (index.html)

## Constraints

### NEVER_MODIFY — UAT-locked
- `get_activities()` in src/app.py
- `signup()` in src/app.py
- `remove_signup()` in src/app.py
- All existing functions in src/tests/test_app.py
- src/static/index.html
- The ACTIVITIES dictionary structure

### API contract (must not be changed once in production)
- POST /api/ask accepts {"question": str}
- Response: {"answer": str, "source": "rag"|"text2sql"|"direct", "confidence": float}
- 400 on missing/empty question, 500 on tool failure

### Security constraints
- Text2SQL: parameterised queries only — NEVER f-string SQL
- Text2SQL: SELECT only — NEVER DELETE, UPDATE, DROP, INSERT
- RAG: answers must cite source chunks — never generate from model training data
- No user input injected into SQL strings

### Required test outcomes
- All original 8 tests must pass after this skill is used
- New tests must cover: rag routing, text2sql routing, direct routing, 400 errors
- Coverage must not drop

## Examples

### Input
"Add routing so qualitative questions go to RAG and quantitative go to Text2SQL"

### Expected output
classify_query() with keyword matching + ask() route + stub imports for tools

## DRI
Capstone team lead — [name]
## Version
v1.0 — [capstone date]
## Deprecation policy
Update when new query types are added. Review after any schema migration.
```

```bash
git add .github/skills/ai-ask-endpoint.md
git commit -m "docs: add SKILL.md for AI ask endpoint (capstone)"
git push
```

---

## Step 3.2 — Run the Full Eval Suite

```bash
npx promptfoo eval
```

```
Total assertions: ______
Passed: ______
Failed: ______
Pass rate: ______%

Target: ≥ 80% (≥ 8 of 10 assertions)

Any not-contains assertions failed?   □ No — UAT-locked code is safe
                                      □ Yes — which? ________________
                                        Fix the code or prompt before proceeding.
```

If below 80%:
1. Review which assertions failed
2. Check the code against the failing assertion
3. If code is wrong: fix it and re-run eval
4. If assertion is wrong: review and adjust

Do not proceed until ≥ 80% is achieved.

---

## Step 3.3 — Run the Complete 7-Step Pre-PR Pipeline

```bash
git push origin feature/capstone-ai-ask
```

Open a Pull Request: `feature/capstone-ai-ask` → `main`

Watch GitHub Actions — verify all steps:

```
Step 2 — Linter (Ruff):             □ Passed   □ Failed
Step 3 — Unit tests (all N tests):  □ Passed   □ Failed
Step 4 — Eval gate (≥ 80%):         □ Passed   □ Failed
Step 5 — Security scan (GHAS):      □ Passed   □ Failed
Step 6 — Auto-docs:                 □ Passed   □ Failed
Step 7 — PR opens (if all pass):    □ Yes       □ Not yet

All 6 checks passed?   □ Yes — PR is ready for review
                        □ No — fix the failing step first
```

If any step fails, record what it caught:

```
Failing step: ______
What it caught: _______________________________________________
How you fixed it: _____________________________________________
```

---

## Step 3.4 — Manual Security Review of the PR

Before requesting a team peer review, each team member individually reviews the PR diff for:

```
Security checklist — review every line of the diff:

□ Any string-formatted SQL found?
  (Look for: f"...{variable}...", "...%s..." + variable, .format())
  Found: □ No   □ Yes — line: ______

□ Any hardcoded credentials, tokens, or secrets?
  Found: □ No   □ Yes — line: ______

□ Any user input concatenated into any string?
  Found: □ No   □ Yes — line: ______

□ Any file path constructed from user input without sanitisation?
  Found: □ No   □ Yes — line: ______

□ Any of the UAT-locked functions present in the diff (modified)?
  Found: □ No   □ Yes — which: ______

All clear?   □ Yes — ready for peer review   □ No — fix before review
```

---

## Step 3.5 — Peer Code Review

One team member who did NOT write the code reviews the PR on GitHub. Use this structured review form:

```
PEER REVIEW FORM — Capstone PR
────────────────────────────────────────────────────────────────
Reviewer: _______________________   PR: #______

Code quality:
□ classify_query() correctly routes qualitative vs quantitative
□ ask() returns the correct response format for all three paths
□ 400 response returned for missing/empty question
□ rag_search() gracefully handles missing vector index
□ security_validate() correctly rejects DELETE, UPDATE, DROP
□ security_validate() correctly rejects f-string SQL patterns

Test quality:
□ All 5 new test functions test what their name says
□ Each test asserts status code AND at least one response body key
□ No existing test was modified (confirmed via diff)

Pipeline:
□ All 6 pipeline steps green in Actions tab
□ Eval pass rate ≥ 80% shown in eval step log

SKILL.md:
□ CONSTRAINTS section names all 3 UAT-locked functions
□ API contract documented
□ Security constraints listed

Decision:
□ APPROVED — ready to merge
□ CHANGES REQUESTED — see comments below

Comments:
_________________________________________________________________
_________________________________________________________________
```

---

## Step 3.6 — Merge and Verify

After peer review approval:

```bash
# On GitHub: merge the PR using "Squash and merge"
# Commit message:
# feat: add AI-powered activities Q&A (capstone)
#
# - POST /api/ask endpoint with classify_query() routing
# - RAG tool: FAISS knowledge base search
# - Text2SQL tool: parameterised PostgreSQL queries
# - Frontend widget: ask.html
# - 5 new tests (all original 8 tests preserved)
# - 12-layer UAT protection stack active
# - RAGAS faithfulness: [score] · SQL correctness: [score]
# - Eval gate: [pass rate]% ≥ 80% threshold
# - Generated with GitHub Copilot assistance

# After merge, verify main is clean:
git checkout main
git pull
pytest src/tests/test_app.py -v
```

```
All tests pass on main after merge?   □ Yes — capstone complete
                                       □ No — investigate urgently
```

---

---

# PHASE 4 — Present & Reflect (30 min)

---

## Step 4.1 — Team Demo (5 minutes per team)

Each team presents to the full cohort. Stick to 5 minutes. The question is not "does the feature work?" — it is "does the protection stack work?"

**Demonstration sequence:**

```
1. Show the AI Scope Statement (30 seconds)
   "Our UAT-locked list included: [read the three functions]"

2. Show the git log on main
   "These are the commits. Every one has AI attribution in the message."

3. Show the /api/ask endpoint in action (1 minute)
   - Type: "Tell me about the Chess Club" → shows RAG source
   - Type: "How many students are in Swimming?" → shows Text2SQL source
   - Type: "" (empty) → shows 400 response

4. Show the GitHub Actions pipeline (1 minute)
   "All 6 steps green. The PR could only open after all of these passed."

5. Show the eval scorecard (30 seconds)
   "Our promptfoo pass rate was [X]%. RAGAS faithfulness: [X].
   SQL correctness: [X]%."

6. Show one thing the pipeline caught (1 minute)
   "During development, the pipeline blocked a PR because [reason].
   Here is the step that caught it."
```

---

## Step 4.2 — Eval Scorecard

Complete your team's official scorecard. This will be presented publicly.

```
╔══════════════════════════════════════════════════════════════════════════╗
║  CAPSTONE EVAL SCORECARD                                                ║
║  Team: ______________________   Date: ___________                       ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  PROTECTION LAYERS                                                       ║
║  Layer 1  AI Scope Statement          □ Active   □ Partial   □ Missing  ║
║  Layer 2  copilot-instructions.md     □ Active   □ Partial   □ Missing  ║
║  Layer 3  Scoped prompts              □ Active   □ Partial   □ Missing  ║
║  Layer 4  git diff review             □ Active   □ Partial   □ Missing  ║
║  Layer 5  Coverage delta gate         □ Active   □ Partial   □ Missing  ║
║  Layer 6  SKILL.md constraints        □ Active   □ Partial   □ Missing  ║
║  Layer 7  Eval gate (promptfoo)       □ Active   □ Partial   □ Missing  ║
║  Layer 8  7-step pre-PR pipeline      □ Active   □ Partial   □ Missing  ║
║  Layer 9  Security scan (GHAS)        □ Active   □ Partial   □ Missing  ║
║  Layer 10 Human code review           □ Active   □ Partial   □ Missing  ║
║  Layer 11 Team AI policy              □ Active   □ Partial   □ Missing  ║
║  Layer 12 CoP knowledge base          □ Active   □ Partial   □ Missing  ║
║                                                                          ║
║  Active layers: ______ / 12                                             ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  QUALITY METRICS                                                         ║
║  promptfoo eval pass rate:       ______%   (target ≥ 80%)               ║
║  RAGAS faithfulness score:       ______    (target ≥ 0.85)              ║
║  SQL correctness score:          ______%   (target ≥ 90%)               ║
║  Test count before capstone:     ______                                  ║
║  Test count after capstone:      ______                                  ║
║  Tests removed:                  ______    (must be 0)                   ║
║  Pipeline steps green:           ______ / 6                             ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  PIPELINE INCIDENTS                                                      ║
║  How many PRs were blocked by the pipeline?   ______                    ║
║  Which step blocked the most PRs?   ______________________________      ║
║  What was the root cause of the most common block?                      ║
║  _______________________________________________________________          ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  HITL DECISIONS (if Agent Mode was used)                                ║
║  Times APPROVED without changes:   ______                               ║
║  Times REDIRECTED (scope adjusted): ______                              ║
║  Times REJECTED:   ______                                               ║
║  Most common reason for redirect/reject:                                ║
║  _______________________________________________________________          ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Step 4.3 — CoP Knowledge Base Entry

Every team documents one incident from the capstone — something that went wrong, nearly went wrong, or that the pipeline caught.

```
══════════════════════════════════════════════════════════════════
  CoP KB ENTRY — CAPSTONE INCIDENT
  Team: _______________________   Date: ___________
══════════════════════════════════════════════════════════════════

Incident title:
_______________________________________________________________

What happened:
[Describe: which prompt, which file, what Copilot did or nearly did]

_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

Which gate caught it (or would have caught it)?
□ AI Scope Statement — developer noticed during scope review
□ copilot-instructions.md — Copilot refused or flagged
□ git diff review — unexpected file appeared
□ Coverage delta gate — test count dropped
□ SKILL.md constraint — inherited by invocation
□ Eval gate (promptfoo not-contains assertion fired)
□ Unit tests — existing test failed
□ Security scan (GHAS) — flagged a pattern
□ Human code review — reviewer spotted it
□ It was NOT caught — this is a gap

Root cause:
□ Vague prompt (missing scope or constraint)
□ copilot-instructions.md not updated for new scope
□ Prompt used a red-flag word (refactor/improve/clean)
□ Agent plan not reviewed before approving
□ Eval assertion was missing for this case
□ Other: _______________________________________________

Prevention — one change that would prevent this pattern:
Gate: ___________________   Configuration: ___________________

SKILL.md update required?
□ No   □ Yes — Add to CONSTRAINTS: ___________________________

Who else should know about this?
Teams at risk: ________________________________________________
Action: Share in CoP channel by: ______________________________
══════════════════════════════════════════════════════════════════
```

---

## Step 4.4 — Individual Reflection

Complete independently before leaving. 5 minutes.

```
1. The gate that caught the most valuable issue during my capstone work:

   Gate: _______________________
   What it caught: _____________________________________________

2. The prompt mistake I made that I will not make again:

   _______________________________________________________________
   _______________________________________________________________

3. The protection layer I will add to my real project first thing Monday:

   _______________________________________________________________

4. The most surprising thing Copilot did during this capstone (good or bad):

   _______________________________________________________________
   _______________________________________________________________

5. Write the four principles from memory:

   1. AI ___________________; humans are ___________________.
   2. ___________________ but ___________________.
   3. ___________________ before you ___________________.
   4. ___________________ it ___________________.
```

---

---

# Capstone Scoring Guide

**For trainers and cohort leads.** Use this to give teams structured feedback after their demo.

| Dimension | Excellent (3) | Meets standard (2) | Needs work (1) |
|---|---|---|---|
| **Scope discipline** | Scope statement specific, all 3 functions named, no UAT-locked file touched | Scope statement written but some fields broad | Scope statement missing or UAT-locked file touched |
| **Pipeline green** | All 6 steps pass, blocked PR demonstrated | 4–5 steps pass, one gap explained | < 4 steps passing |
| **Eval quality** | ≥ 80% pass rate, ≥ 3 not-contains assertions | ≥ 80% with only contains assertions | < 80% or no not-contains assertions |
| **Test integrity** | Count increased, zero removed, 5 new tests for /api/ask | Count increased, zero removed, fewer new tests | Any existing test removed or modified |
| **Security** | Zero string-formatted SQL, validate() function present and tested | No string-formatted SQL found but no explicit validation | String-formatted SQL in generated code |
| **SKILL.md** | Complete with CONSTRAINTS naming all 3 locked functions + API contract + security rules | CONSTRAINTS present but incomplete | No CONSTRAINTS section |
| **Demo clarity** | Pipeline shown, blocked PR shown, eval scorecard presented | Feature demo + pipeline, no blocked PR example | Feature demo only |
| **CoP entry** | Specific incident, correct root cause, prevention gate named, SKILL.md update decided | Incident described but root cause vague | No incident or only theoretical |

**Maximum score: 24 points**

```
Score ranges:
20–24:  Exceptional — ready to champion AI-safe development in their team
16–19:  Strong — solid understanding, one or two areas to reinforce
12–15:  Meets standard — completed the capstone, needs coaching on gaps
< 12:   Requires additional support before independent use
```

---

# Trainer Facilitation Notes

**Common blockers and how to handle them:**

**"The FAISS index doesn't exist / RAG search crashes"**
Have a fallback `rag_search()` stub that reads the KB markdown files directly and returns the most relevant paragraph using simple keyword matching. The eval gate will still test the routing logic correctly.

**"The database isn't set up / Text2SQL fails to connect"**
Have a fallback `run_text2sql()` that uses the ACTIVITIES Python dictionary instead of PostgreSQL. The security validation function still works identically. SQL correctness eval uses mock assertions against the generated SQL string, not execution results.

**"The eval gate fails at Step 4 in the pipeline"**
Check whether the OPENAI_API_KEY secret is set in the repo. If not, the promptfoo eval cannot run. Workaround: comment out Step 4 in the pipeline YAML for the demo, run eval locally, and screenshot the result to paste into the PR comment manually.

**"The team is stuck on the frontend widget"**
This is the lowest-priority task. If time is short, skip `ask.html` — the backend endpoint is the core deliverable. The scorecard does not penalise for a missing frontend if the endpoint, tests, eval, and pipeline are all present.

**"A team's pipeline never goes fully green"**
Accept a local eval pass + passing pytest run as a valid alternative if the CI configuration has environment issues. The learning is in building the components — not in debugging CI environment secrets under time pressure.

---
