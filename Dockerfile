FROM python:3.10-slim

WORKDIR /app
COPY Pipfile Pipfile.lock ./

RUN cd /app/ && \
    pip install --no-cache-dir pipenv && \
    pipenv install --ignore-pipfile --deploy --system --clear

COPY webserver.py alembic.ini /app/
COPY medex /app/medex/
COPY static /app/static/
COPY schema /app/schema/
COPY templates /app/templates/

ENV TZ=Europe/Berlin

EXPOSE 8000

CMD [ "waitress-serve", "--threads", "6", "--port", "8000", "--call", "webserver:main" ]
