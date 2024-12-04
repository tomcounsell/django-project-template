# Scheduled Tasks AI Template

## Installation
Install PostgreSQL
Install Redis
Install Hadolint

1. Clone the repository:
   ```bash
   git clone https://github.com/aihelps/scheduled-tasks-ai-template.git
   ```
2. Navigate to the project directory:
   ```bash
   cd scheduled-tasks-ai-template
   ```

### With Docker Compose
1. Install Docker Compose:
   ```bash
   brew install docker-compose
   ```
2. Build and run the containers:
   ```bash
   docker-compose build && docker-compose up
   ```
3. Check the status of the containers:
   ```bash
   docker-compose ps
   ```
4. Access the container shell:
   ```bash
   docker-compose exec web sh
   ```
5. Create a superuser account:
   ```bash
   docker compose exec web sh -c "python manage.py createsuperuser"
   ```
6. Access the admin interface:
   ```
   http://localhost:8000/admin
   ```

### With Kubernetes Minikube
1. Install required tools:
   ```bash
   brew install kubectl minikube helm
   ```
2. Make the setup scripts executable:
   ```bash
   chmod +x scripts/k8s-setup.sh scripts/k8s-cleanup.sh
   ```
3. Run the setup script:
   ```bash
   ./scripts/k8s-setup.sh
   ```
4. Forward the port to access the application:
   ```bash
   kubectl port-forward service/django 8000:8000 -n scheduled-tasks-ai
   ```
5. Create a superuser:
   ```bash
   kubectl exec -it deployment/django -n scheduled-tasks-ai -- python manage.py createsuperuser
   ```
6. Access the admin interface:
   ```
   http://localhost:8000/admin
   ```

To clean up:
```bash
./scripts/k8s-cleanup.sh        # Remove all resources
./scripts/k8s-cleanup.sh --stop # Remove all resources and stop Minikube
```

Useful commands:
```bash
# View logs
kubectl logs -f deployment/django -n scheduled-tasks-ai    # Django logs
kubectl logs -f deployment/qcluster -n scheduled-tasks-ai  # Q-cluster logs
kubectl logs -f deployment/redis -n scheduled-tasks-ai     # Redis logs
kubectl logs -f deployment/postgres -n scheduled-tasks-ai  # PostgreSQL logs

# Access shell
kubectl exec -it deployment/django -n scheduled-tasks-ai -- sh

# Launch Kubernetes Dashboard
minikube dashboard