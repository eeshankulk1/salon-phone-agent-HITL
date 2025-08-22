"""
Embeddings Service - Handles text embedding operations
"""
from typing import List
from .llm_client import llm_client


def embed_question(text: str) -> List[float]:
    """
    Generate embedding vector for a question/text.
    
    This function provides a clean interface for embedding operations,
    making it easy to swap out the underlying LLM provider if needed.
    
    Args:
        text: The text/question to embed
        
    Returns:
        List of floats representing the embedding vector
        
    Raises:
        Exception: If embedding generation fails
    """
    return llm_client.get_embedding(text) 