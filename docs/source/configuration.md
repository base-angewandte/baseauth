# Configuration

The _baseauth_ backend is configured through one `.env` file in the project root folder.
There is a template `env-skel` file available in the same folder, to copy from and
then modify it. See also [](install.md) on when and how to set up those file.

Environment variables without a default value are required to be set.

## `.env`

### Database Settings

These settings are used to set up the DB in the portfolio-postgres container.

#### `POSTGRES_DB`

Name of the PostgreSQL database.

#### `POSTGRES_USER`

User of the PostgreSQL database.

#### `POSTGRES_PASSWORD`

Password for user of the PostgreSQL database.

Make sure to change this to a strong password on any production/public server.

#### `POSTGRES_PORT`

Default: `5432`

Port of the PostgreSQL database.

The database port only needs to be changed, if you are running Portfolio
locally in combination with e.g. Showroom also running locally. Then at
least one of the database container ports needs to be mapped to a different
value. So use whatever you set in your compose.override.yaml for
portfolio-postgres or use the default.

### Redis Settings

#### `REDIS_PORT`

Default: `6379`

Port of the Redis data store

Similar to `POSTGRES_PORT` you won't need to change this in most cases.
But if you develop locally and have several Redis instances for different
projects running at the same time, you might map some of them to alternate
ports. So whichever non-default port you set in your compose.override.yaml
for Redis, this should be also set here, unless you operate in a fully
containerised setup.

### DOCKER

For any online deployment the default (True) should be fine here, as usually all
services will be run inside docker containers. Only when you want to start the
Django application itself on your host machine (e.g. for local development), you have
to set this to False.

### SITE_URL & FORCE_SCRIPT_NAME

The `SITE_URL` has to be set to the base URL of the site _basauth_ is running on, which
will depend on whether you deploy this to some online node, either with multiple services
sharing one domain or running _baseauth_ on a separate domain, or if you run it locally.
For local development setups you can choose `http://127.0.0.1:8000/`. For an online
deployment choose the base path (protocol and domain), e.g. `https://base.uni-ak.ac.at/`.

Additionally, `FORCE_SCRIPT_NAME` (which defaults to `/auth`) will be used to
determine the actual PATH to your _baseauth_ instance, by prefixing it with the
`SITE_URL`. So for a local development setup (where Django is actually running on
127.0.0.1:8300) make sure to remove the comment and explicitly set this to an empty
string:

```
FORCE_SCRIPT_NAME=
```

Do the same if _baseauth_ runs on the root of a dedicated domain, and leave the
default if it runs on a shared domain where it runs on the _/auth_ path.

### BEHIND_PROXY

This defines whether your application is running behind a reverse proxy (e.g. nginx).
In most cases the default True will be fine here. But for local development you might
want to set this to False.

### DJANGO_ADMINS & DJANGO_SUPERUSERS

While `DJANGO_ADMINS` is only used to configure whom to send admin notifications,
`DJANGO_SUPERUSERS` tells Django which users to actually treat as administrators.
This is applied on every login, irrespective of which flags you set for single
users through the Django admin or by using the `createsuperuser` management command.
So if you create an admin user, make sure to add their username in this setting.
Otherwise, the user will automatically be demoted again.

### EMAIL\_\*

All settings in the block prefixed with `EMAIL_` are needed if you want to receive
e-Mail notifications from Django. While this is usually not necessary for local
development environments, it is highly advised for staging and production deployments.

### SESSION_COOKIE_DOMAIN

Usually you will use your baseauth server alongside some base applications. For the
relevant session cookies to work, we either need to run all applications on one
domain (in this case this setting can be left untouched), or we have to make sure
that the cookies provided by basauth to the client (the web browser) will be also
sent to the other base applications. For that you need to run the applications under
a common parent domain. In this case set this parameter to the common domain part.

E.g. if baseauth is running on baseauth.example.org and Portfolio is running on
portfolio.example.org, then set the SESSION_COOKIE_DOMAIN to example.org

For more background details:

- https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-SESSION_COOKIE_DOMAIN

### CORS\_\* & CSRF\_\*

For the frontend to work and being able to make authenticated requests on behalf
of the user you should minimally set `CORS_ALLOW_CREDENTIALS` to True. All other
settings should basically be fine by default, as long as your frontend runs on the
same domain as the backend. If you need frontends on different domains (e.g. for
testing and staging purposes) to be able to make those request, you should add them
to the `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` lists.

Also in a setup where the different apps do not share the same domain you will have
to adapt the CSRF_COOKIE_DOMAIN, analog to the SESSION_COOKIE_DOMAIN.

For more background details on these settings:

- https://docs.djangoproject.com/en/4.2/ref/csrf/
- https://pypi.org/project/django-cors-headers/

### Showroom connection

