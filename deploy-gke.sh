#!/bin/bash
# Deployment script for Google Kubernetes Engine

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-YOUR_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
CLUSTER_NAME="${GKE_CLUSTER_NAME:-adk-triage-cluster}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/adk-triage-agent"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "=== ADK Triage Agent GKE Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Cluster: $CLUSTER_NAME"
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Authenticate with Google Cloud
echo "Authenticating with Google Cloud..."
gcloud auth login
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required Google Cloud APIs..."
gcloud services enable \
    container.googleapis.com \
    containerregistry.googleapis.com \
    cloudbuild.googleapis.com

# Build and push Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo "Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}:${IMAGE_TAG}

# Create GKE cluster (if it doesn't exist)
if ! gcloud container clusters describe $CLUSTER_NAME --region=$REGION &>/dev/null; then
    echo "Creating GKE cluster..."
    gcloud container clusters create $CLUSTER_NAME \
        --region=$REGION \
        --num-nodes=1 \
        --machine-type=e2-medium \
        --enable-autoscaling \
        --min-nodes=1 \
        --max-nodes=5 \
        --enable-autorepair \
        --enable-autoupgrade
else
    echo "Cluster already exists, skipping creation..."
fi

# Get cluster credentials
echo "Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Update image in deployment.yaml
echo "Updating deployment manifest..."
sed -i "s|gcr.io/YOUR_PROJECT_ID/adk-triage-agent:latest|${IMAGE_NAME}:${IMAGE_TAG}|g" k8s/deployment.yaml

# Create namespace
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Update secret with your API key
echo "⚠️  IMPORTANT: Update k8s/secret.yaml with your Google API Key before proceeding"
read -p "Press enter when ready to continue..."

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Wait for deployment
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/adk-triage-agent -n adk-triage-agent --timeout=5m

# Get service external IP
echo "Getting service external IP..."
echo "Waiting for LoadBalancer IP (this may take a few minutes)..."
kubectl get service adk-triage-agent-service -n adk-triage-agent --watch

echo ""
echo "=== Deployment Complete ==="
echo "Run the following command to get the external IP:"
echo "kubectl get service adk-triage-agent-service -n adk-triage-agent"
