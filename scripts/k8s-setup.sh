#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Kubernetes setup..."

# Check if minikube is running
if ! minikube status | grep -q "Running"; then
    echo "📦 Starting Minikube..."
    minikube start --driver=docker
fi

# Switch to minikube's Docker daemon
echo "🔄 Switching to Minikube's Docker daemon..."
eval $(minikube docker-env)

# Build the Docker image
echo "🏗️  Building Docker image..."
docker build -t scheduled-tasks-ai-web:latest .

# Create namespace if it doesn't exist
echo "🌍 Creating namespace..."
kubectl create namespace scheduled-tasks-ai 2>/dev/null || true

# Create secrets from .env file
echo "🔐 Creating secrets..."
kubectl create secret generic django-secrets \
    --from-env-file=.env \
    --namespace scheduled-tasks-ai \
    -o yaml --dry-run=client | kubectl apply -f -

# Apply Kubernetes configurations
echo "⚙️  Applying Kubernetes configurations..."
kubectl apply -k kubernetes/overlays/development

# Wait for pods to be ready
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=django --timeout=120s -n scheduled-tasks-ai
kubectl wait --for=condition=ready pod -l app=redis --timeout=120s -n scheduled-tasks-ai
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s -n scheduled-tasks-ai
kubectl wait --for=condition=ready pod -l app=qcluster --timeout=120s -n scheduled-tasks-ai

echo "✅ Setup complete! Run these commands to:"
echo "🔍 View logs:          kubectl logs -f deployment/django -n scheduled-tasks-ai"
echo "🐚 Access shell:       kubectl exec -it deployment/django -n scheduled-tasks-ai -- sh"
echo "🌐 Forward port:       kubectl port-forward service/django 8000:8000 -n scheduled-tasks-ai"
echo "👤 Create superuser:   kubectl exec -it deployment/django -n scheduled-tasks-ai -- python manage.py createsuperuser"
