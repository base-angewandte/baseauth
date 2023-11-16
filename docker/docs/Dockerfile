FROM python:3.11

ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

WORKDIR /docs
VOLUME /docs
