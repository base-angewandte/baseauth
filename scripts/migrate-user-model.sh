#!/bin/bash

set -e

if [ -z "${PROJECT_NAME}" ]; then
	echo "ERROR: this script has to be called through the make command: make migrate-user-model"
	exit
fi

QUERY="echo \"SELECT * FROM django_migrations\" | psql -U django_${PROJECT_NAME}"

if ! docker compose exec baseauth-postgres sh -c "${QUERY}" | grep accounts | grep -q 0001_initial; then
	docker compose exec -T baseauth-postgres psql -U django_baseauth <"$(dirname "$0")/migrate-user-model.sql"
else
	echo 'Initial accounts migration is already applied.'
fi
