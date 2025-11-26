from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.rag_service import (
    process_query,
    get_query_history,
    get_chat_bot,
    get_all_chat_bots
)

router = APIRouter()

class QueryRequest(BaseModel):
    documentId: Optional[str] = None 
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

# Handle query
@router.post("/", response_model=QueryResponse)
async def handle_query(request: QueryRequest, db: Session = Depends(get_db)):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query content cannot be empty")
    
    try:
        result = process_query(db, request.documentId, request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

# Get query history
@router.get("/history")
async def get_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        history = get_query_history(db, skip, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

# Get chat history for specific document
@router.get("/chatbot/{document_id}")
async def get_document_chat(document_id: str, db: Session = Depends(get_db)):
    chat_bot = get_chat_bot(db, document_id)
    if not chat_bot:
        raise HTTPException(status_code=404, detail="Chat history not found for this document")
    return chat_bot

# Get all chatbots
@router.get("/chatbots")
async def get_chatbots(db: Session = Depends(get_db)):
    return get_all_chat_bots(db)