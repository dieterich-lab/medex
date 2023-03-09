#!/usr/bin/env bash

# enviroment variables
export FLASK_DEBUG=1
export FLASK_APP=webserver.py

export POSTGRES_USER=test
export POSTGRES_PASSWORD=test
export POSTGRES_DB=example
export POSTGRES_PORT=5429
export POSTGRES_HOST=localhost

# run flask
flask run
