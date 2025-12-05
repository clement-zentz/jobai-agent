# Makefile
.PHONY: up build build-nc restart logs down down-v bash fixture test coverage

dc=docker compose

up:
	$(dc) up --watch

build:
	$(dc) build

build-nc:
	$(dc) build --no-cache

restart:
	$(dc) restart

logs:
	$(dc) logs

down:
	$(dc) down

down-v:
	$(dc) down -v --remove-orphans

bash:
	$(dc) exec api bash

fixture:
	$(dc) exec api python3 -m scripts.python.generate_fixtures

test:
	$(dc) exec api pytest

coverage:
	$(dc) exec api pytest --cov=app --cov-report=term-missing

