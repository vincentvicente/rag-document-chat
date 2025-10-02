from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 文档相关模型
class DocumentBase(BaseModel):
    original_name: str
    mime_type: str
    size: int

class DocumentCreate(DocumentBase):
    file_name: str
    file_path: str
    preview_text: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: str
    upload_date: datetime
    preview_text: Optional[str] = None
    message_count: Optional[int] = 0
    chunk_count: Optional[int] = 0

    class Config:
        from_attributes = True

# 文本块相关模型
class TextChunkBase(BaseModel):
    text: str
    chunk_index: int

class TextChunkCreate(TextChunkBase):
    document_id: str

class TextChunkResponse(TextChunkBase):
    id: str
    document_id: str

    class Config:
        from_attributes = True

# 嵌入向量相关模型
class EmbeddingCreate(BaseModel):
    chunk_id: str
    vector: List[float]

class EmbeddingResponse(BaseModel):
    id: str
    chunk_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# 消息相关模型
class MessageBase(BaseModel):
    content: str
    role: str
    sources: Optional[List[Dict[str, Any]]] = None

class MessageCreate(MessageBase):
    document_id: str

class MessageResponse(MessageBase):
    id: str
    document_id: str
    timestamp: datetime

    class Config:
        from_attributes = True

# 查询相关模型
class QueryRequest(BaseModel):
    documentId: str
    query: str

class SourceResponse(BaseModel):
    text: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceResponse]

# 查询历史相关模型
class QueryHistoryResponse(BaseModel):
    id: int
    document_id: Optional[str]
    query: str
    answer: str
    timestamp: datetime
    sources: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True

# ChatBot相关模型
class ChatBotResponse(BaseModel):
    id: str
    title: str
    messages: List[MessageResponse]
    created: datetime

class ChatBotSummary(BaseModel):
    id: str
    title: str
    message_count: int
    created: datetime

