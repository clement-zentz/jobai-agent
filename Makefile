# Makefile
.PHONY: up build build-nc restart logs down down-v bash

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
	$(dc) down -v

bash:
	$(dc) exec api bash

