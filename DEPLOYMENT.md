# Deploying ADK Triage Agent to Google Kubernetes Engine (GKE)

This guide walks you through deploying the ADK Triage Agent to production on Google Kubernetes Engine.

## Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed and configured
- `kubectl` installed
- `docker` installed
- Google API Key for GenAI

## Quick Start

### 1. Set Environment Variables

```powershell
$env:GCP_PROJECT_ID = "your-gcp-project-id"
$env:GCP_REGION = "us-central1"
```

### 2. Update Secret

Edit `k8s/secret.yaml` and replace `YOUR_GOOGLE_API_KEY_HERE` with your actual Google API key.

### 3. Run Deployment Script

```powershell
.\deploy-gke.ps1 -ProjectId "your-project-id"
```

## Manual Deployment Steps

### 1. Build and Push Docker Image

```powershell
# Set your project ID
$PROJECT_ID = "your-project-id"

# Build the image
docker build -t gcr.io/$PROJECT_ID/adk-triage-agent:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/adk-triage-agent:latest
```

### 2. Create GKE Cluster

```powershell
gcloud container clusters create adk-triage-cluster `
    --region us-central1 `
    --num-nodes 1 `
    --machine-type e2-medium `
    --enable-autoscaling `
    --min-nodes 1 `
    --max-nodes 5
```

### 3. Get Cluster Credentials

```powershell
gcloud container clusters get-credentials adk-triage-cluster --region us-central1
```

### 4. Deploy to Kubernetes

```powershell
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secret (update with your API key first!)
kubectl apply -f k8s/secret.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

### 5. Get External IP

```powershell
kubectl get service adk-triage-agent-service -n adk-triage-agent
```

Wait for the `EXTERNAL-IP` to be assigned (may take a few minutes).

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Load Balancer (External)        │
│              (Port 80)                  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Kubernetes Service              │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌───────▼──────┐
│   Pod 1      │  │   Pod 2      │
│   (App)      │  │   (App)      │
│   Port 8080  │  │   Port 8080  │
└──────────────┘  └──────────────┘
```

## Kubernetes Resources

### Deployment
- **Replicas**: 2 (can scale 1-10 with HPA)
- **Container Image**: `gcr.io/YOUR_PROJECT/adk-triage-agent:latest`
- **Resources**:
  - Requests: 250m CPU, 512Mi memory
  - Limits: 500m CPU, 1Gi memory
- **Health Checks**: Liveness and Readiness probes on `/health`

### Service
- **Type**: LoadBalancer
- **External Port**: 80
- **Target Port**: 8080
- **Session Affinity**: ClientIP

### HorizontalPodAutoscaler
- **Min Replicas**: 2
- **Max Replicas**: 10
- **Target CPU**: 70%
- **Target Memory**: 80%

## Security Best Practices

1. **Secrets Management**: 
   - Never commit `k8s/secret.yaml` with real credentials
   - Use Google Secret Manager for production
   
2. **Non-Root User**: Container runs as user 1000

3. **Network Policies**: Add network policies to restrict traffic

4. **RBAC**: Implement proper Role-Based Access Control

## Monitoring

### Check Pod Status
```powershell
kubectl get pods -n adk-triage-agent
```

### View Logs
```powershell
kubectl logs -f deployment/adk-triage-agent -n adk-triage-agent
```

### Check HPA Status
```powershell
kubectl get hpa -n adk-triage-agent
```

### Describe Service
```powershell
kubectl describe service adk-triage-agent-service -n adk-triage-agent
```

## Scaling

### Manual Scaling
```powershell
kubectl scale deployment adk-triage-agent --replicas=5 -n adk-triage-agent
```

### Auto-scaling is enabled by default via HPA

## Updating the Application

```powershell
# Build new image
docker build -t gcr.io/$PROJECT_ID/adk-triage-agent:v2 .

# Push to registry
docker push gcr.io/$PROJECT_ID/adk-triage-agent:v2

# Update deployment
kubectl set image deployment/adk-triage-agent `
    adk-triage-agent=gcr.io/$PROJECT_ID/adk-triage-agent:v2 `
    -n adk-triage-agent

# Check rollout status
kubectl rollout status deployment/adk-triage-agent -n adk-triage-agent
```

## Rollback

```powershell
kubectl rollout undo deployment/adk-triage-agent -n adk-triage-agent
```

## Cost Optimization

- **Machine Type**: Using `e2-medium` (cost-effective)
- **Autoscaling**: Scales down to 1 node when idle
- **Preemptible Nodes**: Consider for non-critical workloads

## Cleanup

```powershell
# Delete all resources
kubectl delete namespace adk-triage-agent

# Delete cluster
gcloud container clusters delete adk-triage-cluster --region us-central1
```

## Troubleshooting

### Pods Not Starting
```powershell
kubectl describe pod <pod-name> -n adk-triage-agent
kubectl logs <pod-name> -n adk-triage-agent
```

### Service Not Accessible
```powershell
kubectl get events -n adk-triage-agent
kubectl get service adk-triage-agent-service -n adk-triage-agent -o yaml
```

### Image Pull Errors
```powershell
# Ensure you're authenticated
gcloud auth configure-docker
```

## Next Steps

1. Set up CI/CD with Cloud Build
2. Configure Cloud Monitoring and Logging
3. Set up SSL/TLS with Google-managed certificates
4. Implement Cloud Armor for DDoS protection
5. Use Cloud CDN for static assets
