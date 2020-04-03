FROM python:stretch

ADD . /app

RUN apt-get update && \
    apt-get install swig -y && \
    cd /app/ && \
    pip install pipenv && \
    pipenv install --ignore-pipfile --deploy --system



WORKDIR /app

ENV FLASK_ENV docker
# not really needed as weitress ignores this option
ENV FLASK_APP webserver.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV TZ=Europe/Berlin



EXPOSE 5428
EXPOSE 80


CMD [  "python", "manage.py", "run", "--port", "80", "--call" ]
