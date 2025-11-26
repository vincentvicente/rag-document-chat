#!/bin/bash

echo "🚀 Python Project Environment Setup Script"
echo "=========================="

# Check Python version
echo "📋 Checking Python version..."
python --version

# Remove old virtual environment (if exists)
if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies (batch installation to avoid compilation issues)
echo "📚 Installing core dependencies..."
pip install fastapi uvicorn python-multipart pydantic python-dotenv sqlalchemy alembic

echo "📄 Installing document processing dependencies..."
pip install PyPDF2 python-docx

echo "🤖 Installing AI-related dependencies..."
pip install google-generativeai langchain langchain-community

echo "🔢 Installing math computation dependencies (may take some time)..."
pip install numpy scikit-learn

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads

# Initialize database
echo "🗄️  Initializing database..."
python -c "
try:
    from app.models.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print('✅ Database initialized successfully!')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
"

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "Use the following command to start the project:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or run directly:"
echo "  ./run.sh"
