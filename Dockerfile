FROM python:3.7-slim

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

EXPOSE 5428
EXPOSE 700


CMD [ "waitress-serve","--port","700","--host","medex","--call", "webserver:main" ]
