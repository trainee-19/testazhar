"""Knowledge base extension for FAISS-backed RAG search.

This module provides a single public helper for searching a FAISS vector
store and returning a structured RAG response.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List


def rag_search(question: str) -> Dict[str, Any]:
    """Search the FAISS vector store for the question and return an answer.

    The function loads the index from vector-store/index.faiss, embeds the
    provided question with a deterministic fallback, retrieves the top three
    matching chunks, and returns the best answer along with a confidence score.
    Falls back to searching in-memory activities when the vector store is unavailable.
    """

    def _fallback_response() -> Dict[str, Any]:
        return {
            "answer": "I couldn't find information about that in our knowledge base.",
            "source": "rag",
            "confidence": 0.0,
        }

    def _search_activities(query: str) -> Dict[str, Any]:
        """Search the activities dictionary for relevant information."""
        try:
            from src.app import activities
        except ImportError:
            return _fallback_response()

        normalized_query = query.strip().lower()
        if not normalized_query:
            return _fallback_response()

        best_match = None
        best_score = 0.0

        for activity_name, activity_data in activities.items():
            name_lower = activity_name.lower()
            desc_lower = activity_data.get("description", "").lower()
            combined = f"{name_lower} {desc_lower}".lower()

            score = 0.0
            for word in normalized_query.split():
                if len(word) > 2:
                    if word in name_lower:
                        score += 0.5
                    if word in desc_lower:
                        score += 0.3

            if score > best_score:
                best_score = score
                best_match = activity_data

        if best_match is None or best_score < 0.3:
            return _fallback_response()

        answer_parts = [
            best_match.get("description", ""),
            f"Schedule: {best_match.get('schedule', 'Not specified')}",
            f"Max participants: {best_match.get('max_participants', 'Not specified')}",
            f"Current signups: {len(best_match.get('participants', []))}",
        ]

        answer = "\n".join(part for part in answer_parts if part)
        return {
            "answer": answer,
            "source": "rag",
            "confidence": min(0.95, best_score),
        }

    def _get_index_path() -> Path:
        return Path(__file__).resolve().parents[2] / "vector-store" / "index.faiss"

    def _load_index(index_path: Path):
        try:
            import faiss
        except ImportError as exc:
            raise RuntimeError("FAISS is required for rag_search") from exc

        return faiss.read_index(str(index_path)), faiss

    def _embed_text(text: str, dimension: int) -> List[List[float]]:
        normalized = text.strip().lower().encode("utf-8")
        if dimension <= 0:
            raise ValueError("Invalid embedding dimension")

        vector = [0.0] * dimension
        for offset, byte in enumerate(normalized):
            vector[offset % dimension] += float(byte)

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [[value / norm for value in vector]]

    def _load_chunk_map(index_path: Path) -> Dict[str, str]:
        candidate_files = [
            index_path.with_name("chunks.json"),
            index_path.with_name("metadata.json"),
            index_path.with_name("index.json"),
        ]
        for candidate in candidate_files:
            if not candidate.exists():
                continue
            try:
                with candidate.open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
            except Exception:
                continue

            if isinstance(payload, dict):
                return {str(key): str(value) for key, value in payload.items()}
            if isinstance(payload, list):
                return {str(index): str(item) for index, item in enumerate(payload)}

        return {}

    if not isinstance(question, str) or not question.strip():
        return _fallback_response()

    index_path = _get_index_path()
    
    # Try FAISS first if available
    if index_path.exists():
        try:
            index, faiss = _load_index(index_path)
            query_vector = _embed_text(question, int(index.d))
            distances, indices = index.search(query_vector, 3)

            if not hasattr(indices, "shape") or not indices.size:
                return _fallback_response()

            chunk_map = _load_chunk_map(index_path)
            chunks: List[str] = []
            for idx in indices[0].tolist():
                if idx is None or idx < 0:
                    continue
                chunk = chunk_map.get(str(idx))
                if chunk is None:
                    chunk = chunk_map.get(str(int(idx)))
                if chunk is None:
                    chunk = f"[chunk {int(idx)}]"
                chunks.append(chunk)

            if not chunks:
                return _search_activities(question)

            best_distance = float(distances[0][0]) if distances.size else float("inf")
            metric = getattr(index, "metric_type", None)
            if metric is not None and hasattr(faiss, "METRIC_INNER_PRODUCT") and metric == faiss.METRIC_INNER_PRODUCT:
                confidence = max(0.0, min(1.0, best_distance))
            else:
                confidence = 1.0 / (1.0 + best_distance) if best_distance >= 0.0 else 0.0

            if confidence < 0.5:
                return _search_activities(question)

            answer = "\n\n".join(chunk.strip() for chunk in chunks if chunk and chunk.strip())
            if not answer:
                return _search_activities(question)

            return {
                "answer": answer,
                "source": "rag",
                "confidence": confidence,
            }
        except Exception:
            return _search_activities(question)
    
    # Fallback: search activities when FAISS unavailable
    return _search_activities(question)
