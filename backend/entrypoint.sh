#!/bin/bash
set -e

echo "🚀 Starting PromptShield Enterprise Backend..."

# Wait for DB to be ready (simple sleep for now)
# In production, use wait-for-it.sh or pg_isready
echo "⏳ Waiting for Database..."
sleep 5
python backend/fix_db.py

# Run migrations
echo "🔄 Running Database Migrations..."
# Ensure we are in the directory containing alembic.ini or point to it
# alembic.ini is in root
# cd /app (Removed for Render Native compatibility)
alembic upgrade head

# Start server
echo "✅ Starting Uvicorn Server..."
# Use PORT env var if available (Render/Heroku), else 8003
PORT="${PORT:-8003}"
uvicorn backend.app:app --host 0.0.0.0 --port "$PORT"
