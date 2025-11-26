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

# Load environment variables
load_dotenv()

# Split text into chunks and generate embeddings
def process_and_store_embeddings(db: Session, document_id: str, text: str) -> Dict[str, Any]:
    try:
        # Split text into chunks - using AI Buddy project method
        # First split by pages (assuming triple newlines indicate page separation)
        pages = text.split('\n\n\n')
        pages = [page for page in pages if page.strip()]
        chunks = []
        
        # Split each page into upper and lower halves
        for page in pages:
            if not page.strip():
                continue
            
            # Split page into upper and lower halves
            mid_point = len(page) // 2
            upper_half = page[:mid_point].strip()
            lower_half = page[mid_point:].strip()
            
            if upper_half:
                chunks.append(upper_half)
            if lower_half:
                chunks.append(lower_half)
        
        # If too few chunks after splitting, use original chunking method
        if len(chunks) < 5:
            print("Page chunking produced too few chunks, using original chunking method")
            original_chunks = split_text(text)
            chunks.extend(original_chunks)
        
        print(f"Document split into {len(chunks)} text chunks")
        
        # Batch process embeddings - inspired by AI Buddy project batch processing
        batch_size = 100  # Consistent with AI Buddy project
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + min(batch_size, len(chunks) - i)]
            print(f"Processing batch {i//batch_size + 1} / {(len(chunks) + batch_size - 1)//batch_size}")
            
            # Generate embeddings for each chunk in the batch and store to database
            for j, chunk_text in enumerate(batch):
                # Create text chunk
                chunk = schemas.TextChunkCreate(
                    document_id=document_id,
                    text=chunk_text,
                    chunk_index=i + j
                )
                db_chunk = crud.create_text_chunk(db, chunk)
                
                # Generate embedding vector
                embedding_vector = generate_embedding(chunk_text)
                
                # Store embedding vector
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
        print(f"Error processing embeddings: {str(e)}")
        raise Exception(f"Failed to process embeddings: {str(e)}")

# Generate embedding vector for text
def generate_embedding(text: str) -> List[float]:
    try:
        # Read API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        
        # If key is available, use Gemini API
        if api_key:
            try:
                import google.generativeai as genai
                
                # Configure API key
                genai.configure(api_key=api_key)
                
                # Use Gemini's embedding model
                embedding_model = 'models/embedding-001'
                
                # Generate embedding
                result = genai.embed_content(
                    model=embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
                
                # Return embedding vector
                return result["embedding"]
                
            except Exception as api_error:
                print(f"Gemini API embedding generation failed, using mock embedding: {str(api_error)}")
        else:
            print("Warning: GEMINI_API_KEY is not set, using mock embedding")
        
        # Mock embedding vector (if API call failed or no API key)
        return np.random.normal(0, 0.1, 384).tolist()
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        raise e

# Search for similar text chunks
def search_similar_chunks(db: Session, document_id: str, query: str, limit: int = 4) -> List[Dict[str, Any]]:
    try:
        if not document_id:
            # If no document ID specified, search all documents
            return search_all_documents(db, query, limit)
        
        # Get all embeddings for the document
        embeddings = crud.get_document_embeddings(db, document_id)
        
        if not embeddings:
            raise Exception(f"Embeddings not found for document ID: {document_id}")
        
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Calculate similarity using Euclidean distance - inspired by AI Buddy project
        results = []
        for item in embeddings:
            distance = calculate_euclidean_distance(query_embedding, item["vector"])
            results.append({
                **item,
                "distance": distance,
                "score": 0  # Will be calculated later
            })
        
        # Sort by distance (smaller distance means more similar)
        results.sort(key=lambda x: x["distance"])
        results = results[:limit]
        
        # Convert distance to score (1 - normalized distance)
        max_distance = max(result["distance"] for result in results) if results else 1
        for item in results:
            item["score"] = 1 - (item["distance"] / max_distance)
        
        return [{
            "text": item["text"],
            "score": item["score"],
            "distance": item["distance"]
        } for item in results]
    except Exception as e:
        print(f"Error searching similar chunks: {str(e)}")
        raise e

# Calculate Euclidean distance - inspired by AI Buddy project
def calculate_euclidean_distance(vec_a: List[float], vec_b: List[float]) -> float:
    if len(vec_a) != len(vec_b):
        raise ValueError("Vector dimensions must be the same")
    
    return np.sqrt(np.sum(np.square(np.array(vec_a) - np.array(vec_b))))

# Search all documents
def search_all_documents(db: Session, query: str, limit: int) -> List[Dict[str, Any]]:
    # Get all documents
    documents = crud.get_all_documents(db)
    
    all_results = []
    for document in documents:
        try:
            # Search similar chunks in each document
            similar_chunks = search_similar_chunks(db, document.id, query, limit=2)  # Take 2 most similar chunks per document
            
            # Add document ID
            for chunk in similar_chunks:
                chunk["document_id"] = document.id
            
            all_results.extend(similar_chunks)
        except Exception as e:
            print(f"Error searching document {document.id}: {str(e)}")
    
    # Sort by similarity
    all_results.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top limit results
    return all_results[:limit]

# Delete document embeddings
def delete_embeddings(db: Session, document_id: str) -> bool:
    # Get all text chunks for the document
    chunks = crud.get_document_chunks(db, document_id)
    
    # Delete embeddings for each text chunk (handled automatically by cascade delete)
    # Delete all text chunks (embeddings handled automatically by cascade delete)
    return crud.delete_document_chunks(db, document_id) > 0