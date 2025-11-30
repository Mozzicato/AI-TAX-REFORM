#!/bin/bash

# 🚀 Quick Deploy NTRIA to Hugging Face Spaces
# This script automates the deployment process

set -e  # Exit on error

echo "🇳🇬 NTRIA - Hugging Face Spaces Deployment Setup"
echo "=================================================="
echo ""

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v git &> /dev/null; then
        echo "❌ Git is not installed. Please install Git first."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
    echo ""
}

# Get user inputs
get_user_inputs() {
    echo "🔐 Hugging Face Configuration"
    echo "----------------------------"
    
    read -p "Enter your HF username: " HF_USERNAME
    read -p "Enter your Space name (e.g., TAXBOT): " SPACE_NAME
    read -sp "Paste your HF token here (won't be displayed): " HF_TOKEN
    echo ""
    echo ""
    
    # Validate inputs
    if [ -z "$HF_USERNAME" ] || [ -z "$SPACE_NAME" ] || [ -z "$HF_TOKEN" ]; then
        echo "❌ Please provide all required information"
        exit 1
    fi
}

# Clone Space repository
clone_space() {
    echo "📥 Cloning Space repository..."
    
    HF_URL="https://${HF_USERNAME}:${HF_TOKEN}@huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"
    
    if [ -d "$SPACE_NAME" ]; then
        echo "⚠️  Directory $SPACE_NAME already exists. Updating instead..."
        cd "$SPACE_NAME"
        git pull
    else
        git clone "$HF_URL" "$SPACE_NAME"
        cd "$SPACE_NAME"
    fi
    
    echo "✅ Repository cloned/updated"
    echo ""
}

# Copy files
copy_files() {
    echo "📂 Copying files from AI-TAX-REFORM..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    cp "$SCRIPT_DIR/app.py" .
    cp "$SCRIPT_DIR/requirements.txt" .
    cp "$SCRIPT_DIR/README.md" .
    cp "$SCRIPT_DIR/packages.txt" .
    
    echo "✅ Files copied"
    echo ""
}

# Create .env file
setup_env() {
    echo "⚙️  Setting up environment..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# NTRIA Gradio App - Environment Configuration
# Backend API URL - Update this to your deployed backend
BACKEND_API_URL=http://localhost:8000
API_TIMEOUT=30
EOF
        echo "📝 Created .env file (update BACKEND_API_URL if needed)"
    else
        echo "📝 .env file already exists"
    fi
    
    echo ""
}

# Commit and push
commit_and_push() {
    echo "🚀 Committing and pushing to Hugging Face Spaces..."
    
    git add .
    git commit -m "Deploy NTRIA Gradio interface with Graph RAG backend" || echo "ℹ️  No changes to commit"
    git push
    
    echo "✅ Pushed to Hugging Face Spaces"
    echo ""
}

# Success message
success_message() {
    echo "🎉 Deployment Complete!"
    echo "========================"
    echo ""
    echo "Your Space is now live at:"
    echo "🔗 https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Visit the Space link above"
    echo "   2. Check the 'Logs' tab to see build progress"
    echo "   3. Update .env with your backend API URL if using a remote backend"
    echo "   4. Push changes: git add . && git commit -m 'Update config' && git push"
    echo ""
    echo "📚 For more info, see HF_SPACES_DEPLOYMENT.md"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    get_user_inputs
    clone_space
    copy_files
    setup_env
    commit_and_push
    success_message
}

main
