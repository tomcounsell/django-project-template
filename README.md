# Scheduled Tasks AI Template

## Installation
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
4. Enter the container shell:
   ```bash
   docker-compose exec web sh
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Access the admin interface:
   ```
   http://localhost:8000/admin
   ```

### With Kubernetes Minikube
1. Install Minikube:
   ```bash
   brew install kubectl minikube helm
   ```
2. Start Minikube:
   ```bash
   minikube start --driver=docker
   ```
3. Apply Kubernetes configurations:
   ```bash
   kubectl apply -f kubernetes/base/
   kubectl apply -f kubernetes/overlays/development/
   ```
4. Get the application URL:
   ```bash
   minikube service scheduled-tasks-ai --url
   ```