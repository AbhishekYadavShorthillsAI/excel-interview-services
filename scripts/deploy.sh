#!/bin/bash

# Google Cloud Deploy Script for AI Interview & Generator Services  
# Make sure you have gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
MONGODB_URI=${3:-""}
GEMINI_API_KEY=${4:-""}
PERPLEXITY_API_KEY=${5:-""}

echo "🚀 Deploying AI Interview & Generator Services to Google Cloud"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Check if required variables are set
if [ -z "$MONGODB_URI" ] || [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: Missing required environment variables"
    echo "Usage: ./deploy.sh PROJECT_ID REGION MONGODB_URI GEMINI_API_KEY [PERPLEXITY_API_KEY]"
    echo ""
    echo "Example:"
    echo "./deploy.sh my-project us-central1 'mongodb+srv://user:pass@cluster.mongodb.net/interview' 'your-gemini-key' 'your-perplexity-key'"
    echo ""
    echo "Note: PERPLEXITY_API_KEY is optional but recommended for enhanced question generation"
    exit 1
fi

# Set project
echo "🔧 Setting up Google Cloud project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create secrets
echo "🔐 Creating secrets..."
echo -n "$MONGODB_URI" | gcloud secrets create mongodb-uri --data-file=- --replication-policy="automatic" || echo "Secret mongodb-uri already exists"
echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- --replication-policy="automatic" || echo "Secret gemini-api-key already exists"

if [ ! -z "$PERPLEXITY_API_KEY" ]; then
    echo -n "$PERPLEXITY_API_KEY" | gcloud secrets create perplexity-api-key --data-file=- --replication-policy="automatic" || echo "Secret perplexity-api-key already exists"
fi

echo ""
echo "📋 DEPLOYMENT PLAN:"
echo "1. 🏗️  Generator Backend (Question Creation)"
echo "2. 🎨 Generator Frontend (Question Management UI)"  
echo "3. 🤖 Interview Backend (Interview Conductor)"
echo "4. 📊 Interview Frontend (Interview UI)"
echo ""

# ===============================
# DEPLOY GENERATOR SERVICE FIRST
# ===============================

echo "🎯 Step 1: Building Generator Backend..."
gcloud builds submit --config generator/cloudbuild.yaml .

echo "🚀 Deploying Generator Backend to Cloud Run..."
SECRETS_ARG="MONGODB_URI=mongodb-uri:latest,GEMINI_API_KEY=gemini-api-key:latest"
if [ ! -z "$PERPLEXITY_API_KEY" ]; then
    SECRETS_ARG="$SECRETS_ARG,PERPLEXITY_API_KEY=perplexity-api-key:latest"
fi

gcloud run deploy generator-backend \
    --image gcr.io/$PROJECT_ID/generator-backend:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --port 8000 \
    --set-env-vars HOST=0.0.0.0 \
    --set-secrets $SECRETS_ARG \
    --max-instances 10 \
    --timeout 300

# Get generator backend URL
GENERATOR_BACKEND_URL=$(gcloud run services describe generator-backend --region $REGION --format 'value(status.url)')
echo "✅ Generator Backend deployed at: $GENERATOR_BACKEND_URL"

echo "🎨 Step 2: Building Generator Frontend..."
gcloud builds submit --config generator/cloudbuild-frontend.yaml .

echo "🚀 Deploying Generator Frontend to Cloud Run..."
gcloud run deploy generator-frontend \
    --image gcr.io/$PROJECT_ID/generator-frontend:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 500m \
    --port 8502 \
    --set-env-vars API_BASE_URL=$GENERATOR_BACKEND_URL/api/v1 \
    --max-instances 5 \
    --timeout 300

# Get generator frontend URL
GENERATOR_FRONTEND_URL=$(gcloud run services describe generator-frontend --region $REGION --format 'value(status.url)')
echo "✅ Generator Frontend deployed at: $GENERATOR_FRONTEND_URL"

# ===============================
# DEPLOY INTERVIEW SERVICE SECOND
# ===============================

echo "🤖 Step 3: Building Interview Backend..."
gcloud builds submit --config interview/cloudbuild.yaml .

echo "🚀 Deploying Interview Backend to Cloud Run..."
gcloud run deploy interview-backend \
    --image gcr.io/$PROJECT_ID/interview-backend:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --port 8001 \
    --set-env-vars HOST=0.0.0.0 \
    --set-secrets MONGODB_URI=mongodb-uri:latest,GEMINI_API_KEY=gemini-api-key:latest \
    --max-instances 10 \
    --timeout 300

# Get interview backend URL
INTERVIEW_BACKEND_URL=$(gcloud run services describe interview-backend --region $REGION --format 'value(status.url)')
echo "✅ Interview Backend deployed at: $INTERVIEW_BACKEND_URL"

echo "📊 Step 4: Building Interview Frontend..."
gcloud builds submit --config interview/cloudbuild-frontend.yaml .

echo "🚀 Deploying Interview Frontend to Cloud Run..."
gcloud run deploy interview-frontend \
    --image gcr.io/$PROJECT_ID/interview-frontend:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 500m \
    --port 8501 \
    --set-env-vars API_BASE_URL=$INTERVIEW_BACKEND_URL/api/v1/interview \
    --max-instances 5 \
    --timeout 300

# Get interview frontend URL
INTERVIEW_FRONTEND_URL=$(gcloud run services describe interview-frontend --region $REGION --format 'value(status.url)')
echo "✅ Interview Frontend deployed at: $INTERVIEW_FRONTEND_URL"

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "📊 GENERATOR SERVICE (Create Questions):"
echo "   UI:  $GENERATOR_FRONTEND_URL"
echo "   API: $GENERATOR_BACKEND_URL"
echo "   Docs: $GENERATOR_BACKEND_URL/docs"
echo ""
echo "🤖 INTERVIEW SERVICE (Conduct Interviews):"
echo "   UI:  $INTERVIEW_FRONTEND_URL" 
echo "   API: $INTERVIEW_BACKEND_URL"
echo "   Docs: $INTERVIEW_BACKEND_URL/docs"
echo ""
echo "🔗 WORKFLOW:"
echo "1. Use Generator UI to create questions: $GENERATOR_FRONTEND_URL"
echo "2. Use Interview UI to conduct interviews: $INTERVIEW_FRONTEND_URL"
echo ""
echo "📋 TESTING URLS TO SHARE:"
echo "• Question Generator: $GENERATOR_FRONTEND_URL"
echo "• Interview Platform: $INTERVIEW_FRONTEND_URL"
echo ""
echo "💡 To update deployment, run this script again with same parameters." 