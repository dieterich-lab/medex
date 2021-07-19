FROM python:stretch

ADD . /app

RUN apt-get update && \
    apt-get install swig -y && \
    cd /app/ && \
    pip install pipenv && \
    pipenv install --ignore-pipfile --deploy --system



WORKDIR /app

ENV FLASK_ENV production
ENV TZ=Europe/Berlin

EXPOSE 5428
EXPOSE 5000


CMD [ "waitress-serve","--port","5000","--host","medex","--call", "webserver:main" ]
