#!/bin/bash

# Checkpoint Clothing Co - Local Development Setup

echo "🎮 Checkpoint Clothing Co - Development Server"
echo "================================================"
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
    echo ""
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🚀 Starting development server..."
echo ""
echo "📍 Main Store:    http://localhost:5000"
echo "📍 Admin Panel:   http://localhost:5000/admin/dashboard"
echo "📍 API Endpoint:  http://localhost:5000/api/designs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 app.py
