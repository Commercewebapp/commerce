FROM python:3.8-alpine

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN apk add --no-cache jpeg-dev zlib-dev


# install dependencies
COPY ./requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apk del .tmp

COPY . .

# collect static files
RUN python manage.py collectstatic --noinput

# add and run as non-root user
RUN adduser -D myuser
USER myuser

# run gunicorn
CMD gunicorn commerce.wsgi --bind 0.0.0.0:$PORT
