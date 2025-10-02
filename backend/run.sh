#!/bin/bash

echo "🚀 启动 RAG 后端服务..."

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 未找到虚拟环境，请先运行 ./setup.sh"
    exit 1
fi

# 检查依赖是否安装
python -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 依赖未正确安装，请先运行 ./setup.sh"
    exit 1
fi

# 启动服务
echo "🌟 在 http://localhost:3000 启动服务..."
python main.py
