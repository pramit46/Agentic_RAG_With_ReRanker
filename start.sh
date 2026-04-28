#!/bin/bash

# Quick Start Script for Agentic RAG Application
# This script activates the virtual environment and runs the application

echo "════════════════════════════════════════════════════════════════"
echo "  🤖 AGENTIC RAG WITH HITL RE-RANKING 🤖"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Starting application..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Copying from .env.example..."
    cp .env.example .env
    echo "✓ Please edit .env and add your OPENAI_API_KEY"
    echo ""
fi

# Activate virtual environment and run
source venv/bin/activate
python main.py
deactivate
