import numpy as np
from typing import Dict, List, Any, Optional
import os
import json
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.utils.text_splitter import split_text
from app.models import crud, schemas

# 加载环境变量
load_dotenv()

# 将文本分块并生成嵌入向量
def process_and_store_embeddings(db: Session, document_id: str, text: str) -> Dict[str, Any]:
    try:
        # 将文本分成块 - 使用AI Buddy项目的方法
        # 首先按页面分割（假设文本中的双换行符表示页面分隔）
        pages = text.split('\n\n\n')
        pages = [page for page in pages if page.strip()]
        chunks = []
        
        # 将每页分为上下两部分
        for page in pages:
            if not page.strip():
                continue
            
            # 将页面分为上下两部分
            mid_point = len(page) // 2
            upper_half = page[:mid_point].strip()
            lower_half = page[mid_point:].strip()
            
            if upper_half:
                chunks.append(upper_half)
            if lower_half:
                chunks.append(lower_half)
        
        # 如果分块后的文本太少，使用原始分块方法
        if len(chunks) < 5:
            print("页面分块产生的块太少，使用原始分块方法")
            original_chunks = split_text(text)
            chunks.extend(original_chunks)
        
        print(f"文档分成了 {len(chunks)} 个文本块")
        
        # 批处理生成嵌入 - 借鉴AI Buddy项目的批处理方法
        batch_size = 100  # 与AI Buddy项目保持一致
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + min(batch_size, len(chunks) - i)]
            print(f"处理批次 {i//batch_size + 1} / {(len(chunks) + batch_size - 1)//batch_size}")
            
            # 为批次中的每个块生成嵌入并存储到数据库
            for j, chunk_text in enumerate(batch):
                # 创建文本块
                chunk = schemas.TextChunkCreate(
                    document_id=document_id,
                    text=chunk_text,
                    chunk_index=i + j
                )
                db_chunk = crud.create_text_chunk(db, chunk)
                
                # 生成嵌入向量
                embedding_vector = generate_embedding(chunk_text)
                
                # 存储嵌入向量
                embedding = schemas.EmbeddingCreate(
                    chunk_id=db_chunk.id,
                    vector=embedding_vector
                )
                crud.create_embedding(db, embedding)
        
        return {
            "document_id": document_id,
            "chunk_count": len(chunks)
        }
    except Exception as e:
        print(f"处理嵌入时出错: {str(e)}")
        raise Exception(f"处理嵌入失败: {str(e)}")

# 生成文本的嵌入向量
def generate_embedding(text: str) -> List[float]:
    try:
        # 从环境变量读取API密钥
        api_key = os.getenv("GEMINI_API_KEY")
        
        # 如果密钥可用，使用Gemini API
        if api_key:
            try:
                import google.generativeai as genai
                
                # 配置API密钥
                genai.configure(api_key=api_key)
                
                # 使用Gemini的嵌入模型
                embedding_model = 'models/embedding-001'
                
                # 生成嵌入
                result = genai.embed_content(
                    model=embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
                
                # 返回嵌入向量
                return result["embedding"]
                
            except Exception as api_error:
                print(f"Gemini API嵌入生成失败，使用模拟嵌入: {str(api_error)}")
        else:
            print("警告: GEMINI_API_KEY 未设置，使用模拟嵌入")
        
        # 模拟的嵌入向量（如果API调用失败或没有API密钥）
        return np.random.normal(0, 0.1, 384).tolist()
    except Exception as e:
        print(f"生成嵌入时出错: {str(e)}")
        raise e

# 搜索相关的文本块
def search_similar_chunks(db: Session, document_id: str, query: str, limit: int = 4) -> List[Dict[str, Any]]:
    try:
        if not document_id:
            # 如果没有指定文档ID，搜索所有文档
            return search_all_documents(db, query, limit)
        
        # 获取文档的所有嵌入向量
        embeddings = crud.get_document_embeddings(db, document_id)
        
        if not embeddings:
            raise Exception(f"未找到文档ID的嵌入: {document_id}")
        
        # 生成查询的嵌入
        query_embedding = generate_embedding(query)
        
        # 使用欧几里得距离计算相似度 - 借鉴AI Buddy项目
        results = []
        for item in embeddings:
            distance = calculate_euclidean_distance(query_embedding, item["vector"])
            results.append({
                **item,
                "distance": distance,
                "score": 0  # 将在后面计算
            })
        
        # 按距离排序（距离越小越相似）
        results.sort(key=lambda x: x["distance"])
        results = results[:limit]
        
        # 将距离转换为分数（1 - 归一化距离）
        max_distance = max(result["distance"] for result in results) if results else 1
        for item in results:
            item["score"] = 1 - (item["distance"] / max_distance)
        
        return [{
            "text": item["text"],
            "score": item["score"],
            "distance": item["distance"]
        } for item in results]
    except Exception as e:
        print(f"搜索相似块时出错: {str(e)}")
        raise e

# 计算欧几里得距离 - 从AI Buddy项目借鉴
def calculate_euclidean_distance(vec_a: List[float], vec_b: List[float]) -> float:
    if len(vec_a) != len(vec_b):
        raise ValueError("向量维度必须相同")
    
    return np.sqrt(np.sum(np.square(np.array(vec_a) - np.array(vec_b))))

# 搜索所有文档
def search_all_documents(db: Session, query: str, limit: int) -> List[Dict[str, Any]]:
    # 获取所有文档
    documents = crud.get_all_documents(db)
    
    all_results = []
    for document in documents:
        try:
            # 搜索每个文档中的相似块
            similar_chunks = search_similar_chunks(db, document.id, query, limit=2)  # 每个文档取2个最相似的块
            
            # 添加文档ID
            for chunk in similar_chunks:
                chunk["document_id"] = document.id
            
            all_results.extend(similar_chunks)
        except Exception as e:
            print(f"搜索文档 {document.id} 时出错: {str(e)}")
    
    # 按相似度排序
    all_results.sort(key=lambda x: x["score"], reverse=True)
    
    # 返回前limit个结果
    return all_results[:limit]

# 删除文档的嵌入
def delete_embeddings(db: Session, document_id: str) -> bool:
    # 获取文档的所有文本块
    chunks = crud.get_document_chunks(db, document_id)
    
    # 删除每个文本块的嵌入（通过级联删除自动处理）
    # 删除所有文本块（通过级联删除自动处理嵌入）
    return crud.delete_document_chunks(db, document_id) > 0