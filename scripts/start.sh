#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

export FLASK_ENV=development
export FLASK_APP=webserver.py

export REDIS_URL=redis://localhost:6379/0
flask run --host=0.0.0.0
