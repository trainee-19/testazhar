"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
import os
from pathlib import Path

try:
    from src.extensions.kb_extension import rag_search
    from src.sql.text2sql import run_text2sql
except ModuleNotFoundError:
    from extensions.kb_extension import rag_search
    from sql.text2sql import run_text2sql

app = FastAPI(
    title="Mergington High School API",
    description=(
        "API for viewing and signing up for extracurricular activities"
    ),
)

# Mount the static files directory
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
    name="static",
)


# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/ask.html")
def ask_page():
    return RedirectResponse(url="/static/ask.html")

# ============================================================
# UAT-LOCKED: This route has passed UAT. DO NOT MODIFY.
# ============================================================
@app.get("/activities")
def get_activities():
    return activities


@app.get("/activities/{activity_name}")
def get_activity(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]


# ============================================================
# UAT-LOCKED: This route has passed UAT. DO NOT MODIFY.
# ============================================================
@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}



def classify_query(question: str) -> str:
    """Classify a question as either qualitative, quantitative, or unknown."""
    if not isinstance(question, str):
        return "unknown"

    normalized = question.strip().lower()
    rag_keywords = ("what", "describe", "tell me about", "how does", "explain")
    if any(keyword in normalized for keyword in rag_keywords):
        return "rag"
    sql_keywords = (
        "how many",
        "which",
        "list",
        "count",
        "total",
        "how much",
        "how full",
    )
    if any(keyword in normalized for keyword in sql_keywords):
        return "text2sql"
    return "unknown"





@app.post("/api/ask")
async def ask(request: Request) -> JSONResponse:
    """Route user questions to either RAG or text-to-SQL helpers."""
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "answer": "Please provide a non-empty question.",
                "source": "direct",
                "confidence": 1.0,
            },
        )

    if not isinstance(payload, dict):
        return JSONResponse(
            status_code=400,
            content={
                "answer": "Please provide a non-empty question.",
                "source": "direct",
                "confidence": 1.0,
            },
        )

    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        return JSONResponse(
            status_code=400,
            content={
                "answer": "Please provide a non-empty question.",
                "source": "direct",
                "confidence": 1.0,
            },
        )

    route = classify_query(question)
    try:
        if route == "rag":
            result = rag_search(question)
            return JSONResponse(status_code=200, content=result)
        if route == "text2sql":
            result = run_text2sql(question)
            return JSONResponse(status_code=200, content=result)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "answer": "I couldn't process that question right now.",
                "source": "direct",
                "confidence": 0.0,
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "answer": (
                "I can only answer questions about activities. "
                "Try asking what an activity is about, "
                "or how many students have joined."
            ),
            "source": "direct",
            "confidence": 1.0,
        },
    )



