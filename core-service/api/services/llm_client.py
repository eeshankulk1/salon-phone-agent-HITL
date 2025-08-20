"""
LLM Client Service - Abstracts LLM operations for modularity
"""
from typing import List, Optional
from openai import OpenAI


class LLMClient:
    """
    Abstraction layer for LLM operations.
    Makes it easy to swap out different LLM providers or models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM client.
        
        Args:
            api_key: OpenAI API key. If None, will use environment variable.
        """
        self.client = OpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-small"
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for the given text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            Exception: If the API call fails
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")


# Global instance - can be configured with dependency injection if needed
llm_client = LLMClient() 