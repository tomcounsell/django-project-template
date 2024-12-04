# Scheduled Tasks for Generative AI Template

Paul Tuck @pau1tuck

## Installation

### Prerequisites
- Python => 3.10
- PostgreSQL => 16.0
- Redis => 7.0
- Docker => 24.0
- Docker Compose => 2.17
- Hadolint => 2.12.0 (optional)

### Quickstart

1. Clone the repository:
   ```bash
   git clone https://github.com/aihelps/scheduled-tasks-ai-template.git
   ```
2. Navigate to the project directory:
   ```bash
   cd scheduled-tasks-ai-template
   ```

### With Docker Compose
1. Run `export xlm=xlm`
   
2. Install Docker Compose:
   ```bash
   brew install docker-compose
   ```
3. Build and run the containers:
   ```bash
   docker-compose build && docker-compose up
   ```
4. Check the status of the containers:
   ```bash
   docker-compose ps
   ```
5. Access the container shell:
   ```bash
   docker-compose exec web sh
   ```
6. Create a superuser account:
   ```bash
   docker compose exec web sh -c "python manage.py createsuperuser"
   ```
7. Access the admin interface:
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