#!/bin/bash
set -e

echo "🔨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Frontend build complete"
echo "📦 Installing Python dependencies..."
pip install -r render_requirements.txt

echo "✅ Build complete"