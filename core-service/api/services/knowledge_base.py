from ..services.embeddings import embed_question
from database import crud
from typing import List, Sequence, Union, Optional, Dict, Any


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


def update_knowledge_base_from_text(entry_id: str, update_data: Dict[str, Any]) -> Optional[Any]:
    """
    Update a knowledge base entry with automatic embedding updates.
    
    If the question_text_example is being updated, this function will:
    1. Generate a new embedding for the updated question
    2. Include the embedding in the update data
    3. Update the knowledge base entry with all changes
    
    Args:
        entry_id: The ID of the knowledge base entry to update
        update_data: Dictionary containing the fields to update
        
    Returns:
        Updated KnowledgeBaseEntry or None if not found
        
    Raises:
        Exception: If embedding generation or database update fails
    """
    # Create a copy of update_data to avoid modifying the original
    processed_update_data = update_data.copy()
    
    # If question text is being updated, generate new embedding
    if "question_text_example" in processed_update_data:
        new_question = processed_update_data["question_text_example"]
        if new_question:  # Only if the new question is not empty
            vector_embedding = _normalize_embedding_vector(embed_question(new_question))
            processed_update_data["embedding"] = vector_embedding
    
    # Update the knowledge base entry with all data (including embedding if applicable)
    return crud.update_kb(entry_id, processed_update_data)


def search_knowledge_base_by_question(question: str, k: int = 5, min_sim: float = 0.70):
    q_vec = _normalize_embedding_vector(embed_question(question))
    rows = crud.search_kb_by_embedding(q_vec, k=k)
    return [r for r in rows if r["sim"] >= min_sim]