"""Text-to-SQL tool for converting natural language questions to parameterised SQL.

This module generates safe, parameterised SELECT queries from natural language
questions about the activities database. All queries are validated for security
before execution, with zero tolerance for string formatting vulnerabilities.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, Tuple


# Database schema definition for prompt injection
ACTIVITIES_SCHEMA = """
Table: activities
Columns:
  - name (TEXT): Activity name, unique identifier
  - description (TEXT): What the activity is about
  - schedule (TEXT): When it meets (days and times)
  - max_participants (INT): Maximum capacity
  - participants (JSONB): List of student emails signed up

Example rows:
  ('Chess Club', 'Learn strategies...', 'Fridays, 3:30 PM', 12, ['michael@...', ...])
  ('Programming Class', 'Learn fundamentals...', 'Tues/Thurs, 3:30 PM', 20, [...])
  ('Gym Class', 'Physical education...', 'M/W/F, 2:00 PM', 30, [...])
"""


def security_validate(sql: str) -> bool:
    """Validate that SQL is safe for execution.

    Checks:
    - Must be a SELECT statement only
    - No DELETE, DROP, UPDATE, INSERT, ALTER, CREATE
    - Must use parameterised placeholders (%s) not f-string formatting
    - Must reference only the activities table

    Args:
        sql: SQL query string to validate

    Returns:
        True if SQL passes all security checks, False otherwise
    """

    if not isinstance(sql, str) or not sql.strip():
        return False

    normalized = sql.strip().upper()

    # Check for dangerous operations
    dangerous_keywords = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
    for keyword in dangerous_keywords:
        if re.search(rf"\b{keyword}\b", normalized):
            return False

    # Must start with SELECT
    if not normalized.startswith("SELECT"):
        return False

    # Check for f-string style formatting (vulnerable patterns)
    if re.search(r"['\"].*{.*}.*['\"]", sql):
        return False

    # Check for format() method call
    if ".format(" in sql.lower():
        return False

    # Check for concatenation with user input patterns (e.g., ' + , " +, + ', + ")
    if re.search(r"['\"][+]|[+]['\"]|['\"]\s+[+]|[+]\s+['\"]", sql):
        return False

    # Must use %s placeholders if there are any parameters (not %d, %(name)s, etc.)
    # But we allow SELECT without parameters
    if re.search(r"%[^s\s]", sql):
        return False

    # Must reference activities table (check in uppercase since normalized is uppercase)
    if "ACTIVITIES" not in normalized:
        return False

    # Reject if trying to reference other tables (case-insensitive negative lookahead)
    if re.search(r"\bFROM\s+(?!activities\b)[a-z_]+", normalized, re.IGNORECASE):
        return False

    return True


def _generate_sql_from_question(question: str) -> Optional[str]:
    """Generate a parameterised SQL query from a natural language question.

    Uses keyword-based pattern matching to determine query intent. All generated
    queries use %s placeholders for parameterisation.

    Args:
        question: Natural language question about activities

    Returns:
        A safe, parameterised SQL SELECT query or None if unmappable
    """

    if not isinstance(question, str) or not question.strip():
        return None

    normalized = question.strip().lower()

    # Pattern: "How many X" / "How many students" / "How full"
    if any(pattern in normalized for pattern in ["how many", "how many students", "count", "total"]):
        if "chess" in normalized or "chess club" in normalized:
            sql = (
                "SELECT name, max_participants, "
                "jsonb_array_length(participants) as current "
                "FROM activities WHERE name = %s"
            )
            return sql
        if "programming" in normalized:
            sql = (
                "SELECT name, max_participants, "
                "jsonb_array_length(participants) as current "
                "FROM activities WHERE name ILIKE %s"
            )
            return sql
        if "gym" in normalized:
            sql = (
                "SELECT name, max_participants, "
                "jsonb_array_length(participants) as current "
                "FROM activities WHERE name ILIKE %s"
            )
            return sql
        # Generic: count of all activities with openings
        sql = (
            "SELECT name, max_participants, "
            "jsonb_array_length(participants) as current FROM activities"
        )
        return sql

    # Pattern: "Which activities" / "List all"
    if any(pattern in normalized for pattern in ["which activities", "list all", "what activities"]):
        return "SELECT name, description, schedule FROM activities"

    # Pattern: "Tell me about X" / "What is X" / "Describe X"
    if any(pattern in normalized for pattern in ["tell me about", "what is", "describe", "about"]):
        sql = (
            "SELECT name, description, schedule, max_participants "
            "FROM activities WHERE name ILIKE %s"
        )
        if "chess" in normalized:
            return sql
        if "programming" in normalized:
            return sql
        if "gym" in normalized:
            return sql
        # Extract activity name and search
        words = normalized.split()
        for i, word in enumerate(words):
            if word in ["about", "is"]:
                if i + 1 < len(words):
                    sql = (
                        "SELECT name, description, schedule, "
                        "max_participants FROM activities "
                        "WHERE name ILIKE %s"
                    )
                    return sql
        return "SELECT name, description, schedule FROM activities"

    # Pattern: "How many spots" / "Spots available" / "Open spots"
    if any(pattern in normalized for pattern in ["spots", "available", "openings", "capacity"]):
        sql = (
            "SELECT name, max_participants, "
            "jsonb_array_length(participants) as current, "
            "max_participants - jsonb_array_length(participants) as available "
            "FROM activities"
        )
        return sql

    # Default: return all activities
    return "SELECT name, description, schedule FROM activities"


def _execute_query(sql: str, params: List[Any] = None) -> Tuple[bool, Optional[List[Tuple]], str]:
    """Execute a validated SQL query against the activities database.

    Args:
        sql: Parameterised SQL query (must be pre-validated)
        params: List of parameters for %s placeholders

    Returns:
        Tuple of (success: bool, results: Optional[List], error_msg: str)
    """

    if params is None:
        params = []

    try:
        import psycopg2
    except ImportError:
        return False, None, "psycopg2 not available"

    try:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "activities")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "")

        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=5,
        )

        cursor = connection.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        return True, results, ""
    except Exception as exc:
        error_msg = f"Database error: {type(exc).__name__}"
        return False, None, error_msg


def _format_result(results: Optional[List[Tuple]]) -> str:
    """Format database query results into a human-readable answer.

    Args:
        results: List of tuples from database query or None

    Returns:
        Formatted answer string
    """

    if not results:
        return "No activities found."

    if len(results) == 1:
        row = results[0]
        return " | ".join(str(col) for col in row)

    lines = []
    for row in results:
        lines.append(" | ".join(str(col) for col in row))

    return "\n".join(lines)


def run_text2sql(question: str) -> Dict[str, Any]:
    """Convert a natural language question to SQL and return a formatted answer.

    Generates a SELECT query using the activities schema, validates it for
    security, executes it against PostgreSQL, and returns the result.

    Args:
        question: Natural language question about activities

    Returns:
        Dictionary with keys:
        - answer (str): Formatted result or error message
        - source (str): Always "text2sql"
        - confidence (float): 1.0 if executed successfully, 0.0 on validation failure
    """

    if not isinstance(question, str) or not question.strip():
        return {
            "answer": "Please provide a non-empty question.",
            "source": "text2sql",
            "confidence": 0.0,
        }

    # Generate SQL from question
    sql = _generate_sql_from_question(question)
    if sql is None:
        return {
            "answer": (
                "I couldn't understand that question. "
                "Try asking about activity details or how many students are enrolled."
            ),
            "source": "text2sql",
            "confidence": 0.0,
        }

    # Validate SQL for security
    if not security_validate(sql):
        return {
            "answer": "Query validation failed. The system could not safely process this request.",
            "source": "text2sql",
            "confidence": 0.0,
        }

    # Extract parameters from question for parameterised queries
    params = []
    if "%s" in sql:
        # Simple heuristic: if question mentions a specific activity, use it
        normalized = question.lower()
        for activity in [
            "chess club",
            "chess",
            "programming class",
            "programming",
            "gym class",
            "gym",
        ]:
            if activity in normalized:
                params.append(f"%{activity}%")
                break

    # Execute query
    success, results, error_msg = _execute_query(sql, params)

    if not success:
        # Database unavailable or other error — use fallback
        if "psycopg2" in error_msg:
            # Use in-memory fallback data
            try:
                from src.app import activities

                answer = "Available activities: " + ", ".join(activities.keys())
                return {
                    "answer": answer,
                    "source": "text2sql",
                    "confidence": 0.8,
                }
            except ImportError:
                pass

        return {
            "answer": f"Database unavailable: {error_msg}. Please try again later.",
            "source": "text2sql",
            "confidence": 0.0,
        }

    # Format and return results
    answer = _format_result(results)
    return {
        "answer": answer,
        "source": "text2sql",
        "confidence": 1.0,
    }
