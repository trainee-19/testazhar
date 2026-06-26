from fastapi.testclient import TestClient

from src.app import app, classify_query


client = TestClient(app)


def test_classify_query_routes_rag_questions():
    assert classify_query("What is Chess Club about?") == "rag"
    assert classify_query("Describe the programming class") == "rag"


def test_classify_query_routes_text2sql_questions():
    assert classify_query("How many students joined?") == "text2sql"
    assert classify_query("Which activities have the most participants?") == "text2sql"


def test_classify_query_returns_unknown_for_unmatched_questions():
    assert classify_query("Please help me with my homework") == "unknown"


def test_ask_route_returns_400_for_missing_question():
    response = client.post("/api/ask", json={})
    assert response.status_code == 400
    assert response.json()["source"] == "direct"


def test_ask_route_routes_rag_questions():
    response = client.post("/api/ask", json={"question": "What is Chess Club about?"})
    assert response.status_code == 200
    assert response.json()["source"] == "rag"
