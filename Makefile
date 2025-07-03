# Makefile for Resume Job Matcher Docker Operations
.PHONY: help build run stop clean logs shell test dev prod monitoring

# Default environment
ENV ?= development
COMPOSE_FILES = -f deployment/docker/docker-compose.yml

# Set compose files based on environment
ifeq ($(ENV),development)
	COMPOSE_FILES += -f deployment/docker/docker-compose.dev.yml
else ifeq ($(ENV),production)
	COMPOSE_FILES += -f deployment/docker/docker-compose.prod.yml
endif

# Docker compose command
DOCKER_COMPOSE = docker-compose $(COMPOSE_FILES)

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "Resume Job Matcher Docker Operations"
	@echo ""
	@echo "Usage: make [target] [ENV=development|production]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@echo "  make dev                    # Start development environment"
	@echo "  make prod                   # Start production environment"
	@echo "  make build ENV=production   # Build production images"
	@echo "  make logs SERVICE=api       # Show API service logs"

build: ## Build Docker images
	@echo "$(GREEN)Building images for $(ENV) environment...$(NC)"
	$(DOCKER_COMPOSE) build

run: ## Run services
	@echo "$(GREEN)Starting $(ENV) environment...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN).env file created. Please review and update values.$(NC)"; \
	fi
	$(DOCKER_COMPOSE) up

run-detached: ## Run services in background
	@echo "$(GREEN)Starting $(ENV) environment in background...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN).env file created. Please review and update values.$(NC)"; \
	fi
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Services started successfully!$(NC)"
	@echo "API available at: $(YELLOW)http://localhost:8000$(NC)"
	@echo "API docs at: $(YELLOW)http://localhost:8000/docs$(NC)"

dev: ## Start development environment
	@$(MAKE) run ENV=development

dev-build: ## Build and start development environment
	@echo "$(GREEN)Building and starting development environment...$(NC)"
	@$(MAKE) build ENV=development
	@$(MAKE) run ENV=development

prod: ## Start production environment
	@$(MAKE) run-detached ENV=production

prod-build: ## Build and start production environment
	@echo "$(GREEN)Building and starting production environment...$(NC)"
	@$(MAKE) build ENV=production
	@$(MAKE) run-detached ENV=production

monitoring: ## Start with monitoring services (Flower)
	@echo "$(GREEN)Starting with monitoring services...$(NC)"
	$(DOCKER_COMPOSE) --profile monitoring up -d

stop: ## Stop all services
	@echo "$(GREEN)Stopping services...$(NC)"
	$(DOCKER_COMPOSE) down

stop-volumes: ## Stop services and remove volumes
	@echo "$(GREEN)Stopping services and removing volumes...$(NC)"
	$(DOCKER_COMPOSE) down -v

restart: ## Restart services
	@echo "$(GREEN)Restarting services...$(NC)"
	$(DOCKER_COMPOSE) restart

logs: ## Show logs (use SERVICE=name for specific service)
ifdef SERVICE
	@echo "$(GREEN)Showing logs for $(SERVICE)...$(NC)"
	$(DOCKER_COMPOSE) logs -f $(SERVICE)
else
	@echo "$(GREEN)Showing all logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f
endif

shell: ## Open shell in API container
	@echo "$(GREEN)Opening shell in API container...$(NC)"
	$(DOCKER_COMPOSE) exec api bash

shell-worker: ## Open shell in worker container
	@echo "$(GREEN)Opening shell in worker container...$(NC)"
	$(DOCKER_COMPOSE) exec worker bash

shell-redis: ## Open Redis CLI
	@echo "$(GREEN)Opening Redis CLI...$(NC)"
	$(DOCKER_COMPOSE) exec redis redis-cli

ps: ## Show running containers
	@echo "$(GREEN)Running containers:$(NC)"
	$(DOCKER_COMPOSE) ps

status: ## Show service status
	@echo "$(GREEN)Service status:$(NC)"
	$(DOCKER_COMPOSE) ps --format table

health: ## Check service health
	@echo "$(GREEN)Checking service health...$(NC)"
	@echo "API Health:"
	@curl -s http://localhost:8000/api/v1/health/ | jq . || echo "API not responding"
	@echo "\nRedis Health:"
	@$(DOCKER_COMPOSE) exec redis redis-cli ping || echo "Redis not responding"
	@echo "\nWorker Health:"
	@$(DOCKER_COMPOSE) exec worker celery -A app.core.celery_app.celery_app inspect ping || echo "Worker not responding"

test: ## Run tests in container
	@echo "$(GREEN)Running tests...$(NC)"
	$(DOCKER_COMPOSE) exec api python -m pytest tests/ -v

test-build: ## Build and run tests
	@echo "$(GREEN)Building and running tests...$(NC)"
	@$(MAKE) build ENV=development
	$(DOCKER_COMPOSE) run --rm api python -m pytest tests/ -v

clean: ## Clean up containers, images, and volumes
	@echo "$(GREEN)Cleaning up Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v --rmi all
	docker system prune -f

clean-all: ## Clean up everything including unused images and volumes
	@echo "$(RED)Warning: This will remove all unused Docker resources!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) down -v --rmi all; \
		docker system prune -a -f --volumes; \
		echo "$(GREEN)Cleanup completed!$(NC)"; \
	else \
		echo "$(YELLOW)Cleanup cancelled.$(NC)"; \
	fi

backup: ## Backup application data
	@echo "$(GREEN)Creating backup...$(NC)"
	@mkdir -p backups
	@docker run --rm \
		-v resume-matcher_app_data:/data \
		-v $(PWD)/backups:/backup \
		alpine tar czf /backup/app_data_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz -C /data .
	@echo "$(GREEN)Backup created in backups/ directory$(NC)"

restore: ## Restore application data (use BACKUP_FILE=filename)
ifndef BACKUP_FILE
	@echo "$(RED)Error: Please specify BACKUP_FILE=filename$(NC)"
	@echo "Available backups:"
	@ls -la backups/ 2>/dev/null || echo "No backups found"
else
	@echo "$(GREEN)Restoring from $(BACKUP_FILE)...$(NC)"
	@docker run --rm \
		-v resume-matcher_app_data:/data \
		-v $(PWD)/backups:/backup \
		alpine tar xzf /backup/$(BACKUP_FILE) -C /data
	@echo "$(GREEN)Restore completed!$(NC)"
endif

update: ## Pull latest images and restart
	@echo "$(GREEN)Updating images and restarting...$(NC)"
	$(DOCKER_COMPOSE) pull
	$(DOCKER_COMPOSE) up -d

config: ## Validate and show Docker Compose configuration
	@echo "$(GREEN)Docker Compose configuration:$(NC)"
	$(DOCKER_COMPOSE) config

# Development shortcuts
install: ## Install development environment
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@$(MAKE) dev-build

reset: ## Reset development environment
	@echo "$(GREEN)Resetting development environment...$(NC)"
	@$(MAKE) stop
	@$(MAKE) clean
	@$(MAKE) dev-build

# Production shortcuts
deploy: ## Deploy to production
	@echo "$(GREEN)Deploying to production...$(NC)"
	@$(MAKE) prod-build

# Quick commands
up: run ## Alias for run
down: stop ## Alias for stop
build-dev: dev-build ## Alias for dev-build
build-prod: prod-build ## Alias for prod-build