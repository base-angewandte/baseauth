# Installation guide

Before you set up either a production or development instance, make sure
to meet all the [](./requirements.md).

```{admonition} Additional steps when migrating
:class: tip

In case you are not creating a fresh installation, but are migrating
from some older version, make sure to check out the [](./migration.md)
first. In some cases you need to take additional steps, that are not
outlined here.
```

## Development

There are two supported ways to start the development server:

1. Start only the auxiliary servers (database and redis) in docker
   but start the django dev server locally in your virtual env. This
   is the preferred way if you actively develop this application.

2. Start everything inside docker containers. This is the "easy" way
   to start a dev server and fiddle around with it, hot reloading included.

In both cases there are some common steps to follow:

- Make sure you have `make` installed (e.g. with `sudo apt install make`
  for Debian based distributions)

- [Install docker with compose plugin](https://docs.docker.com/get-docker/)
  for your system

- [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
  for your system

- Install pre-commit with uv:

  ```bash
  uv tool install pre-commit --with pre-commit-uv
  ```

- Clone git repository, checkout branch `develop` and install pre-commit hooks:

  ```bash
  git clone https://github.com/base-angewandte/baseauth.git
  cd baseauth
  git checkout develop
  pre-commit install --install-hooks --overwrite
  ```

- Check and adapt settings (if you need more details than the comments on
  the single settings in the skeleton env file give you, take a look at the
  [](./configuration.md) section). You need to at least set the `POSTGRES_PASSWORD` and
  the `SITE_URL`:

  ```bash
  cp env-skel .env
  vi .env
  ```

- Create the docker compose override file:

  ```bash
  cp compose.override.dev.yaml compose.override.yaml
  ```

Now, depending on which path you want to go, take one of the following two
subsections.

### Everything inside docker

- Make sure that the `DOCKER` variable in `.env` is set to `TRUE`. Otherwise,
  Django will assume that postgres and redis are accessible on localhost ports.

- Start everything:

  ```bash
  make start-dev-docker
  ```

  If this is your first start, you will also need to apply the initial
  migrations (can be skipped, unless you reset your database):

  ```bash
  make init
  ```

  To stop all services again hit CTRL-C to stop following the logs and then use `make stop`.

### The full developer setup

- Create a virtual environment with `uv` and activate it:

  ```bash
  uv venv --python 3.12 --seed
  source .venv/bin/activate
  ```

- Install requirements in your virtualenv:

  ```bash
  uv pip sync src/requirements-dev.txt
  ```

- Check the _compose.override.yaml_ file you created before from the template
  and uncomment the port mounts for Redis and Postgres, so your local Django can access them.

- Start required services:

  ```bash
  make start-dev
  ```

- Run migrations:

  ```bash
  cd src
  python manage.py migrate
  ```

- Start development server:

  ```bash
  python manage.py runserver 8000
  ```

## Production

- Update package index:

  ```bash
  # RHEL
  sudo yum update

  # Debian
  sudo apt-get update
  ```

- [Install docker with compose plugin](https://docs.docker.com/get-docker/)
  for your system

- Change to user `base`

- Change to `/opt/base`

- Clone git repository:

  ```bash
  git clone https://github.com/base-angewandte/baseauth.git
  cd baseauth
  ```

- Check and adapt settings. Take the [](./configuration.md) section as a reference.
  You need to at least set the `POSTGRES_PASSWORD` and the `SITE_URL`:

  ```bash
  cp env-skel .env
  vi .env
  ```

- Use `Makefile` to initialize and run project:

  ```bash
  make start init restart-gunicorn
  ```

- Install nginx and configure it accordingly
