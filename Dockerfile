FROM python:stretch

ADD . /app

RUN apt-get update && \
    apt-get install swig -y && \
    cd /app/ && \
    pip install pipenv && \
    pipenv install --ignore-pipfile --deploy --system



WORKDIR /app

ENV FLASK_ENV production
# not really needed as waitress ignores this option
ENV TZ=Europe/Berlin

EXPOSE 5428
EXPOSE 800


CMD [ "waitress-serve","--port","800","--call", "webserver:main"  ]