These settings are only required, if a _Showroom_ instance is active, and syncing of
user profiles & preferences to _Showroom_ is activated. In order to activate syncing,
set `SYNC_TO_SHOWROOM` to `True`. Additionally, the `SHOWROOM_API_KEY` has to be
set to a key that has to be generated with the
[`create-source-repository`](https://showroom-backend.readthedocs.io/en/latest/management_commands.html#create-source-repository)
command, when _Showroom_ is set up. This key then can be used for _Portfolio_ and _baseauth_
to push new and updated activities and entities.

The other values only have to be set, if we deviate from a default single-domain
setup:

- `SHOWROOM_BASE_URL`: points to the base URL of where Showroom is available and
  defaults to `showroom/` appended to whatever is set as the `SITE_URL`.
- `SHOWROOM_API_PATH`: defaults to `api/v1/` and should only be changed if a new
  API version comes out

### Authentication backends

_baseauth_ can either be used as a standalone system, using Django's user model,
or it can use different authentication backends and/or a combination of those.

To configure which backends are used set the `AUTHENTICATION_BACKENDS` directive.
By default, this will only use Django's user model. In most system you might want
to replace this or add other backends in front of it.

Currently available options are:

- `django` - the internal user model authentication backend of Django
- `ldap` - a generic LDAP-based authentication
- `cas` - redirect all auth to an upstream CAS server

While `cas` will overrule other authentication backends, generally you can combine
different backends, so they will be checked in order of listing. So if
you for example use:

```
AUTHENTICATION_BACKENDS=ldap,django
```

_baseauth_ will first check against the configured LDAP directory, and only if it
cannot authenticate the user against it, will also check the Django user model. If
you switch those two parameters, the Django model will be checked first and LDAP
will only be checked if Django user does not exist. Be aware, that most authentication
backends create an internal Django user upon authentication. So in most cases it will
be most reasonable to put `django` last in the list - or even leave it out, if you do
not need local accounts (e.g. for testing oder administration).

Depending on which authentication backends you configure, you will also have to
add specific configuration directives. These will be explained in the following
subsections.

#### LDAP

If `ldap` is used in the `AUTHENTICATION_BACKENDS`, you also have to set the following:

- `AUTH_LDAP_SERVER_URI` : the server URI (including the port) of the LDAP server.
  E.g.: ldaps://ldap.example.org:636
- `AUTH_LDAP_BIND_DN` : the distinguished name used to query the directory
- `AUTH_LDAP_BIND_PASSWORD` : the password of the above user/DN
- `AUTH_LDAP_USER_ATTR_MAP` : a dictionary mapping the Django's internal user attributes
  to the LDAP user attributes. Defaults to `first_name=givenName,last_name=sn,email=mail`.

Now depending on your setup you can use three different ways to query your users:

1. Use `AUTH_LDAP_USER_DN_TEMPLATE` to set a string template that describes any
   user’s distinguished name based on the username. This must contain the placeholder
   %(user)s. E.g.: `uid=%(user)s,ou=users,dc=example,dc=com`. If this directive is
   set, the other directives are not relevant.
2. Use `AUTH_LDAP_USER_SEARCH_BASE` and `AUTH_LDAP_USER_SEARCH_USER_TEMPLATE` to
   configure the LDAP query. The first is the distinguished name of the search base.
   E.g.: `ou=users,dc=example,dc=com`. The second one is the filter string for the
   user lookup. E.g. `(cn=%(user)s)`
3. Similar to the second method, you can use the `AUTH_LDAP_USER_SEARCH_USER_TEMPLATE`
   as the filter string for the user lookup, but provide several distinguished names
   that should be used as the search base. These you can set as a semicolon-separated
   list of distinguished names. E.g.:
   `ou=unit1,ou=users,dc=example,dc=com;ou=unit2,ou=users,dc=example,dc=com`
   This will only work, if `AUTH_LDAP_USER_SEARCH_BASE` is not set.

#### CAS

```{note}
This authentication backend will overrule all other backends you might have configured.
All login and logout routes will be redirected to the upstream CAS server.
```

If `cas` is used in the `AUTHENTICATION_BACKENDS`, you also have to set the following:

- `CAS_SERVER` has to point to an upstream CAS server, which all login and logout
  attempts will be redirected to.

All other `CAS_` settings are optional (for details see the
[django-cas-ng config docs](https://djangocas.dev/docs/4.0/configuration.html)):

- `CAS_VERSION` : specifies the version of the CAS protocol and defaults to `3`
- `CAS_REDIRECT_URL` : specifies the redirect to happen after successful login and
  defaults to `/`. This only affects logins directly on baseauth. Logins coming
  from one of the apps already have their redirect URL set.
- `CAS_VERIFY_SSL_CERTIFICATE` : defaults to `True` and should not be changed in any
  production context. For local testing you can disable the SSL certificate check
  (e.g. if case of a self-signed certificate).
- `CAS_RENAME_ATTRIBUTES` : a dictionary used to rename the (key of the) attributes
  that the upstream CAS server may return. Is empty by default, so no renaming happens.
  For example, if `CAS_RENAME_ATTRIBUTES=ln=last_name,fn=first_name` the `ln` attribute
  returned by the cas server will be renamed as `last_name` and `fn` to `first_name`.
