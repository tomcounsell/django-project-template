# Scheduled Tasks for Generative AI Template

Paul Tuck <@pau1tuck>

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
   git clone https://github.com/aihelps/scheduled-tasks-ai.git
   ```
2. Navigate to the project directory:
   ```bash
   cd scheduled-tasks-ai
   ```

### With Docker Compose

1. Build and run the containers:
   ```bash
   make up
   ```

2. Check the status of the containers:
   ```bash
   make ps
   ```

3. Access the container shell:
   ```bash
   make shell
   ```

4. Create a superuser account (to log in to the admin interface):
   ```bash
   make superuser
   ```

5. Access the admin interface:
   http://localhost:8000/admin

6. (Optional) View container logs:
   make logs

### Using VSCode Dev Containers

To streamline development, you can open this project directly in VSCode using **Dev Containers**. Follow these steps:

1. **Install Required Extensions:**
   - Ensure you have the following VSCode extensions installed:
     - **Dev Containers** (Remote - Containers)
     - **Docker**
     - **Python**

2. **Open the Repository in VSCode:**
   - Launch VSCode and open the project folder:
     ```bash
     code .
     ```

3. **Reopen in Dev Container:**
   - Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
   - Select **Dev Containers: Reopen in Container**.
   - VSCode will rebuild the container and attach to it automatically.

4. **Verify Python Interpreter:**
   - Ensure the Python interpreter is set to the container environment:
     - Open the Command Palette and select **Python: Select Interpreter**.
     - Choose the path `/usr/local/bin/python`.

5. **Run the Application:**
   - Use the integrated terminal in VSCode to manage the project:
     ```bash
     python manage.py runserver
     ```
   - Access the application at:
     ```
     http://localhost:8000
     ```

### Grafana Setup

#### Add Prometheus as a Data Source

1. Navigate to the Grafana dashboard at `http://localhost:3000`.
2. Login with the username `admin` and the password you set for `GF_SECURITY_ADMIN_PASSWORD` in your `.env` file. If not set, the default password is `admin`.
3. In the left-hand sidebar, find “Connections” and click on “Data sources.”
4. Click "Add data source."
5. Select Prometheus.
6. In the "Prometheus server URL" field, enter: `http://prometheus:9090`.
7. Click "Save & Test" to verify the connection.

### Alternative Installation: With Kubernetes Minikube

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