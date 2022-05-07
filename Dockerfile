# syntax=docker/dockerfile:1
FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY pip_requirements.txt /code/
RUN pip install -r pip_requirements.txt
COPY . /code/