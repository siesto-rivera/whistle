FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y default-libmysqlclient-dev gcc && apt-get clean

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /usr/src/app/

RUN pip install --upgrade pip && pip install -r requirements.txt
