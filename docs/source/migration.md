# Migration notes

In some cases, migration paths are not straight-forward and
cannot be resolved solely by Django's internal migration
mechanism. Therefore, you might have to take some additional
steps before or after a `make update`, in case you are
migrating from one of the versions listed below.

## Any checkout before May 2025

This involves any version up to git commit id
`47c1c81afe298a93025a6f0f4bacdd1b54261936` on 2024-07-29 16:28:18.

As we switched from Django's internal user model to a custom
user model, we need to fake apply a migration, before any
further migration can continue.

Instead of the usual `make update` you need to do:

```bash
make git-update
make migrate-user-model
make update
```
