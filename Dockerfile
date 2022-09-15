FROM python:3.10-slim

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN $GITHUB_TOKEN

ARG UVICORN_HOST
ENV UVICORN_HOST $UVICORN_HOST

ARG UVICORN_PORT
ENV UVICORN_PORT $UVICORN_PORT

ARG UVICORN_LOG_LEVEL
ENV UVICORN_LOG_LEVEL $UVICORN_LOG_LEVEL

WORKDIR /usr/src/app

COPY . .

RUN apt update && \
    apt-get install build-essential libffi-dev -y \
    && pip install --no-cache-dir -r requirements.txt

CMD [ "/bin/bash", "./run.sh" ]