from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base

class Document(Base):
    """文档模型"""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    original_name = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.now)
    preview_text = Column(Text, nullable=True)
    
    # 关系
    chunks = relationship("TextChunk", back_populates="document", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="document", cascade="all, delete-orphan")

class TextChunk(Base):
    """文本块模型"""
    __tablename__ = "text_chunks"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    
    # 关系
    document = relationship("Document", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")

class Embedding(Base):
    """嵌入向量模型"""
    __tablename__ = "embeddings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    chunk_id = Column(String, ForeignKey("text_chunks.id", ondelete="CASCADE"), unique=True, nullable=False)
    vector = Column(JSON, nullable=False)  # 存储嵌入向量，JSON格式
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    chunk = relationship("TextChunk", back_populates="embedding")

class Message(Base):
    """消息模型"""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # "user" 或 "assistant"
    timestamp = Column(DateTime, default=datetime.now)
    sources = Column(JSON, nullable=True)  # 存储引用源，JSON格式
    
    # 关系
    document = relationship("Document", back_populates="messages")

class QueryHistory(Base):
    """查询历史模型"""
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    sources = Column(JSON, nullable=True)  # 存储引用源，JSON格式

