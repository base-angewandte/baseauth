#!/bin/bash

set -e

if ! docker compose exec baseauth-postgres sh -c 'echo "SELECT * FROM django_migrations" | psql -U django_baseauth' | grep accounts | grep -q 0001_initial; then
	docker compose exec -T baseauth-postgres psql -U django_baseauth <"$(dirname "$0")/migrate-user-model.sql"
else
	echo 'Initial accounts migration is already applied.'
fi
