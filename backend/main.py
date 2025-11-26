from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Import API routes
from app.api import documents, queries

# Import database models
from app.models.database import engine, Base, get_db
from app.models import models

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="RAG API",
    description="Document Q&A System API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be restricted to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register API routes
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(queries.router, prefix="/api/query", tags=["queries"])

@app.get("/")
async def root():
    return {"message": "Welcome to RAG API"}

@app.get("/db-test")
async def db_test(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # 尝试查询文档表
        docs = db.query(models.Document).limit(5).all()
        return {"status": "success", "message": "数据库连接正常", "documents_count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库连接错误: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)