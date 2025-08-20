from ..services.embeddings import embed_question
from database import crud

def create_knowledge_base_from_text(question: str, answer: str, source_help_request_id=None):
    vector_embedding = embed_question(question)
    payload = {
        "question_text_example": question,
        "answer_text": answer,
        "source_help_request_id": source_help_request_id,
        "embedding": vector_embedding,
    }
    return crud.create_kb(payload)