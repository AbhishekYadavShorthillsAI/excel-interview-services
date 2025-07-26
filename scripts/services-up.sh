#!/bin/bash

# AI Interview Services - Scale Up Script
# This script scales all services back to their normal instance counts

set -e

PROJECT_ID="ai-interview-0726-demo"
REGION="us-central1"

echo "🔼 Scaling up AI Interview Services..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Function to scale up a service
scale_up_service() {
    local service_name=$1
    local max_instances=$2
    echo "⏫ Scaling up $service_name (max: $max_instances instances)..."
    
    if gcloud run services update $service_name \
        --region=$REGION \
        --project=$PROJECT_ID \
        --min-instances=0 \
        --max-instances=$max_instances \
        --quiet; then
        echo "✅ $service_name scaled up"
    else
        echo "❌ Failed to scale up $service_name"
    fi
    echo ""
}

# Scale up all services to their normal instance counts
scale_up_service "generator-backend" 10
scale_up_service "generator-frontend" 5
scale_up_service "interview-backend" 10
scale_up_service "interview-frontend" 5

echo "🎯 All services have been scaled up!"
echo ""
echo "🔗 Your service URLs:"
echo "📝 Generator Frontend: https://generator-frontend-orovjqoova-uc.a.run.app"
echo "🤖 Interview Frontend: https://interview-frontend-orovjqoova-uc.a.run.app"
echo ""
echo "📊 Check service status:"
echo "gcloud run services list --region=$REGION --project=$PROJECT_ID" 