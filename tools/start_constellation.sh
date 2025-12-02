#!/bin/bash

# Start constellation development environment
echo "🌟 Starting CogOS Constellation Development Environment..."

# Check if we're in the right directory
if [ ! -f "Plan.md" ]; then
    echo "❌ Please run this script from the CogOS project root directory"
    exit 1
fi

# Install backend dependencies if needed
echo "📦 Checking backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start backend server in background
echo "🚀 Starting backend API server..."
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Return to project root
cd ..

# Install frontend dependencies if needed
echo "📦 Checking frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install --legacy-peer-deps
fi

# Build and start frontend
echo "🚀 Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

# Return to project root
cd ..

echo ""
echo "🌟 CogOS Constellation Environment Started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🖥️  Frontend:  http://localhost:3000"
echo "🔧 Backend:   http://localhost:8000"
echo "📊 API Docs:  http://localhost:8000/docs"
echo "🎯 Constellation: http://localhost:3000/constellation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ Features enabled:"
echo "   • 3D Knowledge Constellation Visualization"
echo "   • Real-time Performance Monitoring"
echo "   • Physics-based Node Positioning"
echo "   • Domain Clustering"
echo "   • Advanced Navigation Controls"
echo "   • Real-time Data Updates"
echo ""
echo "🎯 Performance Targets:"
echo "   • <50ms API Response Time"
echo "   • 60fps 3D Rendering"
echo "   • <1MB Frontend Bundle"
echo "   • <200MB Memory Usage"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# Keep script running
while true; do
    sleep 1
done
