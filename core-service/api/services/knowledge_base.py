from ..services.embeddings import embed_question
from database import crud
from typing import List, Sequence, Union


def _normalize_embedding_vector(vector: Union[Sequence[float], Sequence[int], Sequence[Union[float, int]]]) -> List[float]:
    """Ensure the embedding is a 1D list[float].
    Accepts a list or tuple and flattens a single nested dimension if present.
    Raises ValueError for invalid shapes or element types.
    """
    # Handle single-nested list like [[...]] by unwrapping
    if isinstance(vector, (list, tuple)) and len(vector) == 1 and isinstance(vector[0], (list, tuple)):
        vector = vector[0]  # type: ignore[assignment]

    if not isinstance(vector, (list, tuple)):
        raise ValueError("Embedding must be a list or tuple of floats")

    # Validate all numeric and coerce to float
    normalized: List[float] = []
    for value in vector:  # type: ignore[assignment]
        if isinstance(value, (int, float)):
            normalized.append(float(value))
        else:
            raise ValueError("Embedding contains non-numeric values")

    return normalized


def create_knowledge_base_from_text(question: str, answer: str, source_help_request_id=None):
    vector_embedding = _normalize_embedding_vector(embed_question(question))
    payload = {
        "question_text_example": question,
        "answer_text": answer,
        "source_help_request_id": source_help_request_id,
        "embedding": vector_embedding,
    }
    return crud.create_kb(payload)


def search_knowledge_base_by_question(question: str, k: int = 5, min_sim: float = 0.70):
    q_vec = _normalize_embedding_vector(embed_question(question))
    rows = crud.search_kb_by_embedding(q_vec, k=k)
    return [r for r in rows if r["sim"] >= min_sim]