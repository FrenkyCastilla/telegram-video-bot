#!/bin/bash

# Telegram Video Bot - Quick Start Script

set -e

echo "🤖 Telegram Video Bot - Quick Start"
echo "===================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your tokens:"
    echo "   nano .env"
    echo ""
    echo "Required variables:"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - FIREWORKS_API_KEY"
    echo "  - OPENAI_API_KEY"
    exit 1
fi

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected. Starting with Docker..."
    docker-compose up -d
    echo "✅ Bot started in Docker container"
    echo "📋 View logs: docker-compose logs -f"
    echo "🛑 Stop bot: docker-compose down"
else
    echo "🐍 Docker not found. Starting with Python..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
    
    # Check if ffmpeg is available
    if ! command -v ffmpeg &> /dev/null; then
        echo "⚠️  Warning: ffmpeg not found. Video conversion may not work."
        echo "   Install: sudo apt-get install ffmpeg (Ubuntu/Debian)"
        echo "           brew install ffmpeg (macOS)"
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -q -r requirements.txt
    
    # Create temp directory
    mkdir -p temp
    
    # Run bot
    echo "🚀 Starting bot..."
    python main.py
fi
