#!/usr/bin/env bash

pre-commit install &&
source local.env &&
docker-compose up -d &&
./manage.py runserver
