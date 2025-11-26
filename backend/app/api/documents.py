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

# Upload document
@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    document: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if document.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    # Validate file size
    # FastAPI caches files to memory, so we can check file size
    file_size = 0
    while True:
        chunk = await document.read(1024)
        if not chunk:
            break
        file_size += len(chunk)
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size cannot exceed 10MB")
    
    # Reset file pointer
    await document.seek(0)
    
    # Save file
    file_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file_id}_{document.filename}"
    file_path = os.path.join("uploads", filename)
    
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(document.file, buffer)
    
    # Process document in background
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
        # Process document synchronously because we need to return processing results
        result = process_document(db, file_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all documents
@router.get("/")
async def get_documents(db: Session = Depends(get_db)):
    try:
        documents = get_all_documents(db)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get single document
@router.get("/{document_id}")
async def get_document(document_id: str, db: Session = Depends(get_db)):
    document = get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

# Delete document
@router.delete("/{document_id}")
async def remove_document(document_id: str, db: Session = Depends(get_db)):
    success = delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}