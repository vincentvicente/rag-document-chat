#!/bin/bash

echo "🚀 Python 项目环境设置脚本"
echo "=========================="

# 检查 Python 版本
echo "📋 检查 Python 版本..."
python --version

# 删除旧的虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "🗑️  删除旧的虚拟环境..."
    rm -rf venv
fi

# 创建新的虚拟环境
echo "📦 创建虚拟环境..."
python -m venv venv

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖（分批安装，避免编译问题）
echo "📚 安装核心依赖..."
pip install fastapi uvicorn python-multipart pydantic python-dotenv sqlalchemy alembic

echo "📄 安装文档处理依赖..."
pip install PyPDF2 python-docx

echo "🤖 安装 AI 相关依赖..."
pip install google-generativeai langchain langchain-community

echo "🔢 安装数学计算依赖（可能需要较长时间）..."
pip install numpy scikit-learn

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p uploads

# 初始化数据库
echo "🗄️  初始化数据库..."
python -c "
try:
    from app.models.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print('✅ 数据库初始化成功！')
except Exception as e:
    print(f'❌ 数据库初始化失败: {e}')
"

echo ""
echo "🎉 环境设置完成！"
echo ""
echo "使用以下命令启动项目："
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "或者直接运行："
echo "  ./run.sh"
