# Migration notes

In some cases, migration paths are not straight-forward and
cannot be resolved solely by Django's internal migration
mechanism. Therefore, you might have to take some additional
steps before or after a `make update`, in case you are
migrating from one of the versions listed below.

## Any checkout before May 2025

This involves any version up to git commit id
`47c1c81afe298a93025a6f0f4bacdd1b54261936` on 2024-07-29 16:28:18.

**Config file changes:**

We refactored the configuration to only use a single .env file. Also,
the docker compose file was brought up to its newest version. This
requires you to adapt your config file as follows:

- move all settings from the src/baseauth/.env file to .env
  and make sure that the `POSTGRES_*` variables are set with the
  values of your old `BASEAUTH_DB_*` variables (these can then be
  dropped altogether).
- if you are using a docker compose override file, move your old
  docker-compose.override.yml to compose.override.yaml and remove
  the first line with the version

**Database upgrade:**

As we switched from Django's internal user model to a custom
user model, we need to fake apply a migration, before any
further migration can continue.

Instead of the usual `make update` you need to do:

```bash
make git-update
make migrate-user-model
make update
```
