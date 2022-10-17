FROM python:3.10-slim

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN $GITHUB_TOKEN

ARG HYPERCORN_HOST
ENV HYPERCORN_HOST $HYPERCORN_HOST

ARG HYPERCORN_PORT
ENV HYPERCORN_PORT $HYPERCORN_PORT

ARG HYPERCORN_LOG_LEVEL
ENV HYPERCORN_LOG_LEVEL $HYPERCORN_LOG_LEVEL

WORKDIR /usr/src/app

COPY . .

RUN apt update && \
    apt-get install build-essential libffi-dev -y \
    && pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "./run.py" ]
