#!/bin/bash

# CogOS - Unified Startup Script

echo "🧠 Starting CogOS - Personal Cognitive Operating System"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
if [ ! -f ".venv/lib/python*/site-packages/fastapi" ]; then
    echo "📦 Installing dependencies..."
    pip install -r app/api/requirements.txt
fi

# Start the API server
echo "🚀 Starting CogOS API server on http://localhost:8000"
cd app && python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000 &

# Wait for server to start
sleep 3

# Open constellation in browser (optional)
if command -v open &> /dev/null; then
    echo "🌌 Opening constellation visualization..."
    open "http://localhost:8000/static/constellation.html"
fi

echo "✅ CogOS is running!"
echo "   - API: http://localhost:8000"
echo "   - Constellation: http://localhost:8000/static/constellation.html"
echo "   - Docs: http://localhost:8000/docs"

wait
