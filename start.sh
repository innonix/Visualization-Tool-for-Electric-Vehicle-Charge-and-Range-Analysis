#!/bin/bash

# EV Analytics Dashboard Startup Script
# =====================================

echo "🚗 EV Analytics Dashboard"
echo "========================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q

# Check for Gemini API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "⚠️  Note: GEMINI_API_KEY not set. AI insights will be disabled."
    echo "   Set it with: export GEMINI_API_KEY='your_api_key'"
    echo "   Or enter it in the app's sidebar."
    echo ""
fi

# Start the app
echo "🚀 Starting EV Analytics Dashboard..."
echo "   Open your browser at: http://localhost:8501"
echo ""
streamlit run app.py
