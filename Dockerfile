FROM python:slim


COPY . /app
COPY Pipfile Pipfile.lock /app/

RUN apt-get update && \
    apt-get install -y && \
    cd /app/ && \
    pip install --no-cache-dir pipenv && \
    pipenv install --ignore-pipfile --deploy --system --clear


WORKDIR /app

ENV FLASK_ENV production
ENV TZ=Europe/Berlin

EXPOSE 5428
EXPOSE 80


CMD [ "waitress-serve","--port","80","--host","medex","--call", "webserver:main" ]
