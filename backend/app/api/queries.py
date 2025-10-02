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

# 处理查询
@router.post("/", response_model=QueryResponse)
async def handle_query(request: QueryRequest, db: Session = Depends(get_db)):
    if not request.query:
        raise HTTPException(status_code=400, detail="查询内容不能为空")
    
    try:
        result = process_query(db, request.documentId, request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理查询失败: {str(e)}")

# 获取查询历史
@router.get("/history")
async def get_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        history = get_query_history(db, skip, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

# 获取特定文档的聊天历史
@router.get("/chatbot/{document_id}")
async def get_document_chat(document_id: str, db: Session = Depends(get_db)):
    chat_bot = get_chat_bot(db, document_id)
    if not chat_bot:
        raise HTTPException(status_code=404, detail="未找到该文档的聊天记录")
    return chat_bot

# 获取所有聊天机器人
@router.get("/chatbots")
async def get_chatbots(db: Session = Depends(get_db)):
    return get_all_chat_bots(db)