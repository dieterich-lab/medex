FROM python:3.10-slim

WORKDIR /app
COPY Pipfile Pipfile.lock ./


RUN apt-get update && \
    apt-get install -y && \
    cd /app/ && \
    pip install --no-cache-dir pipenv && \
    pipenv install --ignore-pipfile --deploy --system --clear &&\
    rm -rf /var/lib/apt/lists/*



COPY . /app

ENV FLASK_ENV production
ENV TZ=Europe/Berlin

EXPOSE 800


CMD [ "waitress-serve", "--threads", "6", "--port", "800", "--call", "webserver:main" ]
