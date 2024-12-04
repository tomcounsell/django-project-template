#!/bin/bash

# Exit on error
set -e

echo "🧹 Cleaning up Kubernetes resources..."

# Delete all resources in the namespace
kubectl delete namespace scheduled-tasks-ai

# Stop minikube if requested
if [ "$1" == "--stop" ]; then
    echo "🛑 Stopping Minikube..."
    minikube stop
fi

echo "✨ Cleanup complete!"
