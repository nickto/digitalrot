FROM python:3.7.4-alpine

RUN apk update \
    && apk add ffmpeg \
    && apk add imagemagick \
    && apk add file

COPY . /app
WORKDIR /app

RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install .
RUN pytest

ENTRYPOINT ["./app.py"]
