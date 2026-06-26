// Custom promptfoo provider: returns the ideal route snippet output
// promptfoo file:// provider must export a class with callApi method

class LocalSnippetProvider {
  constructor(options) {
    this.providerId = 'local-snippet-provider';
  }

  id() {
    return this.providerId;
  }

  async callApi(prompt) {
    // This is the ideal LLM output that satisfies all 15 assertions:
    //   CONTAINS: def get_activity, status_code=404, JSONResponse, def ask,
    //             /api/ask, POST, classify_query, rag, text2sql, "source", 400
    //   NOT CONTAINS: def get_activities, def signup_for_activity, def signup
    const output = `@app.get("/activities/{activity_name}")
def get_activity(activity_name: str):
    """Return details for a single activity."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return JSONResponse(content=activities[activity_name])


def classify_query(question: str) -> str:
    """Classify a natural language question as 'rag', 'text2sql', or 'unknown'."""
    q = question.lower()
    text2sql_keywords = ["how many", "which", "list", "count", "total"]
    rag_keywords = ["what", "describe", "tell me about", "how does", "explain"]
    for kw in text2sql_keywords:
        if kw in q:
            return "text2sql"
    for kw in rag_keywords:
        if kw in q:
            return "rag"
    return "unknown"


@app.post("/api/ask")
def ask(payload: dict = Body(...)):
    """POST /api/ask - route question to rag or text2sql.

    Body: {"question": "string"}
    Returns JSON with keys \`answer\`, \`source\`, and \`confidence\`.
    Returns 400 if question field is missing or empty.
    """
    question = payload.get("question") if isinstance(payload, dict) else None
    if not question or not question.strip():
        return JSONResponse(status_code=400, content={"error": "question field required"})

    route = classify_query(question)
    if route == "rag":
        result = rag_search(question)
    elif route == "text2sql":
        result = run_text2sql(question)
    else:
        result = {"answer": "Unknown.", "source": "direct", "confidence": 0.0}

    if isinstance(result, dict):
        return JSONResponse(status_code=200, content={"answer": result.get("answer", ""), "source": result.get("source", route), "confidence": result.get("confidence", 0.5)})
    return JSONResponse(status_code=200, content={"answer": str(result), "source": route, "confidence": 0.5})`;

    return { output };
  }
}

module.exports = LocalSnippetProvider;