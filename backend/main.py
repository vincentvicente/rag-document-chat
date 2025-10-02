from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# 导入API路由
from app.api import documents, queries

# 导入数据库模型
from app.models.database import engine, Base, get_db
from app.models import models

# 加载环境变量
load_dotenv()

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="RAG API",
    description="文档问答系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
os.makedirs("uploads", exist_ok=True)

# 挂载静态文件
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 注册API路由
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(queries.router, prefix="/api/query", tags=["queries"])

@app.get("/")
async def root():
    return {"message": "Welcome to RAG API"}

@app.get("/db-test")
async def db_test(db: Session = Depends(get_db)):
    """测试数据库连接"""
    try:
        # 尝试查询文档表
        docs = db.query(models.Document).limit(5).all()
        return {"status": "success", "message": "数据库连接正常", "documents_count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库连接错误: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)