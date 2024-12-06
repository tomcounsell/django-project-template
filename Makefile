# Variables
DOCKER_COMPOSE = docker-compose
ENV_FILE = .env

# Help command
.PHONY: help
help:
	@echo "Makefile Commands:"
	@echo "  make build        Build Docker images."
	@echo "  make up           Start Docker containers."
	@echo "  make down         Stop Docker containers."
	@echo "  make logs         Tail logs for all containers."
	@echo "  make ps           List running containers."
	@echo "  make shell        Access Django container shell."
	@echo "  make superuser    Create a Django superuser."
	@echo "  make grafana-init Setup Grafana and Prometheus."
	@echo "  make clean        Remove Docker containers and volumes."

# Docker-related commands
.PHONY: build
build:
	$(DOCKER_COMPOSE) build

.PHONY: up
up:
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down:
	$(DOCKER_COMPOSE) down --volumes

.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: ps
ps:
	$(DOCKER_COMPOSE) ps

.PHONY: shell
shell:
	$(DOCKER_COMPOSE) exec django sh

.PHONY: superuser
superuser:
	$(DOCKER_COMPOSE) exec django sh -c "python manage.py createsuperuser"

# Grafana and Prometheus setup
.PHONY: grafana-init
grafana-init:
	@echo "1. Open Grafana at http://localhost:3000."
	@echo "2. Login with 'admin' and the password in $(ENV_FILE)."
	@echo "3. Add Prometheus as a data source with URL: http://prometheus:9090."

# Clean up
.PHONY: clean
clean:
	$(DOCKER_COMPOSE) down --volumes --remove-orphans
	docker volume prune -f