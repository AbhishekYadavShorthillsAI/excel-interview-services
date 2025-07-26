#!/bin/bash

# AI Interview Services - Scale Down Script
# This script scales all services to 0 instances (effectively stopping them)

set -e

PROJECT_ID="ai-interview-0726-demo"
REGION="us-central1"

echo "🔽 Scaling down AI Interview Services..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Note: Services will scale to 0 when inactive (min=0, max=1)"
echo ""

# Function to scale down a service
scale_down_service() {
    local service_name=$1
    echo "⏬ Scaling down $service_name..."
    
    if gcloud run services update $service_name \
        --region=$REGION \
        --project=$PROJECT_ID \
        --min-instances=0 \
        --max-instances=1 \
        --quiet; then
        echo "✅ $service_name scaled down (min=0, max=1)"
    else
        echo "❌ Failed to scale down $service_name"
    fi
    echo ""
}

# Scale down all services
scale_down_service "generator-backend"
scale_down_service "generator-frontend" 
scale_down_service "interview-backend"
scale_down_service "interview-frontend"

echo "🎯 All services have been scaled down!"
echo "💡 To bring them back up, run: ./scripts/services-up.sh"
echo ""
echo "📊 Check service status:"
echo "gcloud run services list --region=$REGION --project=$PROJECT_ID" 