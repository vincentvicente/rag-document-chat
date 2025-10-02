"""
数据库功能测试脚本
"""
import os
import sys
from sqlalchemy.orm import Session

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import get_db, engine, Base
from app.models import models, crud, schemas

def setup_db():
    """初始化数据库"""
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

def test_document_crud():
    """测试文档CRUD操作"""
    print("\n测试文档CRUD操作...")
    
    # 获取数据库会话
    db = next(get_db())
    
    # 创建测试文档
    doc = schemas.DocumentCreate(
        original_name="test_document.pdf",
        file_name="test_document.pdf",
        file_path="test_path",
        mime_type="application/pdf",
        size=1024,
        preview_text="This is a test document"
    )
    
    # 添加文档
    db_doc = crud.create_document(db, doc)
    print(f"创建文档: {db_doc.id}, {db_doc.original_name}")
    
    # 获取文档
    retrieved_doc = crud.get_document(db, db_doc.id)
    print(f"获取文档: {retrieved_doc.id}, {retrieved_doc.original_name}")
    
    # 获取所有文档
    all_docs = crud.get_all_documents(db)
    print(f"获取所有文档: {len(all_docs)} 个文档")
    
    # 删除文档
    deleted = crud.delete_document(db, db_doc.id)
    print(f"删除文档: {'成功' if deleted else '失败'}")
    
    # 验证删除
    deleted_doc = crud.get_document(db, db_doc.id)
    print(f"验证删除: {'文档已删除' if deleted_doc is None else '文档仍存在'}")

def test_text_chunk_and_embedding():
    """测试文本块和嵌入向量操作"""
    print("\n测试文本块和嵌入向量操作...")
    
    # 获取数据库会话
    db = next(get_db())
    
    # 创建测试文档
    doc = schemas.DocumentCreate(
        original_name="test_document.pdf",
        file_name="test_document.pdf",
        file_path="test_path",
        mime_type="application/pdf",
        size=1024,
        preview_text="This is a test document"
    )
    db_doc = crud.create_document(db, doc)
    print(f"创建文档: {db_doc.id}")
    
    # 创建文本块
    chunk = schemas.TextChunkCreate(
        document_id=db_doc.id,
        text="This is a test chunk",
        chunk_index=0
    )
    db_chunk = crud.create_text_chunk(db, chunk)
    print(f"创建文本块: {db_chunk.id}")
    
    # 创建嵌入向量
    embedding = schemas.EmbeddingCreate(
        chunk_id=db_chunk.id,
        vector=[0.1, 0.2, 0.3, 0.4, 0.5]
    )
    db_embedding = crud.create_embedding(db, embedding)
    print(f"创建嵌入向量: {db_embedding.id}")
    
    # 获取文档的嵌入向量
    doc_embeddings = crud.get_document_embeddings(db, db_doc.id)
    print(f"获取文档嵌入向量: {len(doc_embeddings)} 个向量")
    print(f"向量示例: {doc_embeddings[0]['vector'][:5]}...")
    
    # 删除文档（级联删除文本块和嵌入向量）
    deleted = crud.delete_document(db, db_doc.id)
    print(f"删除文档及相关数据: {'成功' if deleted else '失败'}")

def test_message_and_query_history():
    """测试消息和查询历史操作"""
    print("\n测试消息和查询历史操作...")
    
    # 获取数据库会话
    db = next(get_db())
    
    # 创建测试文档
    doc = schemas.DocumentCreate(
        original_name="test_document.pdf",
        file_name="test_document.pdf",
        file_path="test_path",
        mime_type="application/pdf",
        size=1024,
        preview_text="This is a test document"
    )
    db_doc = crud.create_document(db, doc)
    print(f"创建文档: {db_doc.id}")
    
    # 创建用户消息
    user_message = schemas.MessageCreate(
        document_id=db_doc.id,
        content="This is a test question",
        role="user"
    )
    db_user_message = crud.create_message(db, user_message)
    print(f"创建用户消息: {db_user_message.id}")
    
    # 创建助手消息
    assistant_message = schemas.MessageCreate(
        document_id=db_doc.id,
        content="This is a test answer",
        role="assistant",
        sources=[{"text": "Source text", "score": 0.95}]
    )
    db_assistant_message = crud.create_message(db, assistant_message)
    print(f"创建助手消息: {db_assistant_message.id}")
    
    # 获取文档消息
    messages = crud.get_document_messages(db, db_doc.id)
    print(f"获取文档消息: {len(messages)} 条消息")
    
    # 创建查询历史
    history = crud.create_query_history(
        db,
        db_doc.id,
        "Test query",
        "Test answer",
        [{"text": "Source text", "score": 0.95}]
    )
    print(f"创建查询历史: {history.id}")
    
    # 获取查询历史
    histories = crud.get_query_history(db)
    print(f"获取查询历史: {len(histories)} 条记录")
    
    # 删除文档（级联删除消息）
    deleted = crud.delete_document(db, db_doc.id)
    print(f"删除文档及相关消息: {'成功' if deleted else '失败'}")

def run_tests():
    """运行所有测试"""
    setup_db()
    test_document_crud()
    test_text_chunk_and_embedding()
    test_message_and_query_history()
    print("\n所有测试完成!")

if __name__ == "__main__":
    run_tests()

