FROM python:3.5-alpine
RUN apk add --update --no-cache \
    build-base \
    ca-certificates \
    curl

WORKDIR /app
COPY ./cua.py /app
COPY ./monitor.py /app
COPY ./requirements.txt /app
WORKDIR /app

RUN pip install -r requirements.txt
CMD exec python /app/monitor.py