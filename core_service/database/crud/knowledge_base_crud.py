from typing import List, Optional
from sqlalchemy import or_, func
from datetime import datetime
from ..session import SessionLocal
from ..models import KnowledgeBaseEntry


def list_kb(q: Optional[str] = None) -> List[KnowledgeBaseEntry]:
    """List knowledge base entries, optionally filtered by search query"""
    session = SessionLocal()
    try:
        query = session.query(KnowledgeBaseEntry)
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                or_(
                    KnowledgeBaseEntry.question_text_example.ilike(search_term),
                    KnowledgeBaseEntry.answer_text.ilike(search_term)
                )
            )
        return query.order_by(KnowledgeBaseEntry.created_at.desc()).all()
    finally:
        session.close()


def create_kb(data: dict) -> KnowledgeBaseEntry:
    """Create a new knowledge base entry"""
    session = SessionLocal()
    try:
        kb_entry = KnowledgeBaseEntry(**data)
        session.add(kb_entry)
        session.commit()
        session.refresh(kb_entry)
        return kb_entry
    finally:
        session.close()


def update_kb(entry_id: str, data: dict) -> Optional[KnowledgeBaseEntry]:
    """Update a knowledge base entry"""
    session = SessionLocal()
    try:
        kb_entry = session.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.id == entry_id).first()
        if not kb_entry:
            return None
        
        for key, value in data.items():
            if hasattr(kb_entry, key):
                setattr(kb_entry, key, value)
        
        kb_entry.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(kb_entry)
        return kb_entry
    finally:
        session.close()


def delete_kb(entry_id: str) -> bool:
    """Delete a knowledge base entry"""
    session = SessionLocal()
    try:
        kb_entry = session.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.id == entry_id).first()
        if not kb_entry:
            return False
        
        session.delete(kb_entry)
        session.commit()
        return True
    finally:
        session.close()


def search_kb_by_embedding(query_vec: List[float], k: int = 5) -> List[dict]:
    """
    Vector KNN over knowledge_base using pgvector cosine distance, via SQLAlchemy's Vector comparator API.
    Returns rows with a 'sim' field (cosine similarity in [0,1]).
    """
    session = SessionLocal()
    try:
        # Use comparator for clarity; cosine_distance returns distance in [0, 2]
        distance_expr = KnowledgeBaseEntry.embedding.cosine_distance(query_vec)
        sim_expr = (1 - distance_expr).label('sim')

        rows = (
            session.query(
                KnowledgeBaseEntry.id,
                KnowledgeBaseEntry.question_text_example,
                KnowledgeBaseEntry.answer_text,
                sim_expr,
            )
            .filter(or_(KnowledgeBaseEntry.valid_to.is_(None), KnowledgeBaseEntry.valid_to > func.now()))
            .order_by(distance_expr)
            .limit(k)
            .all()
        )
        # convert to plain dicts
        return [
            {
                "id": r[0],
                "question_text_example": r[1],
                "answer_text": r[2],
                "sim": float(r[3]),
            }
            for r in rows
        ]
    finally:
        session.close() 