# AI Interview Services Management

This guide shows you how to manage your deployed AI Interview services with single commands.

## 📋 Available Commands

### 🔽 Scale Down All Services
```bash
./scripts/services-down.sh
```
- **What it does**: Scales services to minimal configuration (min=0, max=1)
- **Why use it**: Significant cost savings when not actively using services
- **Cost impact**: ✅ **Reduces costs by ~80-90%** (services auto-scale to 0 when idle)
- **Behavior**: Services will automatically scale down to 0 instances when no traffic

### 🔼 Scale Up All Services  
```bash
./scripts/services-up.sh
```
- **What it does**: Scales all services back to normal instance counts
- **Why use it**: Resume normal operations after scaling down
- **Instance counts**: 
  - Backend services: 10 max instances
  - Frontend services: 5 max instances

### 📊 Check Service Status
```bash
./scripts/services-status.sh
```
- **What it does**: Shows current status of all services
- **Information shown**: CPU, Memory, Max Instances, Ready status, URLs

## 🔗 Your Service URLs

Once services are scaled up, access them here:

- **📝 Generator Service**: https://generator-frontend-orovjqoova-uc.a.run.app
- **🤖 Interview Service**: https://interview-frontend-orovjqoova-uc.a.run.app

## 💡 Usage Examples

### Daily Development Workflow
```bash
# Start your work day
./scripts/services-up.sh

# Check if everything is running
./scripts/services-status.sh

# End of day - save costs
./scripts/services-down.sh
```

### Maintenance Mode
```bash
# Scale down for maintenance
./scripts/services-down.sh

# Deploy updates using your existing deployment scripts
./scripts/deploy.sh ai-interview-0726-demo us-central1 "..." "..." "..."

# Scale back up
./scripts/services-up.sh
```

## 💰 Cost Optimization

- **Services Running (Normal)**: ~$10-50/month (depending on usage)
- **Services Scaled Down**: ~$1-5/month (minimal instances, auto-scale to 0)
- **Best Practice**: Scale down when not actively developing or testing
- **Note**: "Scaled down" services still work but may have 1-2 second cold start delay

## 🛠️ Technical Details

- **Platform**: Google Cloud Run
- **Project**: `ai-interview-0726-demo`
- **Region**: `us-central1`
- **Scaling Method**: Min/Max instance configuration
- **Services Managed**: 4 total (2 backends + 2 frontends)

## 🚨 Troubleshooting

### Services Won't Scale Down
```bash
# Force check individual service
gcloud run services describe SERVICE_NAME --region=us-central1 --project=ai-interview-0726-demo
```

### Services Won't Scale Up
```bash
# Check quotas and billing
gcloud run services list --region=us-central1 --project=ai-interview-0726-demo
```

### Need to Redeploy
```bash
# Scale down first
./scripts/services-down.sh

# Use your existing deploy script
./scripts/deploy.sh [your-params]

# No need to scale up - deploy script handles this
``` 