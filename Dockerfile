FROM python:3.10-slim

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN $GITHUB_TOKEN

WORKDIR /usr/src/app

COPY . .

RUN apt update && \
    apt-get install build-essential libffi-dev -y && \
    pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "./main.py" ]