#!/bin/bash

# 🚀 Quick Deploy NTRIA Backend to Railway
# This script automates the deployment process

set -e

echo "🇳🇬 NTRIA Backend - Railway Deployment"
echo "========================================"
echo ""

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v git &> /dev/null; then
        echo "❌ Git is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "⚠️  Docker not found (optional for local testing)"
    else
        echo "✅ Docker found"
    fi
    
    echo "✅ Prerequisites OK"
    echo ""
}

# Build and test locally
test_locally() {
    read -p "Test Docker build locally? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🐳 Building Docker image..."
        docker build -f backend/Dockerfile -t ntria-backend:latest .
        
        echo "✅ Docker build successful"
        echo "🧪 To test locally, run:"
        echo "   docker run -p 8000:8000 -e NEO4J_URI=bolt://localhost:7687 ntria-backend:latest"
        echo ""
    fi
}

# Push to GitHub
push_to_github() {
    echo "📤 Pushing to GitHub..."
    
    git add .
    git commit -m "🚀 Docker setup for Railway deployment" || echo "ℹ️  No changes to commit"
    git push origin main
    
    echo "✅ Pushed to GitHub"
    echo ""
}

# Instructions for Railway
railway_instructions() {
    echo "🚂 Railway Deployment Instructions"
    echo "===================================="
    echo ""
    echo "1. Go to: https://railway.app/dashboard"
    echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
    echo "3. Select: Mozzicato/AI-TAX-REFORM"
    echo "4. Railway will auto-detect the Dockerfile"
    echo ""
    echo "5. Add Environment Variables in Railway:"
    echo "   ✓ NEO4J_URI"
    echo "   ✓ OPENAI_API_KEY"
    echo "   ✓ Graph DB configured (JSON-based)"
    echo "   ✓ ALLOWED_ORIGINS"
    echo ""
    echo "6. Click 'Deploy' and wait for completion"
    echo "7. Copy your public URL from Railway dashboard"
    echo ""
    echo "📚 Full guide: See RAILWAY_DEPLOYMENT.md"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    test_locally
    push_to_github
    railway_instructions
    
    echo "✨ Setup complete!"
    echo "Next: Go to Railway and deploy!"
}

main
