#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

export FLASK_ENV=development
export FLASK_APP=webserver.py

export POSTGRES_USER=test
export POSTGRES_PASSWORD=test
export POSTGRES_DB=example
export POSTGRES_PORT=5428
export POSTGRES_HOST=localhost

export DATABASE_URL=postgresql://test:test@localhost:5428/example
flask run --host=0.0.0.0
