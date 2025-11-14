# Makefile
.PHONY: up build restart logs down

dc=docker compose

up:
	$(dc) up -d

build:
	$(dc) build

restart:
	$(dc) restart

logs:
	$(dc) logs

down:
	$(dc) down

