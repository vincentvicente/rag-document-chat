from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from . import models, schemas

# 文档相关CRUD操作
def create_document(db: Session, document: schemas.DocumentCreate) -> models.Document:
    db_document = models.Document(
        original_name=document.original_name,
        file_name=document.file_name,
        file_path=document.file_path,
        mime_type=document.mime_type,
        size=document.size,
        preview_text=document.preview_text
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: str) -> Optional[models.Document]:
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_all_documents(db: Session, skip: int = 0, limit: int = 100) -> List[models.Document]:
    return db.query(models.Document).offset(skip).limit(limit).all()

def delete_document(db: Session, document_id: str) -> bool:
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_document:
        db.delete(db_document)
        db.commit()
        return True
    return False

# 文本块相关CRUD操作
def create_text_chunk(db: Session, chunk: schemas.TextChunkCreate) -> models.TextChunk:
    db_chunk = models.TextChunk(
        document_id=chunk.document_id,
        chunk_index=chunk.chunk_index,
        text=chunk.text
    )
    db.add(db_chunk)
    db.commit()
    db.refresh(db_chunk)
    return db_chunk

def get_document_chunks(db: Session, document_id: str) -> List[models.TextChunk]:
    return db.query(models.TextChunk).filter(models.TextChunk.document_id == document_id).all()

def delete_document_chunks(db: Session, document_id: str) -> int:
    result = db.query(models.TextChunk).filter(models.TextChunk.document_id == document_id).delete()
    db.commit()
    return result

# 嵌入向量相关CRUD操作
def create_embedding(db: Session, embedding: schemas.EmbeddingCreate) -> models.Embedding:
    db_embedding = models.Embedding(
        chunk_id=embedding.chunk_id,
        vector=embedding.vector
    )
    db.add(db_embedding)
    db.commit()
    db.refresh(db_embedding)
    return db_embedding

def get_chunk_embedding(db: Session, chunk_id: str) -> Optional[models.Embedding]:
    return db.query(models.Embedding).filter(models.Embedding.chunk_id == chunk_id).first()

def get_document_embeddings(db: Session, document_id: str) -> List[Dict[str, Any]]:
    # 联合查询获取文档的所有嵌入向量及其对应的文本块
    results = db.query(models.Embedding, models.TextChunk).join(
        models.TextChunk, models.Embedding.chunk_id == models.TextChunk.id
    ).filter(
        models.TextChunk.document_id == document_id
    ).all()
    
    return [{
        "chunk_id": embedding.chunk_id,
        "text": chunk.text,
        "vector": embedding.vector,
        "chunk_index": chunk.chunk_index
    } for embedding, chunk in results]

# 消息相关CRUD操作
def create_message(db: Session, message: schemas.MessageCreate) -> models.Message:
    db_message = models.Message(
        document_id=message.document_id,
        content=message.content,
        role=message.role,
        sources=message.sources
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_document_messages(db: Session, document_id: str) -> List[models.Message]:
    return db.query(models.Message).filter(models.Message.document_id == document_id).order_by(models.Message.timestamp).all()

# 查询历史相关CRUD操作
def create_query_history(db: Session, document_id: Optional[str], query: str, answer: str, sources: List[Dict[str, Any]]) -> models.QueryHistory:
    db_history = models.QueryHistory(
        document_id=document_id,
        query=query,
        answer=answer,
        sources=sources
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_query_history(db: Session, skip: int = 0, limit: int = 100) -> List[models.QueryHistory]:
    return db.query(models.QueryHistory).order_by(models.QueryHistory.timestamp.desc()).offset(skip).limit(limit).all()

