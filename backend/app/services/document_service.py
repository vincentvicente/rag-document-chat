import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil
from sqlalchemy.orm import Session

from app.utils.file_parser import parse_file
from app.services.embedding_service import process_and_store_embeddings
from app.models import crud, schemas

# 处理上传的文档
def process_document(db: Session, file_info: Dict[str, Any]) -> Dict[str, Any]:
    try:
        file_path = file_info["file_path"]
        file_extension = os.path.splitext(file_info["original_name"])[1].lower()
        
        # 解析文档内容
        text = parse_file(file_path, file_extension)
        
        # 创建文档记录，添加预览文本
        preview_text = text[:200] + "..." if len(text) > 200 else text
        
        # 存储文档到数据库
        document = schemas.DocumentCreate(
            original_name=file_info["original_name"],
            file_name=file_info["file_name"],
            file_path=file_info["file_path"],
            mime_type=file_info["mime_type"],
            size=file_info["size"],
            preview_text=preview_text
        )
        
        db_document = crud.create_document(db, document)
        
        print(f"开始处理文档: {db_document.original_name}")
        
        # 生成嵌入向量并存储
        embedding_result = process_and_store_embeddings(db, db_document.id, text)
        print(f"文档处理完成: {embedding_result['chunk_count']} 个文本块已处理")
        
        return {
            "id": db_document.id,
            "originalName": db_document.original_name,
            "uploadDate": db_document.upload_date,
            "previewText": db_document.preview_text,
            "chunkCount": embedding_result["chunk_count"]
        }
    except Exception as e:
        print(f"处理文档时出错: {str(e)}")
        # 如果文件存在，尝试删除
        if os.path.exists(file_info["file_path"]):
            try:
                os.remove(file_info["file_path"])
            except Exception as del_e:
                print(f"删除文件时出错: {str(del_e)}")
        raise Exception(f"处理文档失败: {str(e)}")

# 获取所有文档
def get_all_documents(db: Session) -> List[Dict[str, Any]]:
    documents = crud.get_all_documents(db)
    
    result = []
    for doc in documents:
        # 获取文档的消息数量
        messages = crud.get_document_messages(db, doc.id)
        
        result.append({
            "id": doc.id,
            "originalName": doc.original_name,
            "uploadDate": doc.upload_date,
            "previewText": doc.preview_text,
            "messageCount": len(messages)
        })
    
    return result

# 根据ID获取文档
def get_document_by_id(db: Session, document_id: str) -> Optional[Dict[str, Any]]:
    doc = crud.get_document(db, document_id)
    if not doc:
        return None
    
    # 获取文档的消息数量
    messages = crud.get_document_messages(db, doc.id)
    
    # 获取文档的文本块数量
    chunks = crud.get_document_chunks(db, doc.id)
    
    return {
        "id": doc.id,
        "originalName": doc.original_name,
        "fileName": doc.file_name,
        "mimeType": doc.mime_type,
        "size": doc.size,
        "uploadDate": doc.upload_date,
        "previewText": doc.preview_text,
        "messageCount": len(messages),
        "chunkCount": len(chunks)
    }

# 删除文档
def delete_document(db: Session, document_id: str) -> bool:
    doc = crud.get_document(db, document_id)
    if not doc:
        return False
    
    # 删除文件
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception as e:
        print(f"删除文件时出错: {str(e)}")
    
    # 从数据库中删除文档（级联删除会自动删除相关的文本块、嵌入和消息）
    return crud.delete_document(db, document_id)