.PHONY: start-default
start-default:  ## start containers
	docker compose pull --ignore-pull-failures
	docker compose build --no-cache --pull ${PROJECT_NAME}-django
	docker compose up -d --build

.PHONY: start-dev-docker-default
start-dev-docker-default:  ## start docker development setup
	docker compose pull --ignore-pull-failures
	docker compose build --pull ${PROJECT_NAME}-django
	docker compose up -d --build
	docker logs -f ${PROJECT_NAME}-django

.PHONY: stop-default
stop-default:  ## stop containers
	docker compose down

.PHONY: recreate-default
recreate-default:  ## fully reload the containers (e.g. due to .env file changes)
	docker compose up -d --force-recreate

.PHONY: gitignore-default
gitignore:  ## create a .gitignore file from templates
	bash config/make-gitignore.sh

.PHONY: git-update-default
git-update-default:  ## git pull as base user
	if [ "$(shell whoami)" != "base" ]; then sudo -u base git pull; else git pull; fi

.PHONY: init-default
init-default:  ## init django project
	docker compose exec ${PROJECT_NAME}-django bash -c "uv pip sync requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput"
ifeq ($(DEBUG),True)
	@make pre-commit-init
endif

.PHONY: init-dev-default
init-dev-default:  ## init django project for local development
	cd src && python manage.py migrate
	@make pre-commit-init

.PHONY: restart-gunicorn-default
restart-gunicorn-default:  ## gracefully restart gunicorn
	docker compose exec ${PROJECT_NAME}-django bash -c 'kill -HUP `cat /var/run/django.pid`'

.PHONY: build-docs-default
build-docs-default:  ## build documentation
	docker build -t ${PROJECT_NAME}-docs ./docker/docs
	docker run --rm -it -v `pwd`/docs:/docs -v `pwd`/src:/src ${PROJECT_NAME}-docs bash -c "make clean html"

.PHONY: update-default
update-default: git-update init restart-gunicorn build-docs  ## update project (runs git-update init restart-gunicorn build-docs)

.PHONY: makemessages-docker-default
makemessages-docker-default:  ## generate all required messages needed for localisation
	docker compose exec ${PROJECT_NAME}-django python manage.py makemessages -l de
	docker compose exec ${PROJECT_NAME}-django python manage.py makemessages -l en

.PHONY: compilemessages-docker-default
compilemessages-docker-default:  ## compile all localised messages to be available in the app
	docker compose exec ${PROJECT_NAME}-django python manage.py compilemessages

.PHONY: pip-compile-default
pip-compile-default:  ## run pip-compile locally
	uv pip compile src/requirements.in -o src/requirements.txt
	uv pip compile src/requirements-dev.in -o src/requirements-dev.txt

.PHONY: pip-compile-upgrade-default
pip-compile-upgrade-default:  ## run pip-compile locally with upgrade parameter
	uv pip compile src/requirements.in -o src/requirements.txt --upgrade
	uv pip compile src/requirements-dev.in -o src/requirements-dev.txt --upgrade

.PHONY: pip-compile-docker-default
pip-compile-docker-default:  ## run pip-compile in docker container
	docker compose exec ${PROJECT_NAME}-django uv pip compile src/requirements.in -o src/requirements.txt
	docker compose exec ${PROJECT_NAME}-django uv pip compile src/requirements-dev.in -o src/requirements-dev.txt

.PHONY: pip-compile-upgrade-docker-default
pip-compile-upgrade-docker-default:  ## run pip-compile in docker container with upgrade parameter
	docker compose exec ${PROJECT_NAME}-django uv pip compile src/requirements.in -o src/requirements.txt --upgrade
	docker compose exec ${PROJECT_NAME}-django uv pip compile src/requirements-dev.in -o src/requirements-dev.txt --upgrade

.PHONY: pre-commit-init-default
pre-commit-init-default:  ## initialize pre-commit
	python3 -m pip install --upgrade pre-commit
	pre-commit install --install-hooks --overwrite

.PHONY: pre-commit-clean-default
pre-commit-clean-default:  ## clean pre-commit
	pre-commit clean

.PHONY: pre-commit-update-default
pre-commit-update-default: pre-commit-clean-default pre-commit-init-default  ## update pre-commit and hooks

.PHONY: update-config-default
update-config-default:  ## update config subtree
	git subtree pull --prefix config git@github.com:base-angewandte/config.git main --squash

.PHONY: help
help:  ## show this help message
	@echo 'usage: make [command] ...'
	@echo
	@echo 'commands:'
	@egrep -h '^(.+)\:.+##\ (.+)' ${MAKEFILE_LIST} | sed 's/-default//g' | sed 's/:.*##/#/g' | sort -t# -u -k1,1 | column -t -c 2 -s '#'

# https://stackoverflow.com/a/49804748
%: %-default
	@true
