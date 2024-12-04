# Command Reference (MacOS)

## Install with Kubernetes Minikube

```sh
brew install kubectl minikube helm
minikube start --driver=docker

## Install with Docker Compose

```sh
brew install docker-compose
export xlm=xlm
docker-compose build
docker-compose up
docker-compose exec web sh # to enter the container shell
python manage.py migrate
```

## Run Tests:
```sh
pytest apps/insights/tests/test_summary_service.py -s
pytest apps/insights/tests/test_comparison_generator.py -s
pytest apps/insights/tests/test_comparison_service.py -s
pytest apps/insights/tests/test_task_scheduler.py -s
```

```sh
# Minikube commands
minikube start      # Start your local cluster
minikube stop       # Stop the cluster
minikube dashboard  # Open the Kubernetes dashboard in your browser

# kubectl commands
kubectl get pods              # List all running pods
kubectl get services         # List all services
kubectl describe pod <name>  # Get detailed info about a pod
kubectl describe service <service-name>
kubectl logs <pod-name>      # View pod logs
```