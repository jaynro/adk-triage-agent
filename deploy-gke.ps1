# Deployment script for Google Kubernetes Engine (PowerShell)

param(
    [string]$ProjectId = $env:GCP_PROJECT_ID,
    [string]$Region = "us-central1",
    [string]$ClusterName = "adk-triage-cluster",
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

Write-Host "=== ADK Triage Agent GKE Deployment ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectId"
Write-Host "Region: $Region"
Write-Host "Cluster: $ClusterName"
Write-Host ""

if ([string]::IsNullOrEmpty($ProjectId)) {
    Write-Host "ERROR: GCP_PROJECT_ID not set. Please set it first:" -ForegroundColor Red
    Write-Host "`$env:GCP_PROJECT_ID = 'your-project-id'" -ForegroundColor Yellow
    exit 1
}

$ImageName = "gcr.io/$ProjectId/adk-triage-agent"

# Authenticate with Google Cloud
Write-Host "Authenticating with Google Cloud..." -ForegroundColor Green
gcloud auth login
gcloud config set project $ProjectId

# Enable required APIs
Write-Host "Enabling required Google Cloud APIs..." -ForegroundColor Green
gcloud services enable container.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com

# Build and push Docker image
Write-Host "Building Docker image..." -ForegroundColor Green
docker build -t "${ImageName}:${ImageTag}" .

Write-Host "Pushing image to Google Container Registry..." -ForegroundColor Green
docker push "${ImageName}:${ImageTag}"

# Check if cluster exists
$clusterExists = gcloud container clusters describe $ClusterName --region=$Region 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating GKE cluster..." -ForegroundColor Green
    gcloud container clusters create $ClusterName `
        --region=$Region `
        --num-nodes=1 `
        --machine-type=e2-medium `
        --enable-autoscaling `
        --min-nodes=1 `
        --max-nodes=5 `
        --enable-autorepair `
        --enable-autoupgrade
} else {
    Write-Host "Cluster already exists, skipping creation..." -ForegroundColor Yellow
}

# Get cluster credentials
Write-Host "Getting cluster credentials..." -ForegroundColor Green
gcloud container clusters get-credentials $ClusterName --region=$Region

# Update image in deployment.yaml
Write-Host "Updating deployment manifest..." -ForegroundColor Green
(Get-Content k8s/deployment.yaml) -replace 'gcr.io/YOUR_PROJECT_ID/adk-triage-agent:latest', "${ImageName}:${ImageTag}" | Set-Content k8s/deployment.yaml

# Create namespace
Write-Host "Creating namespace..." -ForegroundColor Green
kubectl apply -f k8s/namespace.yaml

# Update secret
Write-Host ""
Write-Host "⚠️  IMPORTANT: Update k8s/secret.yaml with your Google API Key" -ForegroundColor Yellow
Write-Host "Press Enter when ready to continue..."
$null = Read-Host

# Apply Kubernetes manifests
Write-Host "Applying Kubernetes manifests..." -ForegroundColor Green
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Wait for deployment
Write-Host "Waiting for deployment to complete..." -ForegroundColor Green
kubectl rollout status deployment/adk-triage-agent -n adk-triage-agent --timeout=5m

# Get service details
Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Getting service information..." -ForegroundColor Green
kubectl get service adk-triage-agent-service -n adk-triage-agent

Write-Host ""
Write-Host "To get the external IP, run:" -ForegroundColor Yellow
Write-Host "kubectl get service adk-triage-agent-service -n adk-triage-agent" -ForegroundColor White
