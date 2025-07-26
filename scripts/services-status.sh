#!/bin/bash

# AI Interview Services - Status Script
# This script shows the current status of all services

set -e

PROJECT_ID="ai-interview-0726-demo"
REGION="us-central1"

echo "📊 AI Interview Services Status"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "=================================="
echo ""

# Function to get service status
get_service_status() {
    local service_name=$1
    echo "🔍 Checking $service_name..."
    
    if gcloud run services describe $service_name \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="table(
            metadata.name:label=SERVICE,
            status.url:label=URL,
            spec.template.spec.containers[0].resources.limits.cpu:label=CPU,
            spec.template.spec.containers[0].resources.limits.memory:label=MEMORY,
            spec.template.metadata.annotations.'autoscaling.knative.dev/maxScale':label=MAX_INSTANCES,
            status.conditions[0].status:label=READY
        )" 2>/dev/null; then
        echo ""
    else
        echo "❌ Service $service_name not found or error occurred"
        echo ""
    fi
}

# Check all services
get_service_status "generator-backend"
get_service_status "generator-frontend"
get_service_status "interview-backend"
get_service_status "interview-frontend"

echo "🔗 Quick Access URLs:"
echo "📝 Generator: https://generator-frontend-orovjqoova-uc.a.run.app"
echo "🤖 Interview: https://interview-frontend-orovjqoova-uc.a.run.app"
echo ""
echo "💡 Management Commands:"
echo "• Scale down all: ./scripts/services-down.sh"
echo "• Scale up all: ./scripts/services-up.sh" 