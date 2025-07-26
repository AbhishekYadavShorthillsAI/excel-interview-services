#!/bin/bash

# Google Cloud Setup Script for AI Interview Services
# This script automates the initial Google Cloud setup

set -e

echo "🚀 Setting up Google Cloud for AI Interview Services"
echo "====================================================="

# Check if user provided project ID
PROJECT_ID=${1:-""}
if [ -z "$PROJECT_ID" ]; then
    echo "Please provide a project ID:"
    echo "Usage: ./setup-gcloud.sh YOUR_PROJECT_ID"
    echo ""
    echo "Example: ./setup-gcloud.sh ai-interview-demo-123"
    echo ""
    echo "💡 Tip: Project IDs must be globally unique. Try adding numbers or your initials."
    exit 1
fi

echo "🔧 Project ID: $PROJECT_ID"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found!"
    echo ""
    echo "Please install it first:"
    echo "macOS: brew install --cask google-cloud-sdk"
    echo "Windows/Linux: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ Google Cloud CLI found"

# Step 1: Authenticate
echo ""
echo "🔐 Step 1: Authenticating with Google Cloud..."
echo "A browser window will open for authentication."
read -p "Press Enter to continue..."

gcloud auth login

if [ $? -ne 0 ]; then
    echo "❌ Authentication failed. Please try again."
    exit 1
fi

echo "✅ Authentication successful"

# Step 2: Create project
echo ""
echo "🏗️  Step 2: Creating Google Cloud project..."

gcloud projects create $PROJECT_ID --name="AI Interview Services" || {
    echo "⚠️  Project creation failed. It might already exist or name is taken."
    echo "Continuing with existing project..."
}

echo "✅ Project ready: $PROJECT_ID"

# Step 3: Set active project
echo ""
echo "⚙️  Step 3: Setting active project..."
gcloud config set project $PROJECT_ID

echo "✅ Active project set"

# Step 4: Enable billing (this needs to be done manually)
echo ""
echo "💳 Step 4: Enable billing (MANUAL STEP REQUIRED)"
echo "========================================"
echo "You need to enable billing for your project:"
echo ""
echo "1. Go to: https://console.cloud.google.com/billing"
echo "2. Link your billing account to project: $PROJECT_ID"
echo "3. This is required for Cloud Run to work"
echo ""
read -p "Press Enter after you've enabled billing..."

# Step 5: Enable required APIs
echo ""
echo "🔌 Step 5: Enabling required APIs..."
echo "This may take a few minutes..."

gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com  
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

echo "✅ All APIs enabled"

# Step 6: Verify setup
echo ""
echo "🔍 Step 6: Verifying setup..."

# Check current configuration
echo ""
echo "Current configuration:"
gcloud config list

echo ""
echo "🎉 Google Cloud setup complete!"
echo "==============================="
echo ""
echo "✅ Project created: $PROJECT_ID"
echo "✅ APIs enabled"
echo "✅ Ready for deployment"
echo ""
echo "🔑 Next steps:"
echo "1. Get your API keys:"
echo "   • MongoDB URI: https://cloud.mongodb.com/"
echo "   • Gemini API: https://makersuite.google.com/app/apikey"
echo "   • Perplexity API (optional): https://www.perplexity.ai/settings/api"
echo ""
echo "2. Deploy your services:"
echo "   ./deploy.sh $PROJECT_ID us-central1 \"mongodb-uri\" \"gemini-key\" \"perplexity-key\""
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions!"

echo ""
echo "💡 Save this command for deployment:"
echo "======================================"
echo "./deploy.sh $PROJECT_ID us-central1 \"YOUR_MONGODB_URI\" \"YOUR_GEMINI_KEY\" \"YOUR_PERPLEXITY_KEY\""
echo "" 