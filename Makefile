include .env
export


start:
	docker-compose up -d --build

stop:
	docker-compose down

restart:
	docker-compose restart

git-update:
	if [ "$(shell whoami)" != "base" ]; then sudo -u base git pull; else git pull; fi

init:
	docker-compose exec cas-django bash -c "pip-sync && python manage.py migrate"

init-static:
	docker-compose exec cas-django bash -c "python manage.py collectstatic --noinput"

build-cas:
	docker-compose build cas-django

restart-gunicorn:
	docker-compose exec cas-django bash -c 'kill -HUP `cat /var/run/django.pid`'

update: git-update init init-static restart-gunicorn

start-dev:
	docker-compose up -d --build \
		cas-redis \
		cas-postgres

pip-compile:
	pip-compile src/requirements.in
	pip-compile src/requirements-dev.in

pip-compile-upgrade:
	pip-compile src/requirements.in --upgrade
	pip-compile src/requirements-dev.in --upgrade
