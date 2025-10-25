#!/bin/bash
# Quick start script for Me-Trade

echo "🚀 Me-Trade Quick Start"
echo "======================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate virtual environment
echo ""
echo "📥 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo ""
echo "💾 Initializing database..."
python -c "from src.db import get_db; db = get_db(); print('✓ Database initialized')"

# Launch app
echo ""
echo "🎉 Setup complete!"
echo ""
echo "🌐 Launching Streamlit app..."
echo ""
streamlit run app.py
