#!/bin/bash

echo "🚀 Starting RAG backend service..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found, please run ./setup.sh first"
    exit 1
fi

# Check if dependencies are installed
python -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not installed correctly, please run ./setup.sh first"
    exit 1
fi

# Start service
echo "🌟 Starting service at http://localhost:3000..."
python main.py
