# load the rejson image as an empty step so we can copy the necessary modules
# ref: https://hub.docker.com/r/redislabs/rejson/dockerfile
# or to the rejson.Dockerfile in this repository

FROM redislabs/rejson:latest as rejson
FROM python:3.11-slim

WORKDIR /usr/src/app

COPY . .

COPY --from=rejson "/usr/lib/redis/modules" ./modules

RUN apt update && \
    apt-get install redis build-essential libffi-dev supervisor -y \
    && pip install --no-cache-dir -r requirements.txt \
    && groupadd -g 999 supervisor \
    && useradd -r -u 999 -g supervisor supervisor \
    && mkdir -p /var/log/supervisord \
    && mkdir -p /run/supervisord \
    && chown -R supervisor:supervisor /var/log/supervisord \
    && chown -R supervisor:supervisor /run/supervisord
    

EXPOSE 8000

USER supervisor

CMD ["/usr/bin/supervisord", "-c", "./resources/docker/supervisord/supervisord.conf"]
