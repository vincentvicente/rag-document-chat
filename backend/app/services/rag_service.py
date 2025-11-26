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
    print("Warning: GEMINI_API_KEY is not set in .env file.")
else:
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Failed to configure Gemini API key: {e}")

# Process query
def process_query(db: Session, document_id: str, query: str) -> Dict[str, Any]:
    try:
        # If no document ID provided, use direct chat mode (without RAG)
        if not document_id:
            try:
                # Direct chat with Gemini (without RAG)
                answer = generate_answer_without_context(query)
                return {
                    "answer": answer,
                    "sources": []
                }
            except Exception as e:
                print(f"Gemini API call failed: {str(e)}")
                return {
                    "answer": "Sorry, I'm unable to answer your question right now. Please try again later.",
                    "sources": []
                }
        
        # Search for relevant text chunks
        similar_chunks = search_similar_chunks(db, document_id, query)
        
        if not similar_chunks:
            no_info_answer = "I couldn't find information related to your question."
            
            # If document ID exists, add message to database
            if document_id:
                message = schemas.MessageCreate(
                    document_id=document_id,
                    content=query,
                    role="user"
                )
                crud.create_message(db, message)
                
                # Add assistant message
                assistant_message = schemas.MessageCreate(
                    document_id=document_id,
                    content=no_info_answer,
                    role="assistant",
                    sources=[]
                )
                crud.create_message(db, assistant_message)
            
            # Record query history
            crud.create_query_history(db, document_id, query, no_info_answer, [])
            
            return {
                "answer": no_info_answer,
                "sources": []
            }
        
        # Build context
        context = "\n\n".join([chunk["text"] for chunk in similar_chunks])
        
        # Try to use LLM to generate answer, fallback to mock answer if failed
        try:
            answer = generate_answer(query, context)
        except Exception as e:
            print(f"LLM API call failed, using mock answer: {str(e)}")
            answer = generate_mock_answer(query, context, similar_chunks)
        
        # If document ID exists, add message to database
        if document_id:
            # Add user message
            user_message = schemas.MessageCreate(
                document_id=document_id,
                content=query,
                role="user"
            )
            crud.create_message(db, user_message)
            
            # Add assistant message
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
        
        # Record query history
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
        print(f"Error processing query: {str(e)}")
        return {
            "answer": f"An error occurred while processing your question. This is a mock answer in test mode. Error: {str(e)}",
            "sources": []
        }

# Generate mock answer (for testing, no API key required)
def generate_mock_answer(query: str, context: str, chunks: List[Dict[str, Any]]) -> str:
    print("Using mock answer mode (for testing)")
    
    # Extract some text from chunks as the basis for the answer
    first_chunk = chunks[0]["text"] if chunks else ""
    second_chunk = chunks[1]["text"] if len(chunks) > 1 else ""
    
    # Generate different mock answers based on query content
    if "what" in query.lower() or "is" in query.lower():
        return f"Based on the document content, this is information about {first_chunk[:30]}. The document mentions: {first_chunk[:100]}..."
    elif "how" in query.lower():
        return f"The document explains this as follows: {first_chunk[:120]}... You can follow these steps."
    elif "why" in query.lower():
        second_part = f"It also mentions: {second_chunk[:50]}..." if second_chunk else ""
        return f"According to the document, the reason is: {first_chunk[:100]}... {second_part}"
    else:
        return f"You asked about \"{query}\". The relevant content in the document is: {first_chunk[:150]}... This is a mock answer in test mode, without actual AI generation."

# Direct chat with Gemini (without context/RAG)
def generate_answer_without_context(query: str) -> str:
    try:
        # Check if API key is configured
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
            
        # Create model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create simple chat prompt
        prompt = f"""You are a helpful AI assistant. Please answer the user's question in a natural and friendly way.

Question: {query}
"""
        
        # Generate answer
        response = model.generate_content(prompt)
        
        # Return generated text
        return response.text
    except Exception as e:
        print(f"Error generating answer without context: {str(e)}")
        raise e

# Use LLM to generate answer (requires API key)
def generate_answer(query: str, context: str) -> str:
    try:
        # Check if API key is configured
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured, cannot call LLM.")
            
        # Create model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create prompt
        prompt_template = """You are a professional document Q&A assistant. Please answer the user's question based on the provided context.
        If there is no relevant information in the context, please state that you cannot answer the question.
        Do not make up information, only use the provided context.
        Try to provide concise and accurate answers.
        
        Context:
        {context}
        
        Question: {query}
        """
        
        prompt = prompt_template.format(context=context, query=query)
        
        # Generate answer
        response = model.generate_content(prompt)
        
        # Return generated text
        return response.text
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        raise e

# Get query history
def get_query_history(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    history_items = crud.get_query_history(db, skip, limit)
    
    return [{
        "id": item.id,
        "document_id": item.document_id,
        "query": item.query,
        "answer": item.answer[:100] + "..." if len(item.answer) > 100 else item.answer,
        "timestamp": item.timestamp
    } for item in history_items]

# Get ChatBot
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

# Get all ChatBots
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