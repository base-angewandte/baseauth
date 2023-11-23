include .env
export

PROJECT_NAME ?= baseauth

include config/base.mk

start-dev:  ## start containers for local development
	docker-compose up -d --build \
		${PROJECT_NAME}-redis \
		${PROJECT_NAME}-postgres
