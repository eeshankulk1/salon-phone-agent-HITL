from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from ..schemas.knowledge_base import KnowledgeBaseOut, KnowledgeBaseCreate, KnowledgeBaseUpdate
from database import crud

router = APIRouter()


def _kb_entry_to_out(kb_entry) -> KnowledgeBaseOut:
    """Convert database model to output schema"""
    # For now, return empty categories list as we haven't implemented 
    # the categories field in the database model yet (keeping it simple)
    return KnowledgeBaseOut(
        id=kb_entry.id,
        question_text_example=kb_entry.question_text_example,
        answer_text=kb_entry.answer_text,
        categories=[],  # TODO: implement categories field when needed
        created_at=kb_entry.created_at,
        updated_at=kb_entry.updated_at
    )


@router.get("/", response_model=List[KnowledgeBaseOut])
def list_knowledge_base(
    q: Optional[str] = Query(None, description="Search term for LIKE query on question_text_example")
):
    """List knowledge base entries, optionally filtered by search query"""
    try:
        kb_entries = crud.list_kb(q=q)
        return [_kb_entry_to_out(entry) for entry in kb_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=KnowledgeBaseOut)
def create_knowledge_base_entry(kb_entry: KnowledgeBaseCreate):
    """Create a new knowledge base entry"""
    try:
        # Convert categories list to comma-separated string if needed
        kb_data = kb_entry.model_dump()
        # For now, ignore categories since we're keeping the model simple
        kb_data.pop('categories', None)
        
        created_entry = crud.create_kb(kb_data)
        return _kb_entry_to_out(created_entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entry_id}", response_model=KnowledgeBaseOut)
def update_knowledge_base_entry(entry_id: str, kb_update: KnowledgeBaseUpdate):
    """Update a knowledge base entry"""
    try:
        # Filter out None values and categories for now
        update_data = {k: v for k, v in kb_update.dict().items() if v is not None}
        update_data.pop('categories', None)  # Remove categories for now
        
        updated_entry = crud.update_kb(entry_id, update_data)
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Knowledge base entry not found")
        
        return _kb_entry_to_out(updated_entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}", response_model=KnowledgeBaseOut)
def get_knowledge_base_entry(entry_id: str):
    """Get a specific knowledge base entry by ID"""
    try:
        # For now, implemented with list query
        # In production, a dedicated get_by_id function
        entries = crud.list_kb()
        entry = next((e for e in entries if str(e.id) == entry_id), None)
        
        if not entry:
            raise HTTPException(status_code=404, detail="Knowledge base entry not found")
        
        return _kb_entry_to_out(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 