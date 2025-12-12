# Makefile
.PHONY: up build build-nc restart logs down down-v bash fixture cov

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

fixture-debug:
	$(dc) exec api \
	python3 -Xfrozen_modules=off -m debugpy \
	--listen 0.0.0.0:5679 \
	--wait-for-client \
	-m scripts.python.generate_fixtures

cov:
	pytest --cov=app --cov-report=term-missing
