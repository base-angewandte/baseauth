include .env
export

PROJECT_NAME ?= baseauth

include config/base.mk

start-dev:  ## start containers for local development
	docker-compose up -d --build \
		${PROJECT_NAME}-redis \
		${PROJECT_NAME}-postgres

.PHONY: migrate-user-model
migrate-user-model:  ## migrate user model from Django default to custom model
	@bash scripts/migrate-user-model.sh
