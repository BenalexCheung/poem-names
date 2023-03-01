# Makefile for Poem Names project
# pip3 install -r requirements.txt
# pip freeze > requirements.txt

all:
	python3 manage.py runserver

# Variables
DOCKER_COMPOSE_FILE=docker-compose.yaml
DOCKER_COMPOSE_DEV_FILE=docker-compose.dev.yaml

# Commands
.PHONY: build
build:
	docker-compose -f $(DOCKER_COMPOSE_FILE) build

.PHONY: run
run:
	docker-compose -f $(DOCKER_COMPOSE_FILE) up

.PHONY: test
test:
	docker-compose -f $(DOCKER_COMPOSE_DEV_FILE) run --rm backend python manage.py test

.PHONY: deploy
deploy:
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d
