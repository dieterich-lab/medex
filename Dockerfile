FROM python:3.8-slim

ADD . /app

COPY Pipfile Pipfile.lock ./

RUN pip install --upgrade pip &&\
    apt-get update && \
    apt-get install -y && \
    cd /app/ && \
    pip install --no-cache-dir pipenv && \
    pipenv install --ignore-pipfile --deploy --system --clear &&\
    rm -rf /var/lib/apt/lists/*



WORKDIR /app

ENV FLASK_ENV production
ENV TZ=Europe/Berlin

EXPOSE 5428
EXPOSE 900


CMD [ "waitress-serve","--port","900","--call", "webserver:main"  ]
