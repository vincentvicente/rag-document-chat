from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import shutil
from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.document_service import (
    process_document,
    get_all_documents,
    get_document_by_id,
    delete_document
)

router = APIRouter()

# 上传文档
@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    document: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 验证文件类型
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if document.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持PDF和DOCX文件")
    
    # 验证文件大小
    # FastAPI会将文件缓存到内存，所以我们可以检查文件大小
    file_size = 0
    while True:
        chunk = await document.read(1024)
        if not chunk:
            break
        file_size += len(chunk)
        if file_size > 10 * 1024 * 1024:  # 10MB限制
            raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
    
    # 重置文件指针
    await document.seek(0)
    
    # 保存文件
    file_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file_id}_{document.filename}"
    file_path = os.path.join("uploads", filename)
    
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(document.file, buffer)
    
    # 后台处理文档
    file_info = {
        "id": file_id,
        "original_name": document.filename,
        "file_name": filename,
        "file_path": file_path,
        "mime_type": document.content_type,
        "size": file_size,
        "upload_date": datetime.now().isoformat()
    }
    
    try:
        # 同步处理文档，因为我们需要返回处理结果
        result = process_document(db, file_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取所有文档
@router.get("/")
async def get_documents(db: Session = Depends(get_db)):
    try:
        documents = get_all_documents(db)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取单个文档
@router.get("/{document_id}")
async def get_document(document_id: str, db: Session = Depends(get_db)):
    document = get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档未找到")
    return document

# 删除文档
@router.delete("/{document_id}")
async def remove_document(document_id: str, db: Session = Depends(get_db)):
    success = delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档未找到")
    return {"message": "文档删除成功"}