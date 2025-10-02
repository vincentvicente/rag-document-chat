from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import json
import random
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import google.generativeai as genai

from app.services.embedding_service import search_similar_chunks
from app.models import crud, schemas

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("警告: GEMINI_API_KEY 未在 .env 文件中设置。")
else:
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Gemini API 密钥配置失败: {e}")

# 处理查询
def process_query(db: Session, document_id: str, query: str) -> Dict[str, Any]:
    try:
        # 如果没有提供文档ID，使用直接对话模式（不使用RAG）
        if not document_id:
            try:
                # 直接与Gemini对话（不使用RAG）
                answer = generate_answer_without_context(query)
                return {
                    "answer": answer,
                    "sources": []
                }
            except Exception as e:
                print(f"Gemini API调用失败: {str(e)}")
                return {
                    "answer": "抱歉，我现在无法回答您的问题。请稍后再试。",
                    "sources": []
                }
        
        # 搜索相关文本块
        similar_chunks = search_similar_chunks(db, document_id, query)
        
        if not similar_chunks:
            no_info_answer = "我找不到与您问题相关的信息。"
            
            # 如果有文档ID，添加消息到数据库
            if document_id:
                message = schemas.MessageCreate(
                    document_id=document_id,
                    content=query,
                    role="user"
                )
                crud.create_message(db, message)
                
                # 添加助手消息
                assistant_message = schemas.MessageCreate(
                    document_id=document_id,
                    content=no_info_answer,
                    role="assistant",
                    sources=[]
                )
                crud.create_message(db, assistant_message)
            
            # 记录查询历史
            crud.create_query_history(db, document_id, query, no_info_answer, [])
            
            return {
                "answer": no_info_answer,
                "sources": []
            }
        
        # 构建上下文
        context = "\n\n".join([chunk["text"] for chunk in similar_chunks])
        
        # 尝试使用LLM生成回答，如果失败则使用模拟回答
        try:
            answer = generate_answer(query, context)
        except Exception as e:
            print(f"LLM API调用失败，使用模拟回答: {str(e)}")
            answer = generate_mock_answer(query, context, similar_chunks)
        
        # 如果有文档ID，添加消息到数据库
        if document_id:
            # 添加用户消息
            user_message = schemas.MessageCreate(
                document_id=document_id,
                content=query,
                role="user"
            )
            crud.create_message(db, user_message)
            
            # 添加助手消息
            assistant_message = schemas.MessageCreate(
                document_id=document_id,
                content=answer,
                role="assistant",
                sources=[{
                    "text": chunk["text"],
                    "score": chunk["score"],
                    "distance": chunk.get("distance")
                } for chunk in similar_chunks]
            )
            crud.create_message(db, assistant_message)
        
        # 记录查询历史
        crud.create_query_history(
            db, 
            document_id, 
            query, 
            answer, 
            [{
                "text": chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"],
                "score": chunk["score"]
            } for chunk in similar_chunks]
        )
        
        return {
            "answer": answer,
            "sources": [{
                "text": chunk["text"],
                "score": chunk["score"]
            } for chunk in similar_chunks]
        }
    except Exception as e:
        print(f"处理查询时出错: {str(e)}")
        return {
            "answer": f"处理您的问题时出现了错误，但这是测试模式下的模拟回答。错误: {str(e)}",
            "sources": []
        }

# 生成模拟回答 (用于测试，不需要API密钥)
def generate_mock_answer(query: str, context: str, chunks: List[Dict[str, Any]]) -> str:
    print("使用模拟回答模式 (测试用)")
    
    # 从chunks中提取一些文本作为回答的基础
    first_chunk = chunks[0]["text"] if chunks else ""
    second_chunk = chunks[1]["text"] if len(chunks) > 1 else ""
    
    # 根据查询内容生成不同的模拟回答
    if "什么" in query or "是什么" in query:
        return f"根据文档内容，这是关于{first_chunk[:30]}的信息。文档中提到：{first_chunk[:100]}..."
    elif "如何" in query or "怎么" in query:
        return f"文档中关于这个问题的说明是：{first_chunk[:120]}... 您可以按照以上步骤操作。"
    elif "为什么" in query:
        second_part = f"另外还提到：{second_chunk[:50]}..." if second_chunk else ""
        return f"根据文档解释，原因是：{first_chunk[:100]}... {second_part}"
    else:
        return f"您询问的是关于\"{query}\"的问题。文档中相关的内容是：{first_chunk[:150]}... 这是测试模式下的模拟回答，没有使用实际的AI生成。"

# 直接与Gemini对话（不使用上下文/RAG）
def generate_answer_without_context(query: str) -> str:
    try:
        # 检查API密钥是否已配置
        if not api_key:
            raise ValueError("GEMINI_API_KEY 未配置")
            
        # 创建模型
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 创建简单的对话提示
        prompt = f"""You are a helpful AI assistant. Please answer the user's question in a natural and friendly way.

Question: {query}
"""
        
        # 生成回答
        response = model.generate_content(prompt)
        
        # 返回生成的文本
        return response.text
    except Exception as e:
        print(f"生成无上下文回答时出错: {str(e)}")
        raise e

# 使用LLM生成回答 (需要API密钥)
def generate_answer(query: str, context: str) -> str:
    try:
        # 检查API密钥是否已配置
        if not api_key:
            raise ValueError("GEMINI_API_KEY 未配置，无法调用LLM。")
            
        # 创建模型
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 创建提示
        prompt_template = """你是一个专业的文档问答助手。请根据提供的上下文回答用户的问题。
        如果上下文中没有相关信息，请直接说明你无法回答该问题。
        不要编造信息，只使用提供的上下文。
        尽量提供简洁、准确的回答。
        
        上下文：
        {context}
        
        问题：{query}
        """
        
        prompt = prompt_template.format(context=context, query=query)
        
        # 生成回答
        response = model.generate_content(prompt)
        
        # 返回生成的文本
        return response.text
    except Exception as e:
        print(f"生成回答时出错: {str(e)}")
        raise e

# 获取查询历史
def get_query_history(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    history_items = crud.get_query_history(db, skip, limit)
    
    return [{
        "id": item.id,
        "document_id": item.document_id,
        "query": item.query,
        "answer": item.answer[:100] + "..." if len(item.answer) > 100 else item.answer,
        "timestamp": item.timestamp
    } for item in history_items]

# 获取ChatBot
def get_chat_bot(db: Session, document_id: str) -> Optional[Dict[str, Any]]:
    document = crud.get_document(db, document_id)
    if not document:
        return None
    
    messages = crud.get_document_messages(db, document_id)
    
    return {
        "id": document.id,
        "title": document.original_name,
        "messages": [{
            "id": msg.id,
            "content": msg.content,
            "role": msg.role,
            "timestamp": msg.timestamp,
            "sources": msg.sources
        } for msg in messages],
        "created": document.upload_date
    }

# 获取所有ChatBot
def get_all_chat_bots(db: Session) -> List[Dict[str, Any]]:
    documents = crud.get_all_documents(db)
    
    result = []
    for doc in documents:
        messages = crud.get_document_messages(db, doc.id)
        
        result.append({
            "id": doc.id,
            "title": doc.original_name,
            "message_count": len(messages),
            "created": doc.upload_date
        })
    
    return result