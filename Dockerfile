FROM python:3.8-slim

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

EXPOSE 5429
EXPOSE 7000


CMD [ "waitress-serve","--threads","6","--port","7000","--call", "webserver:main" ]
