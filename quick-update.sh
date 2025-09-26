#!/bin/bash

echo "🚀 Quick update for Address Analyzing Tool..."

if [ ! -f "main.py" ]; then
    echo "❌ Error: Run from project directory"
    exit 1
fi

if [ -f ".env" ]; then
    cp ".env" ".env.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✓ .env backup created"
fi

echo "🔄 Getting changes from GitHub..."
git pull origin main

if [ -f ".env.backup."* ]; then
    latest_backup=$(ls -t .env.backup.* | head -1)
    cp "$latest_backup" ".env"
    echo "✓ .env restored"
fi

if git diff HEAD~1 --name-only | grep -q "requirements.txt"; then
    echo "🔄 Updating dependencies..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    pip install -r requirements.txt --upgrade
    echo "✓ Dependencies updated"
fi

echo "✅ Quick update completed"
echo "📝 For complete updates use: ./update.sh"

