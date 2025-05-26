FROM python:3.11 AS base

ENV TZ="Europe/Vienna"

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1
ENV UV_SYSTEM_PYTHON=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        flite \
        libldap2-dev \
        libsasl2-dev \
        ldap-utils \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /logs
VOLUME /logs

WORKDIR /django

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY requirements.txt .
RUN uv pip install -r requirements.txt

EXPOSE 8000


FROM base as dev

COPY requirements-dev.txt .
RUN uv pip install -r requirements-dev.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM base as prod

COPY . .

CMD ["rainbow-saddle", "--pid", "/var/run/django.pid", "--gunicorn-pidfile", "/var/run/gunicorn.pid", "gunicorn", "baseauth.wsgi", "-c", "/django/gunicorn-conf.py"]
