FROM python:3.9.13-alpine3.16

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DOCKER 1

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN set -ex \
    && apk add --no-cache geos gdal\
    && apk add --no-cache --virtual .build-deps postgresql-dev build-base zlib-dev jpeg-dev gcc musl-dev \
    && pip install --no-cache-dir --upgrade -r /app/requirements.txt\
    && apk del .build-deps

COPY . /app

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "caim.wsgi:application"]
