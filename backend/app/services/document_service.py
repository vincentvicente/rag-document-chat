import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil
from sqlalchemy.orm import Session

from app.utils.file_parser import parse_file
from app.services.embedding_service import process_and_store_embeddings
from app.models import crud, schemas

# Process uploaded document
def process_document(db: Session, file_info: Dict[str, Any]) -> Dict[str, Any]:
    try:
        file_path = file_info["file_path"]
        file_extension = os.path.splitext(file_info["original_name"])[1].lower()
        
        # Parse document content
        text = parse_file(file_path, file_extension)
        
        # Create document record, add preview text
        preview_text = text[:200] + "..." if len(text) > 200 else text
        
        # Store document to database
        document = schemas.DocumentCreate(
            original_name=file_info["original_name"],
            file_name=file_info["file_name"],
            file_path=file_info["file_path"],
            mime_type=file_info["mime_type"],
            size=file_info["size"],
            preview_text=preview_text
        )
        
        db_document = crud.create_document(db, document)
        
        print(f"Starting to process document: {db_document.original_name}")
        
        # Generate embeddings and store
        embedding_result = process_and_store_embeddings(db, db_document.id, text)
        print(f"Document processing completed: {embedding_result['chunk_count']} text chunks processed")
        
        return {
            "id": db_document.id,
            "originalName": db_document.original_name,
            "uploadDate": db_document.upload_date,
            "previewText": db_document.preview_text,
            "chunkCount": embedding_result["chunk_count"]
        }
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        # If file exists, try to delete it
        if os.path.exists(file_info["file_path"]):
            try:
                os.remove(file_info["file_path"])
            except Exception as del_e:
                print(f"Error deleting file: {str(del_e)}")
        raise Exception(f"Failed to process document: {str(e)}")

# Get all documents
def get_all_documents(db: Session) -> List[Dict[str, Any]]:
    documents = crud.get_all_documents(db)
    
    result = []
    for doc in documents:
        # Get message count for document
        messages = crud.get_document_messages(db, doc.id)
        
        result.append({
            "id": doc.id,
            "originalName": doc.original_name,
            "uploadDate": doc.upload_date,
            "previewText": doc.preview_text,
            "messageCount": len(messages)
        })
    
    return result

# Get document by ID
def get_document_by_id(db: Session, document_id: str) -> Optional[Dict[str, Any]]:
    doc = crud.get_document(db, document_id)
    if not doc:
        return None
    
    # Get message count for document
    messages = crud.get_document_messages(db, doc.id)
    
    # Get text chunk count for document
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

# Delete document
def delete_document(db: Session, document_id: str) -> bool:
    doc = crud.get_document(db, document_id)
    if not doc:
        return False
    
    # Delete file
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
    
    # Delete document from database (cascade delete will automatically delete related text chunks, embeddings, and messages)
    return crud.delete_document(db, document_id)