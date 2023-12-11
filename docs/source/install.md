# Installation guide

Before you set up either a production or development instance, make sure
to meet all the [](./requirements.md).

## Development

There are two supported ways to start the development server:

1. Start only the auxiliary servers (database and redis) in docker
   but start the django dev server locally in your virtual env. This
   is the preferred way if you actively develop this application.

2. Start everything inside docker containers. This is the "easy" way
   to start a dev server and fiddle around with it, hot reloading included.
   But you will not have the local pre-commit setup.

- Clone git repository and checkout branch `develop`:

  ```bash
  git clone https://github.com/base-angewandte/baseauth.git
  cd baseauth
  ```

- Check and adapt settings (if you need more details on the single settings,
  then the comments in the skeleton env files give you, take a look at the
  [](./configuration.md) section):

  ```bash
  # env
  cp env-skel .env
  vi .env

  # django env
  cp ./src/baseauth/env-skel ./src/baseauth/.env
  vi ./src/baseauth/.env
  ```

- Create the docker-compose override file:

  ```bash
  cp docker-compose.override.dev.yml docker-compose.override.yml
  ```

Now, depending on which path you want to go, take one of the following two
subsections.

### Everything inside docker

- Make sure that the `DOCKER` variable in `./src/baseauth/.env` is set to
  `TRUE`. Otherwise, django will assume that postgres and redis are accessible
  on localhost ports.

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

```{note}
Make sure to explicitly set the relevant `POSTGRES_*` variables in your
./src/baseauth/.env file, if you have changed any of the corresponding `CAS_DB_*`
parameters in your .env file. This is not necessary for dockerised setups, but in your
local django dev server those environment variables are not assigned
automagically. Take a look at the [](./configuration.md) section for details.
```

- Create your python environment with `pyenv` and activate it

  ```bash
  pyenv virtualenv 3.11 baseauth
  pyenc activate baseauth
  ```

- Install pip-tools and requirements in your virtualenv:

  ```bash
  pip install pip-tools
  pip-sync src/requirements-dev.txt
  ```

- Install pre-commit hooks:

  ```bash
  pre-commit install
  ```

- Check the _docker-compose.override.yml_ file you created before from the template
  and uncomment the port mounts for Redis and Postgres, so your local Django can access them.

- Start required services:

  ```bash
  make start-dev
  ```

- Run migration:

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

- Install docker and docker-compose

- Change to user `base`

- Change to `/opt/base`

- Clone git repository:

  ```bash
  git clone https://github.com/base-angewandte/baseauth.git
  cd baseauth
  ```

- Check and adapt settings:

  ```bash
  # env
  cp env-skel .env
  vi .env

  # django env
  cp ./src/baseauth/env-skel ./src/baseauth/.env
  vi ./src/baseauth/.env
  ```

- Use `Makefile` to initialize and run project:

  ```bash
  make start init restart-gunicorn
  ```

- Install nginx and configure it accordingly
