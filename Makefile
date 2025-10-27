.PHONY: help build up down restart logs clean seed migrate test db-shell api-shell

help:
	@echo "Task Management API - Make Commands"
	@echo "===================================="
	@echo "make build       - Build Docker images"
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make restart     - Restart all services"
	@echo "make logs        - View logs (all services)"
	@echo "make logs-api    - View API logs only"
	@echo "make logs-nginx  - View Nginx logs only"
	@echo "make logs-db     - View Database logs only"
	@echo "make clean       - Remove containers, volumes, networks (keeps images)"
	@echo "make clean-all   - Remove containers, volumes, networks AND images"
	@echo "make seed        - Seed the database with sample data"
	@echo "make migrate     - Run database migrations"
	@echo "make migration-create - Create a new migration (interactive)"
	@echo "make db-shell    - Open PostgreSQL shell"
	@echo "make api-shell   - Open API container shell"
	@echo "make status      - Show status of all containers"
	@echo "make health      - Check API health"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started! API available at http://localhost"
	@echo "API Docs: http://localhost/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-nginx:
	docker-compose logs -f nginx

logs-db:
	docker-compose logs -f db

clean:
	docker-compose down -v --remove-orphans
	@echo "All containers, volumes, and networks removed!"

clean-all:
	docker-compose down -v --remove-orphans --rmi all
	@echo "All containers, volumes, networks AND images removed!"

seed:
	docker-compose exec api python -m migrations.seed

migrate:
	docker-compose exec api alembic upgrade head

migration-create:
	@read -p "Enter migration message: " msg; \
	docker-compose exec api alembic revision --autogenerate -m "$$msg"

db-shell:
	docker-compose exec db psql -U postgres -d task_db

api-shell:
	docker-compose exec api /bin/sh

health:
	@curl -s http://localhost/health | python -m json.tool

status:
	docker-compose ps
